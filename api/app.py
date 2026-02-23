"""
api/app.py
FastAPI entrypoint for the Enterprise AI Agent Engine.
"""

import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from uuid import uuid4

# Load .env into environment as early as possible
load_dotenv()

from fastapi import FastAPI, HTTPException, Header, Depends, Request, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
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


app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
def _enforce_api_key() -> bool:
    raw = os.getenv("ENFORCE_API_KEY", "false").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def verify_api_key(x_api_key: str = Header(None)):
    if not _enforce_api_key():
        return

    api_key = os.getenv("API_KEY", "supersecretkey")
    if x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    version: str = Field(default="1.0.0", min_length=1, max_length=20)
    description: str | None = Field(default=None, max_length=1000)


def _as_iso(ts):
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts.isoformat()
    return datetime.now(timezone.utc).isoformat()


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


@app.get("/api/agents")
async def list_agents(
    q: str | None = Query(default=None),
    _: None = Depends(verify_api_key),
):
    db = MongoDB.get_database()
    query = {}
    if q:
        query["name"] = {"$regex": q, "$options": "i"}

    cursor = db.agents.find(query).sort("created_at", -1)
    docs = await cursor.to_list(length=200)
    return [
        {
            "id": str(doc.get("_id")),
            "name": doc.get("name", ""),
            "version": doc.get("version", "1.0.0"),
            "description": doc.get("description"),
            "status": doc.get("status", "active"),
            "created_at": _as_iso(doc.get("created_at")),
        }
        for doc in docs
    ]


@app.post("/api/agents", status_code=201)
async def create_agent(
    payload: AgentCreateRequest,
    _: None = Depends(verify_api_key),
):
    db = MongoDB.get_database()
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Agent name is required")

    duplicate = await db.agents.find_one({"name_lower": name.lower()})
    if duplicate:
        raise HTTPException(status_code=409, detail="Agent with this name already exists")

    doc = {
        "_id": str(uuid4()),
        "name": name,
        "name_lower": name.lower(),
        "version": payload.version.strip() or "1.0.0",
        "description": payload.description,
        "status": "active",
        "created_at": datetime.now(timezone.utc),
    }
    await db.agents.insert_one(doc)
    return {
        "id": doc["_id"],
        "name": doc["name"],
        "version": doc["version"],
        "description": doc["description"],
        "status": doc["status"],
        "created_at": _as_iso(doc["created_at"]),
    }


@app.get("/api/runs")
async def list_runs(
    q: str | None = Query(default=None),
    status: str = Query(default="all"),
    _: None = Depends(verify_api_key),
):
    db = MongoDB.get_database()
    traces = await db.traces.find({}).sort("timestamp", -1).to_list(length=500)

    runs = []
    for trace in traces:
        if not trace.get("request_id"):
            continue

        run_status = "completed" if trace.get("final_answer") else "failed"
        run = {
            "id": trace.get("request_id"),
            "agent_id": trace.get("agent_id") or trace.get("session_id") or "default",
            "status": run_status,
            "started_at": _as_iso(trace.get("timestamp")),
            "completed_at": _as_iso(trace.get("timestamp")),
            "result": trace.get("final_answer") if isinstance(trace.get("final_answer"), str) else None,
        }
        runs.append(run)

    if status and status != "all":
        runs = [run for run in runs if run["status"] == status]

    if q:
        needle = q.lower().strip()
        runs = [
            run for run in runs
            if needle in str(run.get("id", "")).lower()
            or needle in str(run.get("agent_id", "")).lower()
        ]

    return runs


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
