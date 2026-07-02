"""
tests/test_auth.py
Unit and integration tests for the JWT/SMTP authentication refactor.
Verifies registration, login, token refresh, OTP flow, role enforcement,
and configuration settings integration.
"""

import pytest
from datetime import datetime, timezone, timedelta
from app.config.settings import settings


def test_settings_integration():
    """Verify that settings variables are properly defined and match expected values from .env/defaults."""
    assert settings.JWT_SECRET is not None
    assert settings.JWT_ALGORITHM in ("HS256", "RS256")
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS > 0
    assert settings.OTP_EXPIRY_MINUTES > 0
    assert settings.OTP_RESEND_COOLDOWN_SECONDS >= 0
    assert settings.SMTP_HOST is not None
    assert settings.SMTP_PORT in (587, 465, 25)


@pytest.mark.asyncio
async def test_register_flow(client, fake_db):
    """Test successful user registration and duplicate prevention."""
    payload = {
        "email": "newuser@example.com",
        "password": "Password123!",
        "name": "New User"
    }
    
    # 1. Successful registration
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert "access_token" in res_data
    assert "refresh_token" in res_data
    assert res_data["user"]["email"] == "newuser@example.com"
    assert res_data["user"]["role"] == "developer"
    
    # 2. Prevent duplicate registration
    dup_response = client.post("/api/auth/register", json=payload)
    assert dup_response.status_code == 409
    assert "already registered" in dup_response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_flow(client, seed_user):
    """Test login with valid, invalid, and legacy credentials."""
    # Seed user details
    seed_user(email="testlogin@example.com", password="Password123!", role="developer")
    
    # 1. Login with correct credentials
    response = client.post("/api/auth/login", json={
        "email": "testlogin@example.com",
        "password": "Password123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "testlogin@example.com"
    
    # 2. Login with incorrect password
    bad_password_response = client.post("/api/auth/login", json={
        "email": "testlogin@example.com",
        "password": "WrongPassword!"
    })
    assert bad_password_response.status_code == 401
    
    # 3. Login with legacy hash migration
    seed_user(email="legacy@example.com", password="LegacyPassword123!", role="developer", legacy=True)
    legacy_response = client.post("/api/auth/login", json={
        "email": "legacy@example.com",
        "password": "LegacyPassword123!"
    })
    assert legacy_response.status_code == 200
    legacy_data = legacy_response.json()
    assert "access_token" in legacy_data
    
    # Verify legacy user hash got updated to scrypt
    from app.memory.database import MongoDB
    db = MongoDB.get_database()
    updated_user = await db.users.find_one({"email": "legacy@example.com"})
    assert updated_user is not None
    assert updated_user["password_hash"].startswith("scrypt$")


@pytest.mark.asyncio
async def test_refresh_token_flow(client, seed_user):
    """Test token refresh flow."""
    seed_user(email="refresh@example.com", password="Password123!", role="developer")
    
    # Login to get refresh token
    login_res = client.post("/api/auth/login", json={
        "email": "refresh@example.com",
        "password": "Password123!"
    })
    refresh_token = login_res.json()["refresh_token"]
    
    # 1. Refresh with valid token
    refresh_res = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    data = refresh_res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    
    # 2. Refresh with invalid/expired token
    invalid_res = client.post("/api/auth/refresh", json={"refresh_token": "invalid_refresh_token_string"})
    assert invalid_res.status_code == 401


@pytest.mark.asyncio
async def test_get_me_flow(client, seed_user):
    """Test endpoint retrieving current user information /me."""
    seed_user(email="me@example.com", password="Password123!", role="developer")
    
    # Login to get token
    login_res = client.post("/api/auth/login", json={
        "email": "me@example.com",
        "password": "Password123!"
    })
    access_token = login_res.json()["access_token"]
    
    # 1. Request /me with valid Authorization header
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "me@example.com"
    assert me_data["role"] == "developer"
    
    # 2. Request /me without Authorization header
    no_auth_res = client.get("/api/auth/me")
    assert no_auth_res.status_code == 401


@pytest.mark.asyncio
async def test_otp_reset_password_flow(client, seed_user, fake_db):
    """Test full forgot password OTP and password reset flow (utilizes dev echo)."""
    seed_user(email="otpuser@example.com", password="OldPassword123!", role="developer")
    
    # 1. Request OTP (Dev mode: OTP is returned in payload)
    otp_req = client.post("/api/auth/request-otp", json={"email": "otpuser@example.com"})
    assert otp_req.status_code == 200
    otp_data = otp_req.json()
    assert "dev_otp" in otp_data
    dev_otp = otp_data["dev_otp"]
    
    # 2. Verify OTP code (Returns reset_token)
    verify_req = client.post("/api/auth/verify-otp", json={
        "email": "otpuser@example.com",
        "otp": dev_otp
    })
    assert verify_req.status_code == 200
    verify_data = verify_req.json()
    assert "reset_token" in verify_data
    reset_token = verify_data["reset_token"]
    
    # 3. Reset password using reset token
    reset_req = client.post("/api/auth/reset-password", json={
        "reset_token": reset_token,
        "new_password": "NewPassword123!"
    })
    assert reset_req.status_code == 200
    
    # 4. Verify login using new password
    login_res = client.post("/api/auth/login", json={
        "email": "otpuser@example.com",
        "password": "NewPassword123!"
    })
    assert login_res.status_code == 200


@pytest.mark.asyncio
async def test_rbac_routes(client, seed_user):
    """Verify role-based access control checks."""
    # Seed users with different roles
    dev_user = seed_user(email="rbac_dev@example.com", password="Password123!", role="developer")
    admin_user = seed_user(email="rbac_admin@example.com", password="Password123!", role="admin")
    
    # Helper to get headers
    def get_headers(email):
        res = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
        return {"Authorization": f"Bearer {res.json()['access_token']}"}
        
    dev_headers = get_headers("rbac_dev@example.com")
    admin_headers = get_headers("rbac_admin@example.com")
    
    # 1. Admin accesses admin route (success)
    admin_res = client.get("/api/auth/api/admin/users", headers=admin_headers)
    assert admin_res.status_code == 200
    
    # 2. Developer accesses admin route (error 403)
    dev_res = client.get("/api/auth/api/admin/users", headers=dev_headers)
    assert dev_res.status_code == 403
