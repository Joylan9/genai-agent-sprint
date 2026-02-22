"""
api/app.py
FastAPI entrypoint for the Enterprise AI Agent Engine.
"""

import os
from dotenv import load_dotenv

# Load .env into environment as early as possible
load_dotenv()

from fastapi import FastAPI, HTTPException, Header, Depends, Request, Response
from fastapi.responses import JSONResponse
from api.schemas import AgentRequest, AgentResponse
from api.dependencies import build_agent
from app.infra.validators import InputValidator
from app.memory.database import MongoDB
from app.infra.logger import metrics_response
from app.infra.ollama_client import get_ollama_client, get_ollama_model
import redis

app = FastAPI(
    title="Enterprise AI Agent Engine",
    version="1.0.0",
    description="Production-ready AI agent with routing, reliability, and hybrid search."
)

# ============================================================
# MONGODB STARTUP INITIALIZATION
# Build agent after DB + env are ready (so env/HF_TOKEN is loaded)
# ============================================================
agent = None  # will be set in startup_event

@app.on_event("startup")
async def startup_event():
    global agent

    # ---------- Dependency Gate 1: MongoDB ----------
    try:
        MongoDB.connect()
        await MongoDB.initialize_indexes()
        db = MongoDB.get_database()
        await db.command("ping")
        print("✅ MongoDB connected and indexes ensured.")
    except Exception as e:
        print(f"❌ MongoDB startup check FAILED: {e}")
        raise RuntimeError(f"MongoDB not available: {e}") from e

    # ---------- Dependency Gate 2: Ollama ----------
    try:
        client = get_ollama_client()
        models = client.list()
        model_names = [m.model for m in models.models]
        expected_model = get_ollama_model()
        print(f"✅ Ollama connected. Models: {model_names}")
        if expected_model not in model_names:
            print(f"⚠️  Expected model '{expected_model}' not found in {model_names}")
    except Exception as e:
        print(f"❌ Ollama startup check FAILED: {e}")
        raise RuntimeError(f"Ollama not available: {e}") from e

    # ---------- Dependency Gate 3: Redis (Celery broker) ----------
    try:
        redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
        r = redis.from_url(redis_url, socket_connect_timeout=5)
        r.ping()
        print("✅ Redis connected.")
    except Exception as e:
        # Redis is non-critical for core API — warn but don't block startup
        print(f"⚠️  Redis not available (Celery may not work): {e}")

    # Build agent once at startup after env and DB are ready
    agent = build_agent()
    print("✅ Agent built and ready.")


# Load API key from environment (now that load_dotenv ran)
API_KEY = os.getenv("API_KEY", "supersecretkey")

# Maximum allowed request size (currently 1KB for testing)
MAX_REQUEST_SIZE = 1000
# MAX_REQUEST_SIZE = 1 * 1024 * 1024  # 1MB for production


# ============================================================
# REQUEST SIZE MIDDLEWARE
# ============================================================
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    body = await request.body()
    body_size = len(body)

    print(f"[DEBUG] Incoming request size: {body_size} bytes")

    if body_size > MAX_REQUEST_SIZE:
        print("[DEBUG] Request blocked due to size limit.")
        return JSONResponse(
            status_code=413,
            content={"detail": "Request size exceeds allowed limit."},
        )

    async def receive():
        return {"type": "http.request", "body": body}

    request._receive = receive

    return await call_next(request)


# ============================================================
# API KEY DEPENDENCY
# ============================================================
def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "model": get_ollama_model(),
    }


# ----------------------------
# Prometheus metrics endpoint
# ----------------------------
@app.get("/metrics")
async def metrics():
    data, content_type = metrics_response()
    return Response(content=data, media_type=content_type)


# ----------------------------
# Readiness endpoint (deep check)
# ----------------------------
@app.get("/ready")
async def readiness():
    checks = {}

    # MongoDB
    try:
        await MongoDB.get_database().command("ping")
        checks["mongodb"] = "ready"
    except Exception:
        checks["mongodb"] = "unavailable"

    # Ollama
    try:
        get_ollama_client().list()
        checks["ollama"] = "ready"
    except Exception:
        checks["ollama"] = "unavailable"

    # Redis
    try:
        redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
        r = redis.from_url(redis_url, socket_connect_timeout=3)
        r.ping()
        checks["redis"] = "ready"
    except Exception:
        checks["redis"] = "unavailable"

    all_ready = all(v == "ready" for v in checks.values())
    status_code = 200 if all_ready else 503

    return JSONResponse(
        content={"status": "ready" if all_ready else "degraded", "checks": checks},
        status_code=status_code,
    )


# ----------------------------
# TRACE DEBUG ENDPOINT
# ----------------------------
@app.get("/traces/{request_id}")
async def get_trace(
    request_id: str,
    _: None = Depends(verify_api_key),
):
    db = MongoDB.get_database()

    trace = await db.traces.find_one({"request_id": request_id})

    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")

    # Convert ObjectId to string for JSON serialization
    trace["_id"] = str(trace["_id"])

    return trace


@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(
    request: AgentRequest,
    _: None = Depends(verify_api_key),
):
    try:
        # Input validation
        try:
            validated_goal = InputValidator.validate_goal(request.goal)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        plan = await agent.create_plan(validated_goal)

        execution_output = await agent.execute_plan(
            request.session_id,
            validated_goal,
            plan
        )

        return AgentResponse(
            result=execution_output["result"],
            request_id=execution_output["request_id"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))