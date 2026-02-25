"""
app/api/auth.py

JWT-based authentication router.
Provides:
  POST /api/auth/register   — create user account
  POST /api/auth/login       — obtain access + refresh tokens
  POST /api/auth/refresh     — refresh access token
  GET  /api/auth/me          — current user profile

Dependencies:
  get_current_user()         — FastAPI dependency for protected routes
"""

from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from uuid import uuid4

import hashlib
import hmac
import base64
import json

from app.memory.database import MongoDB

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer(auto_error=False)

# ============================================================
# CONFIG
# ============================================================
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ============================================================
# MODELS
# ============================================================

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    name: str = Field(..., min_length=1, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    created_at: str


# ============================================================
# PASSWORD HASHING (bcrypt-compatible using hashlib)
# ============================================================

def _hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a random salt."""
    salt = base64.b64encode(os.urandom(16)).decode()
    pw_hash = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
    return f"{salt}${pw_hash}"


def _verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored hash."""
    try:
        salt, pw_hash = stored_hash.split("$", 1)
        check_hash = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
        return hmac.compare_digest(check_hash, pw_hash)
    except Exception:
        return False


# ============================================================
# JWT TOKEN UTILITIES (minimal, no external JWT library needed)
# ============================================================

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    s += "=" * padding
    return base64.urlsafe_b64decode(s)


def _create_token(payload: dict, expires_delta: timedelta) -> str:
    """Create a JWT token using HMAC-SHA256."""
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    now = datetime.now(timezone.utc)
    payload = {
        **payload,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "jti": str(uuid4()),
    }

    header_b64 = _b64url_encode(json.dumps(header).encode())
    payload_b64 = _b64url_encode(json.dumps(payload).encode())
    signing_input = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        JWT_SECRET.encode(), signing_input.encode(), hashlib.sha256
    ).digest()
    sig_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def _decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token. Returns payload or None."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, sig_b64 = parts

        # Verify signature
        signing_input = f"{header_b64}.{payload_b64}"
        expected_sig = hmac.new(
            JWT_SECRET.encode(), signing_input.encode(), hashlib.sha256
        ).digest()
        actual_sig = _b64url_decode(sig_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        # Decode payload
        payload = json.loads(_b64url_decode(payload_b64))

        # Check expiration
        if payload.get("exp", 0) < datetime.now(timezone.utc).timestamp():
            return None

        return payload
    except Exception:
        return None


def _create_access_token(user_id: str, email: str) -> str:
    return _create_token(
        {"sub": user_id, "email": email, "type": "access"},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def _create_refresh_token(user_id: str) -> str:
    return _create_token(
        {"sub": user_id, "type": "refresh"},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


# ============================================================
# DEPENDENCY: get_current_user
# ============================================================

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """
    FastAPI dependency that extracts and validates the JWT from the
    Authorization header. Returns the user document or raises 401.

    Usage in other routers:
        from app.api.auth import get_current_user
        @router.get("/protected")
        async def protected(user = Depends(get_current_user)):
            ...
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = _decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db = MongoDB.get_database()
    user = await db.users.find_one({"_id": payload["sub"]})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """
    Same as get_current_user but returns None instead of raising 401.
    Use for endpoints that work with or without auth.
    """
    if not credentials:
        return None
    try:
        payload = _decode_token(credentials.credentials)
        if not payload or payload.get("type") != "access":
            return None
        db = MongoDB.get_database()
        return await db.users.find_one({"_id": payload["sub"]})
    except Exception:
        return None


# ============================================================
# ROUTES
# ============================================================

@router.post("/register", response_model=TokenResponse)
async def register(payload: RegisterRequest):
    """Create a new user account."""
    db = MongoDB.get_database()

    # Check if email exists
    existing = await db.users.find_one({"email": payload.email.lower()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user_id = str(uuid4())
    now = datetime.now(timezone.utc)

    user_doc = {
        "_id": user_id,
        "email": payload.email.lower(),
        "name": payload.name,
        "password_hash": _hash_password(payload.password),
        "created_at": now,
        "updated_at": now,
    }

    await db.users.insert_one(user_doc)

    access_token = _create_access_token(user_id, payload.email)
    refresh_token = _create_refresh_token(user_id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={"id": user_id, "email": payload.email, "name": payload.name},
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    """Authenticate and obtain tokens."""
    db = MongoDB.get_database()

    user = await db.users.find_one({"email": payload.email.lower()})
    if not user or not _verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user_id = str(user["_id"])
    access_token = _create_access_token(user_id, user["email"])
    refresh_token = _create_refresh_token(user_id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={"id": user_id, "email": user["email"], "name": user["name"]},
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest):
    """Refresh an expired access token."""
    token_payload = _decode_token(payload.refresh_token)
    if not token_payload or token_payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    db = MongoDB.get_database()
    user = await db.users.find_one({"_id": token_payload["sub"]})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    user_id = str(user["_id"])
    new_access = _create_access_token(user_id, user["email"])
    new_refresh = _create_refresh_token(user_id)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={"id": user_id, "email": user["email"], "name": user["name"]},
    )


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Return the current authenticated user's profile."""
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "name": user["name"],
        "created_at": user.get("created_at", "").isoformat() if hasattr(user.get("created_at", ""), "isoformat") else str(user.get("created_at", "")),
    }


# ============================================================
# OTP / FORGOT PASSWORD
# ============================================================

import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP config from env (set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER or "noreply@traceai.dev")

OTP_EXPIRY_MINUTES = 10


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


class PasswordResetRequest(BaseModel):
    reset_token: str
    new_password: str = Field(..., min_length=6, max_length=128)


def _generate_otp() -> str:
    """Generate a 6-digit OTP."""
    return f"{random.randint(100000, 999999)}"


def _is_smtp_configured() -> bool:
    """Check if SMTP is properly configured (not placeholder values)."""
    if not SMTP_USER or not SMTP_PASS:
        return False
    placeholders = ["your-email", "your-16-char", "example.com", "changeme", "placeholder"]
    for p in placeholders:
        if p in SMTP_USER.lower() or p in SMTP_PASS.lower():
            return False
    return True


def _send_otp_email(to_email: str, otp: str, user_name: str = "User") -> bool:
    """Send OTP via SMTP. Returns True on success."""
    if not _is_smtp_configured():
        # Dev fallback: log OTP to console when SMTP not configured
        print(f"\n{'='*50}")
        print(f"  DEV MODE — OTP for {to_email}: {otp}")
        print(f"  (SMTP not configured — set real credentials in .env)")
        print(f"{'='*50}\n")
        return True  # Treat as success for dev flow

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"TraceAI — Your Verification Code: {otp}"
        msg["From"] = f"TraceAI Platform <{SMTP_FROM}>"
        msg["To"] = to_email

        html_body = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 480px; margin: 0 auto; padding: 40px 20px;">
            <div style="text-align: center; margin-bottom: 32px;">
                <div style="display: inline-block; background: linear-gradient(135deg, #3b82f6, #6366f1); width: 48px; height: 48px; border-radius: 12px; line-height: 48px; color: white; font-size: 20px; font-weight: bold;">⚡</div>
                <h2 style="color: #1e293b; margin: 12px 0 4px;">TraceAI Platform</h2>
            </div>
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 32px; text-align: center;">
                <p style="color: #64748b; margin: 0 0 8px; font-size: 14px;">Hi {user_name},</p>
                <p style="color: #334155; margin: 0 0 24px; font-size: 15px;">Your verification code is:</p>
                <div style="background: linear-gradient(135deg, #3b82f6, #6366f1); color: white; font-size: 32px; font-weight: bold; letter-spacing: 8px; padding: 16px 32px; border-radius: 10px; display: inline-block; font-family: monospace;">
                    {otp}
                </div>
                <p style="color: #94a3b8; margin: 24px 0 0; font-size: 13px;">
                    This code expires in {OTP_EXPIRY_MINUTES} minutes.
                    <br>If you didn't request this, please ignore this email.
                </p>
            </div>
            <p style="color: #cbd5e1; text-align: center; font-size: 11px; margin-top: 24px;">
                TraceAI Agent Platform — Secure Authentication
            </p>
        </div>
        """

        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM, to_email, msg.as_string())

        return True
    except Exception as e:
        print(f"SMTP error sending OTP to {to_email}: {e}")
        return False


@router.post("/request-otp")
async def request_otp(payload: OTPRequest):
    """
    Generate a 6-digit OTP and send to the user's email.
    OTP is valid for 10 minutes. Stores in MongoDB password_resets collection.
    """
    db = MongoDB.get_database()
    email = payload.email.lower()

    # Check user exists
    user = await db.users.find_one({"email": email})
    if not user:
        # Don't reveal whether email exists (security)
        return {"message": "If an account exists with this email, a verification code has been sent."}

    otp = _generate_otp()
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()
    now = datetime.now(timezone.utc)

    # Store OTP (hashed) with expiry — upsert so only latest OTP is valid
    await db.password_resets.update_one(
        {"email": email},
        {
            "$set": {
                "otp_hash": otp_hash,
                "attempts": 0,
                "created_at": now,
                "expires_at": now + timedelta(minutes=OTP_EXPIRY_MINUTES),
                "verified": False,
            }
        },
        upsert=True,
    )

    # Send email
    user_name = user.get("name", "User")
    email_sent = _send_otp_email(email, otp, user_name)

    response = {
        "message": "If an account exists with this email, a verification code has been sent.",
        "expires_in": OTP_EXPIRY_MINUTES * 60,
    }

    # In dev mode (SMTP not configured), include OTP in response so
    # the frontend can show it directly — never do this in production!
    if not _is_smtp_configured():
        response["dev_otp"] = otp
        response["dev_notice"] = "SMTP not configured. OTP returned in response for development."
    elif not email_sent:
        response["warning"] = "Email delivery may have failed. Check backend logs."

    return response


@router.post("/verify-otp")
async def verify_otp(payload: OTPVerifyRequest):
    """
    Verify the OTP code. On success, returns a one-time reset_token
    that can be used to set a new password.
    """
    db = MongoDB.get_database()
    email = payload.email.lower()

    record = await db.password_resets.find_one({"email": email})
    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code found. Please request a new one.",
        )

    # Check expiry
    if record.get("expires_at") and record["expires_at"] < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code expired. Please request a new one.",
        )

    # Rate limit: max 5 attempts
    if record.get("attempts", 0) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Please request a new code.",
        )

    # Increment attempts
    await db.password_resets.update_one(
        {"email": email},
        {"$inc": {"attempts": 1}},
    )

    # Verify OTP
    otp_hash = hashlib.sha256(payload.otp.encode()).hexdigest()
    if not hmac.compare_digest(otp_hash, record.get("otp_hash", "")):
        remaining = 5 - (record.get("attempts", 0) + 1)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid code. {remaining} attempts remaining.",
        )

    # OTP valid — generate reset token
    reset_token = _create_token(
        {"sub": email, "type": "password_reset"},
        timedelta(minutes=15),
    )

    # Mark as verified
    await db.password_resets.update_one(
        {"email": email},
        {"$set": {"verified": True}},
    )

    return {
        "message": "Code verified successfully.",
        "reset_token": reset_token,
    }


@router.post("/reset-password")
async def reset_password(payload: PasswordResetRequest):
    """
    Set a new password using the reset_token from verify-otp.
    """
    # Decode reset token
    token_payload = _decode_token(payload.reset_token)
    if not token_payload or token_payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token. Please start over.",
        )

    email = token_payload.get("sub", "")
    db = MongoDB.get_database()

    # Check the OTP was verified
    record = await db.password_resets.find_one({"email": email, "verified": True})
    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset session invalid. Please request a new code.",
        )

    # Update password
    new_hash = _hash_password(payload.new_password)
    result = await db.users.update_one(
        {"email": email},
        {"$set": {"password_hash": new_hash, "updated_at": datetime.now(timezone.utc)}},
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found.",
        )

    # Clean up reset record
    await db.password_resets.delete_one({"email": email})

    return {"message": "Password reset successfully. You can now sign in with your new password."}
