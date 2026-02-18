"""
Health endpoint checks basic connectivity.
"""

from fastapi import APIRouter
from ..memory.database import MongoDB
from ollama import list as ollama_list

router = APIRouter()

@router.get("/health")
async def health():
    try:
        db = MongoDB.get_database()
        await db.command("ping")

        ollama_list()

        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
