"""
Health endpoint checks basic connectivity.
"""

import os

from fastapi import APIRouter
from ..infra.ollama_client import get_ollama_model
from app.config.runtime import feature_flags_payload

router = APIRouter()

@router.get("/health")
async def health():
    return {
        "status": "ok",
        "model": get_ollama_model(),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "features": feature_flags_payload(),
    }
