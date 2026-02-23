"""
app/api_app.py

FastAPI application entry point for the GenAI Agent Platform.
Gunicorn loads this as: app.api_app:app
"""

import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api.agent import router as agent_router
from app.api.platform import router as platform_router
from app.infra.logger import REQUEST_COUNTER, REQUEST_LATENCY
from app.memory.database import MongoDB
from app.observability.health import router as health_router
from app.observability.readiness import router as readiness_router
import app.tools.rag_search_tool
import app.tools.web_search_tool
import app.tools.tools


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup and shutdown lifecycle."""
    critical_vars = ["API_KEY", "SERPAPI_KEY", "HF_TOKEN", "MONGO_URI", "OLLAMA_HOST"]
    missing = [name for name in critical_vars if not os.getenv(name) or os.getenv(name).startswith("__")]
    if missing:
        raise RuntimeError(f"CRITICAL ENVIRONMENT VARIABLES MISSING: {', '.join(missing)}")

    MongoDB.connect()
    await MongoDB.initialize_indexes()
    yield


def _allowed_origins() -> list[str]:
    configured = os.getenv("CORS_ORIGINS", "").strip()
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]


app = FastAPI(
    title="GenAI Agent Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def prometheus_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    REQUEST_COUNTER.inc()
    REQUEST_LATENCY.observe(duration)
    return response


app.include_router(health_router)
app.include_router(readiness_router)
app.include_router(agent_router)
app.include_router(platform_router)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/")
async def root():
    return {"service": "GenAI Agent Platform", "status": "running"}
