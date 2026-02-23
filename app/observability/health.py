"""
Health endpoint checks basic connectivity.
"""

import os

from fastapi import APIRouter
from ..memory.database import MongoDB
from ollama import list as ollama_list
from ..infra.ollama_client import get_ollama_model

router = APIRouter()

@router.get("/health")
async def health():
    try:
        db = MongoDB.get_database()
        await db.command("ping")

        ollama_list()

        return {
            "status": "ok",
            "model": get_ollama_model(),
            "version": os.getenv("APP_VERSION", "1.0.0"),
        }
    except Exception as e:
        return {
            "status": "degraded",
            "model": get_ollama_model(),
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "error": str(e),
        }
