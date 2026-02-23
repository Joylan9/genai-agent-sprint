"""
Readiness endpoint checks system readiness.
"""

from fastapi import APIRouter
from ..memory.database import MongoDB

router = APIRouter()

@router.get("/ready")
async def ready():
    status = "ready"
    checks = {"mongodb": "unavailable"}
    try:
        db = MongoDB.get_database()
        await db.command("ping")
        checks["mongodb"] = "ready"
    except Exception:
        status = "degraded"
        
    return {"status": status, "checks": checks}
