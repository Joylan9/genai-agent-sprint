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


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup / shutdown lifecycle."""
    # --- Startup ---
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

# Register routers
app.include_router(health_router)
app.include_router(readiness_router)

# Mount Prometheus /metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/")
async def root():
    return {"service": "GenAI Agent Platform", "status": "running"}
