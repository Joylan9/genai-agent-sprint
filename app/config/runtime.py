from __future__ import annotations

import os
from typing import Literal

UserRole = Literal["admin", "developer", "viewer"]
ALLOWED_USER_ROLES: tuple[UserRole, ...] = ("admin", "developer", "viewer")


def env_flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def mongodb_uri() -> str:
    return (
        os.getenv("MONGODB_URI")
        or os.getenv("MONGO_URI")
        or "mongodb://localhost:27017"
    )


def mongodb_db() -> str:
    return os.getenv("MONGODB_DB", "agent_memory")


def web_search_available() -> bool:
    return bool(os.getenv("SERPAPI_KEY"))


def auth_dev_bypass_enabled() -> bool:
    return env_flag("AUTH_DEV_BYPASS_ENABLED", False)


def auth_dev_bypass_role() -> UserRole:
    raw = os.getenv("AUTH_DEV_BYPASS_ROLE", "admin").strip().lower()
    if raw in ALLOWED_USER_ROLES:
        return raw  # type: ignore[return-value]
    return "admin"


def dev_email_otp_echo_enabled() -> bool:
    return env_flag("DEV_EMAIL_OTP_ECHO_ENABLED", False)


def feature_flags_payload() -> dict[str, bool]:
    return {
        "authDevBypassEnabled": auth_dev_bypass_enabled(),
        "webSearchAvailable": web_search_available(),
        "devEmailOtpEchoEnabled": dev_email_otp_echo_enabled(),
    }
