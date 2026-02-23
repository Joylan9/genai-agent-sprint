"""
Readiness endpoint checks system readiness.
"""

from fastapi import APIRouter
from ..registry.tool_registry import ToolRegistry

router = APIRouter()

@router.get("/ready")
async def ready():
    return {"status": "ready"}
