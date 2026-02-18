"""
Readiness endpoint checks system readiness.
"""

from fastapi import APIRouter
from ..registry.tool_registry import ToolRegistry

router = APIRouter()

@router.get("/ready")
async def ready():
    try:
        registry = ToolRegistry()
        tools = registry.list_tools()

        if not tools:
            raise Exception("No tools loaded.")

        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}
