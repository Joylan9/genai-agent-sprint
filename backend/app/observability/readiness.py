"""
Readiness endpoint checks system readiness.
"""

import os

from fastapi import APIRouter
from fastapi.responses import JSONResponse
import redis

from app.config.runtime import feature_flags_payload, web_search_available
from app.infra.ollama_client import get_ollama_client
from ..memory.database import MongoDB

router = APIRouter()

def _check_payload(status: str, optional: bool, detail: str | None = None) -> dict[str, object]:
    payload: dict[str, object] = {"status": status, "optional": optional}
    if detail:
        payload["detail"] = detail
    return payload


@router.get("/ready")
async def ready():
    checks: dict[str, dict[str, object]] = {}

    try:
        db = MongoDB.get_database()
        await db.command("ping")
        checks["mongodb"] = _check_payload("ready", optional=False)
    except Exception as exc:
        checks["mongodb"] = _check_payload("unavailable", optional=False, detail=str(exc))

    try:
        get_ollama_client().list()
        checks["ollama"] = _check_payload("ready", optional=False)
    except Exception as exc:
        checks["ollama"] = _check_payload("unavailable", optional=False, detail=str(exc))

    try:
        redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
        client = redis.from_url(redis_url, socket_connect_timeout=3)
        client.ping()
        checks["redis"] = _check_payload("ready", optional=False)
        checks["celery"] = _check_payload("ready", optional=False)
    except Exception as exc:
        detail = str(exc)
        checks["redis"] = _check_payload("unavailable", optional=False, detail=detail)
        checks["celery"] = _check_payload("unavailable", optional=False, detail=detail)

    checks["web_search"] = _check_payload(
        "ready" if web_search_available() else "disabled",
        optional=True,
        detail=None if web_search_available() else "SERPAPI_KEY is not configured.",
    )

    blocking_failures = [
        name for name, result in checks.items()
        if not result["optional"] and result["status"] != "ready"
    ]

    payload = {
        "status": "ready" if not blocking_failures else "degraded",
        "checks": checks,
        "features": feature_flags_payload(),
    }
    return JSONResponse(content=payload, status_code=200 if not blocking_failures else 503)
