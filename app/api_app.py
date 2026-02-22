"""
app/api_app.py

FastAPI application entry point for the GenAI Agent Platform.
Gunicorn loads this as: app.api_app:app
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_client import make_asgi_app

from app.memory.database import MongoDB
from app.observability.health import router as health_router
from app.observability.readiness import router as readiness_router
from app.api.agent import router as agent_router
from app.infra.logger import REQUEST_COUNTER, REQUEST_LATENCY
import time
from fastapi import Request

import os

@asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup / shutdown lifecycle."""
    # --- Startup Dependency Gates ---
    critical_vars = ["API_KEY", "SERPAPI_KEY", "HF_TOKEN", "MONGO_URI", "OLLAMA_HOST"]
    missing = [v for v in critical_vars if not os.getenv(v) or os.getenv(v).startswith("__")]

    if missing:
        error_msg = f"❌ CRITICAL ENVIRONMENT VARIABLES MISSING: {', '.join(missing)}"
        print(error_msg)
        raise RuntimeError(error_msg)

    MongoDB.connect()
    await MongoDB.initialize_indexes()
    print("✅ MongoDB connected and indexes initialized")
    yield
    # --- Shutdown ---
    print("⏏️  Shutting down gracefully")


app = FastAPI(
    title="GenAI Agent Platform",
    version="1.0.0",
    lifespan=lifespan,
)

@app.middleware("http")
async def prometheus_metrics(request: Request, call_next):
    start_time = time.time()
    
    # Exclude metrics and health from counts if desired, but here we count all
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_COUNTER.inc()
    REQUEST_LATENCY.observe(duration)
    
    return response

# Register routers
app.include_router(health_router)
app.include_router(readiness_router)
app.include_router(agent_router)

# Mount Prometheus /metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/")
async def root():
    return {"service": "GenAI Agent Platform", "status": "running"}
