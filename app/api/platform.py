"""
app/api/platform.py

Supplemental API routes used by the frontend control plane:
- Agent catalog management
- Run history projection
- Trace lookup by request id
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from pymongo import DESCENDING

from app.memory.database import MongoDB

router = APIRouter(tags=["platform"])


def _enforce_api_key() -> bool:
    raw = os.getenv("ENFORCE_API_KEY", "false").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def verify_api_key(x_api_key: str | None = Header(None)):
    """
    Enforce API key for platform management endpoints.
    """
    if not _enforce_api_key():
        return

    api_key = os.getenv("API_KEY", "supersecretkey")
    if x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    version: str = Field(default="1.0.0", min_length=1, max_length=20)
    description: str | None = Field(default=None, max_length=1000)


def _as_iso(ts: Any) -> str:
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts.isoformat()
    return datetime.now(timezone.utc).isoformat()


def _to_agent_dto(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(doc.get("_id")),
        "name": doc.get("name", ""),
        "version": doc.get("version", "1.0.0"),
        "description": doc.get("description"),
        "status": doc.get("status", "active"),
        "created_at": _as_iso(doc.get("created_at")),
    }


def _to_run_dto(trace: dict[str, Any]) -> dict[str, Any]:
    # Prefer stored status (set by Celery tasks) over inferred status
    stored_status = trace.get("status")
    if stored_status in ("queued", "running", "completed", "failed"):
        status = stored_status
    else:
        # Fallback for traces created before Celery integration
        final_answer = trace.get("final_answer")
        status = "completed" if final_answer else "failed"

    return {
        "id": trace.get("request_id"),
        "agent_id": trace.get("agent_id") or trace.get("session_id") or "default",
        "status": status,
        "started_at": _as_iso(trace.get("started_at") or trace.get("timestamp")),
        "completed_at": _as_iso(trace.get("completed_at") or trace.get("timestamp")),
        "result": trace.get("final_answer") if isinstance(trace.get("final_answer"), str) else None,
        "cache_hit": trace.get("cache_hit", False),
        "latency_total": (trace.get("latency") or {}).get("total"),
        "goal": trace.get("goal"),
    }


@router.get("/api/agents")
async def list_agents(
    q: str | None = Query(default=None, description="Agent name search"),
    _: None = Depends(verify_api_key),
):
    db = MongoDB.get_database()
    query: dict[str, Any] = {}
    if q:
        query["name"] = {"$regex": q, "$options": "i"}

    cursor = db.agents.find(query).sort("created_at", DESCENDING)
    docs = await cursor.to_list(length=200)
    return [_to_agent_dto(doc) for doc in docs]


@router.post("/api/agents", status_code=201)
async def create_agent(
    payload: AgentCreateRequest,
    _: None = Depends(verify_api_key),
):
    db = MongoDB.get_database()
    normalized_name = payload.name.strip()
    if not normalized_name:
        raise HTTPException(status_code=400, detail="Agent name is required")

    duplicate = await db.agents.find_one({"name_lower": normalized_name.lower()})
    if duplicate:
        raise HTTPException(status_code=409, detail="Agent with this name already exists")

    doc = {
        "_id": str(uuid4()),
        "name": normalized_name,
        "name_lower": normalized_name.lower(),
        "version": payload.version.strip() or "1.0.0",
        "description": payload.description,
        "status": "active",
        "created_at": datetime.now(timezone.utc),
    }
    await db.agents.insert_one(doc)
    return _to_agent_dto(doc)


@router.patch("/api/agents/{agent_id}")
async def update_agent(
    agent_id: str,
    payload: dict,
    _: None = Depends(verify_api_key),
):
    db = MongoDB.get_database()
    update_data = {}
    if "name" in payload and isinstance(payload["name"], str):
        normalized_name = payload["name"].strip()
        update_data["name"] = normalized_name
        update_data["name_lower"] = normalized_name.lower()
    if "description" in payload:
        update_data["description"] = payload["description"]
    if "version" in payload:
        update_data["version"] = payload["version"]

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await db.agents.update_one(
        {"_id": agent_id},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    doc = await db.agents.find_one({"_id": agent_id})
    return _to_agent_dto(doc)


@router.get("/api/agents/{agent_id}")
async def get_agent(
    agent_id: str,
    _: None = Depends(verify_api_key),
):
    """Return a single agent by ID."""
    db = MongoDB.get_database()
    doc = await db.agents.find_one({"_id": agent_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Agent not found")
    return _to_agent_dto(doc)


@router.delete("/api/agents/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: str,
    _: None = Depends(verify_api_key),
):
    """Delete an agent from the catalog."""
    db = MongoDB.get_database()
    result = await db.agents.delete_one({"_id": agent_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")


@router.delete("/api/runs/{request_id}", status_code=204)
async def delete_run(
    request_id: str,
    _: None = Depends(verify_api_key),
):
    """Delete a run trace by request_id."""
    db = MongoDB.get_database()
    result = await db.traces.delete_one({"request_id": request_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Run not found")


@router.get("/api/runs")
async def list_runs(
    q: str | None = Query(default=None, description="Run id/session search"),
    status: Literal["all", "pending", "running", "completed", "failed"] = "all",
    _: None = Depends(verify_api_key),
):
    db = MongoDB.get_database()
    cursor = db.traces.find({}).sort("timestamp", DESCENDING)
    traces = await cursor.to_list(length=500)
    runs = [_to_run_dto(trace) for trace in traces if trace.get("request_id")]

    if status != "all":
        runs = [run for run in runs if run.get("status") == status]

    if q:
        needle = q.lower().strip()
        runs = [
            run
            for run in runs
            if needle in str(run.get("id", "")).lower()
            or needle in str(run.get("agent_id", "")).lower()
        ]

    return runs


@router.get("/traces/{request_id}")
async def get_trace(
    request_id: str,
    _: None = Depends(verify_api_key),
):
    db = MongoDB.get_database()
    trace = await db.traces.find_one({"request_id": request_id})
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")

    trace["_id"] = str(trace["_id"])
    if "timestamp" in trace:
        trace["timestamp"] = _as_iso(trace["timestamp"])
    return trace


# ============================================================
# ASYNC RUN SUBMISSION (Celery-backed)
# ============================================================

class RunSubmitRequest(BaseModel):
    session_id: str = Field(..., min_length=3, max_length=100)
    goal: str = Field(..., min_length=1, max_length=5000)


@router.post("/api/runs/submit", status_code=202)
async def submit_run(
    payload: RunSubmitRequest,
    _: None = Depends(verify_api_key),
):
    """
    Enqueue an agent execution as a background Celery task.
    Returns immediately with run_id; poll /api/runs/{id}/status for progress.
    """
    from app.tasks.agent_tasks import execute_agent_run

    db = MongoDB.get_database()
    run_id = str(uuid4())

    # Create trace document with status=queued
    await db.traces.insert_one({
        "request_id": run_id,
        "session_id": payload.session_id,
        "goal": payload.goal,
        "status": "queued",
        "plan": None,
        "steps": [],
        "observations": [],
        "final_answer": None,
        "cache_hit": False,
        "latency": {},
        "timestamp": datetime.now(timezone.utc),
    })

    # Enqueue Celery task
    execute_agent_run.delay(run_id, payload.session_id, payload.goal)

    return {
        "run_id": run_id,
        "status": "queued",
        "message": "Agent execution enqueued. Poll /api/runs/{run_id}/status for progress.",
    }


@router.get("/api/runs/{run_id}/status")
async def get_run_status(
    run_id: str,
    _: None = Depends(verify_api_key),
):
    """
    Poll the current status of an async run.
    Returns: status, result (if completed), error (if failed).
    """
    db = MongoDB.get_database()
    trace = await db.traces.find_one({"request_id": run_id})
    if not trace:
        raise HTTPException(status_code=404, detail="Run not found")

    status = trace.get("status", "unknown")
    response: dict[str, Any] = {
        "run_id": run_id,
        "status": status,
        "goal": trace.get("goal"),
        "started_at": _as_iso(trace.get("started_at") or trace.get("timestamp")),
    }

    if status == "completed":
        response["result"] = trace.get("final_answer")
        response["completed_at"] = _as_iso(trace.get("completed_at"))
        response["cache_hit"] = trace.get("cache_hit", False)
        latency = trace.get("latency") or {}
        response["latency_total"] = latency.get("total")
    elif status == "failed":
        response["error"] = trace.get("error")
        response["completed_at"] = _as_iso(trace.get("completed_at"))

    return response


@router.get("/api/feature-flags")
async def get_feature_flags():
    # Return empty dict, meaning all flags use their default fallback configurations
    return {}
