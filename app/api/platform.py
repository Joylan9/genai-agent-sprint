'''
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
'''

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from pymongo import DESCENDING

from app.api.auth import get_current_user, require_role
from app.config.runtime import feature_flags_payload
from app.memory.database import MongoDB

router = APIRouter(tags=["platform"])
ReadableRole = Depends(get_current_user)
DeveloperRole = Depends(require_role("developer", "admin"))
AdminRole = Depends(require_role("admin"))

RunStatus = Literal["queued", "running", "completed", "failed"]


class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    version: str = Field(default="1.0.0", min_length=1, max_length=20)
    description: str | None = Field(default=None, max_length=1000)
    status: str = Field(default="active", max_length=20)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    status: str | None = Field(default=None, max_length=20)
    metadata: dict[str, Any] | None = None


class AgentVersionCreateRequest(BaseModel):
    version: str = Field(..., min_length=1, max_length=20)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RunSubmitRequest(BaseModel):
    session_id: str = Field(..., min_length=3, max_length=100)
    goal: str = Field(..., min_length=1, max_length=5000)
    agent_id: str | None = Field(default=None, max_length=100)


def _as_iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    return str(value)


def _serialize(value: Any) -> Any:
    if isinstance(value, datetime):
        return _as_iso(value)
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    return value


def _normalize_run_status(status: str | None, trace: dict[str, Any]) -> RunStatus:
    normalized = (status or "").strip().lower()
    if normalized == "pending":
        normalized = "queued"
    if normalized in {"queued", "running", "completed", "failed"}:
        return normalized  # type: ignore[return-value]
    return "completed" if trace.get("final_answer") else "failed"


def _to_version_dto(version_doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent_id": version_doc.get("agent_id"),
        "version": version_doc.get("version"),
        "name": version_doc.get("name"),
        "description": version_doc.get("description"),
        "status": version_doc.get("status"),
        "metadata": version_doc.get("metadata", {}),
        "created_at": _as_iso(version_doc.get("created_at")),
        "snapshot": _serialize(version_doc.get("snapshot", {})),
    }


def _to_agent_dto(doc: dict[str, Any], versions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    current_version = doc.get("current_version") or doc.get("version") or "1.0.0"
    payload = {
        "id": str(doc.get("_id")),
        "name": doc.get("name", ""),
        "version": current_version,
        "current_version": current_version,
        "description": doc.get("description"),
        "status": doc.get("status", "active"),
        "metadata": doc.get("metadata", {}),
        "created_at": _as_iso(doc.get("created_at")),
        "updated_at": _as_iso(doc.get("updated_at")),
    }
    if versions is not None:
        payload["versions"] = [_to_version_dto(version) for version in versions]
    return payload


def _to_run_dto(trace: dict[str, Any]) -> dict[str, Any]:
    status = _normalize_run_status(trace.get("status"), trace)
    latency = trace.get("latency") or {}
    completed_at = trace.get("completed_at") if status in {"completed", "failed"} else None
    return {
        "id": trace.get("request_id"),
        "agent_id": trace.get("agent_id") or trace.get("session_id") or "default",
        "agent_name": trace.get("agent_name"),
        "status": status,
        "goal": trace.get("goal"),
        "started_at": _as_iso(trace.get("started_at") or trace.get("timestamp")),
        "completed_at": _as_iso(completed_at),
        "cache_hit": bool(trace.get("cache_hit", False)),
        "latency_total": latency.get("total"),
        "error": trace.get("error"),
    }


async def _get_agent_or_404(agent_id: str) -> dict[str, Any]:
    db = MongoDB.get_database()
    doc = await db.agents.find_one({"_id": agent_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Agent not found")
    return doc


async def _ensure_unique_agent_name(agent_id: str | None, name: str) -> None:
    db = MongoDB.get_database()
    duplicate = await db.agents.find_one({"name_lower": name.lower()})
    if duplicate and duplicate.get("_id") != agent_id:
        raise HTTPException(status_code=409, detail="Agent with this name already exists")


async def _create_agent_version_snapshot(
    agent_doc: dict[str, Any],
    version: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    db = MongoDB.get_database()
    snapshot = {
        "agent_id": str(agent_doc["_id"]),
        "version": version,
        "name": agent_doc.get("name"),
        "description": agent_doc.get("description"),
        "status": agent_doc.get("status", "active"),
        "metadata": metadata or {},
        "snapshot": {
            "name": agent_doc.get("name"),
            "description": agent_doc.get("description"),
            "status": agent_doc.get("status", "active"),
            "metadata": agent_doc.get("metadata", {}),
        },
        "created_at": datetime.now(timezone.utc),
    }
    await db.agent_versions.insert_one(snapshot)
    return snapshot


@router.get("/api/agents")
async def list_agents(
    q: str | None = Query(default=None, description="Agent name search"),
    _: dict = ReadableRole,
):
    db = MongoDB.get_database()
    query: dict[str, Any] = {}
    if q:
        query["name"] = {"$regex": q, "$options": "i"}
    docs = await db.agents.find(query).sort("created_at", DESCENDING).to_list(length=200)
    return [_to_agent_dto(doc) for doc in docs]


@router.post("/api/agents", status_code=201)
async def create_agent(payload: AgentCreateRequest, _: dict = DeveloperRole):
    db = MongoDB.get_database()
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Agent name is required")
    await _ensure_unique_agent_name(None, name)

    now = datetime.now(timezone.utc)
    current_version = payload.version.strip() or "1.0.0"
    doc = {
        "_id": str(uuid4()),
        "name": name,
        "name_lower": name.lower(),
        "version": current_version,
        "current_version": current_version,
        "description": payload.description,
        "status": payload.status,
        "metadata": payload.metadata,
        "created_at": now,
        "updated_at": now,
    }
    await db.agents.insert_one(doc)
    await _create_agent_version_snapshot(doc, current_version, {"source": "create"})
    versions = await db.agent_versions.find({"agent_id": doc["_id"]}).sort("created_at", DESCENDING).to_list(length=50)
    return _to_agent_dto(doc, versions)


@router.patch("/api/agents/{agent_id}")
async def update_agent(agent_id: str, payload: AgentUpdateRequest, _: dict = DeveloperRole):
    db = MongoDB.get_database()
    doc = await _get_agent_or_404(agent_id)
    update_data: dict[str, Any] = {"updated_at": datetime.now(timezone.utc)}

    if payload.name is not None:
        name = payload.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Agent name is required")
        await _ensure_unique_agent_name(agent_id, name)
        update_data["name"] = name
        update_data["name_lower"] = name.lower()
    if payload.description is not None:
        update_data["description"] = payload.description
    if payload.status is not None:
        update_data["status"] = payload.status
    if payload.metadata is not None:
        update_data["metadata"] = payload.metadata

    if len(update_data) == 1:
        raise HTTPException(status_code=400, detail="No fields to update")

    await db.agents.update_one({"_id": agent_id}, {"$set": update_data})
    updated = await _get_agent_or_404(agent_id)
    versions = await db.agent_versions.find({"agent_id": agent_id}).sort("created_at", DESCENDING).to_list(length=50)
    return _to_agent_dto(updated, versions)


@router.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str, _: dict = ReadableRole):
    db = MongoDB.get_database()
    doc = await _get_agent_or_404(agent_id)
    versions = await db.agent_versions.find({"agent_id": agent_id}).sort("created_at", DESCENDING).to_list(length=50)
    return _to_agent_dto(doc, versions)


@router.delete("/api/agents/{agent_id}", status_code=204)
async def delete_agent(agent_id: str, _: dict = AdminRole):
    db = MongoDB.get_database()
    result = await db.agents.delete_one({"_id": agent_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
    await db.agent_versions.delete_many({"agent_id": agent_id})


@router.get("/api/agents/{agent_id}/versions")
async def list_agent_versions(agent_id: str, _: dict = ReadableRole):
    db = MongoDB.get_database()
    await _get_agent_or_404(agent_id)
    versions = await db.agent_versions.find({"agent_id": agent_id}).sort("created_at", DESCENDING).to_list(length=100)
    return [_to_version_dto(version) for version in versions]


@router.post("/api/agents/{agent_id}/versions", status_code=201)
async def create_agent_version(agent_id: str, payload: AgentVersionCreateRequest, _: dict = DeveloperRole):
    db = MongoDB.get_database()
    agent_doc = await _get_agent_or_404(agent_id)
    version = payload.version.strip()
    if not version:
        raise HTTPException(status_code=400, detail="Version is required")

    existing = await db.agent_versions.find_one({"agent_id": agent_id, "version": version})
    if existing:
        raise HTTPException(status_code=409, detail="Version already exists for this agent")

    snapshot = await _create_agent_version_snapshot(agent_doc, version, payload.metadata)
    await db.agents.update_one(
        {"_id": agent_id},
        {"$set": {"current_version": version, "version": version, "updated_at": datetime.now(timezone.utc)}},
    )
    return _to_version_dto(snapshot)


@router.post("/api/agents/{agent_id}/versions/{version}/promote")
async def promote_agent_version(agent_id: str, version: str, _: dict = AdminRole):
    db = MongoDB.get_database()
    agent_doc = await _get_agent_or_404(agent_id)
    version_doc = await db.agent_versions.find_one({"agent_id": agent_id, "version": version})
    if not version_doc:
        raise HTTPException(status_code=404, detail="Version not found")

    snapshot = version_doc.get("snapshot", {})
    next_name = snapshot.get("name", agent_doc.get("name"))
    await _ensure_unique_agent_name(agent_id, next_name)

    await db.agents.update_one(
        {"_id": agent_id},
        {
            "$set": {
                "name": next_name,
                "name_lower": next_name.lower(),
                "description": snapshot.get("description"),
                "status": snapshot.get("status", "active"),
                "metadata": snapshot.get("metadata", {}),
                "current_version": version,
                "version": version,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    updated = await _get_agent_or_404(agent_id)
    versions = await db.agent_versions.find({"agent_id": agent_id}).sort("created_at", DESCENDING).to_list(length=100)
    return _to_agent_dto(updated, versions)


@router.delete("/api/runs/{request_id}", status_code=204)
async def delete_run(request_id: str, _: dict = AdminRole):
    db = MongoDB.get_database()
    result = await db.traces.delete_one({"request_id": request_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Run not found")
    await db.run_events.delete_many({"run_id": request_id})


@router.get("/api/runs")
async def list_runs(
    q: str | None = Query(default=None, description="Run id, goal, agent, or trace search"),
    status: Literal["all", "queued", "running", "completed", "failed"] = "all",
    _: dict = ReadableRole,
):
    db = MongoDB.get_database()
    query: dict[str, Any] = {}
    if status != "all":
        query["status"] = status
    if q:
        regex = {"$regex": q.strip(), "$options": "i"}
        query["$or"] = [
            {"request_id": regex},
            {"agent_id": regex},
            {"agent_name": regex},
            {"goal": regex},
        ]

    traces = await db.traces.find(query).sort("timestamp", DESCENDING).to_list(length=500)
    return [_to_run_dto(trace) for trace in traces if trace.get("request_id")]


@router.get("/traces/{request_id}")
async def get_trace(request_id: str, _: dict = ReadableRole):
    db = MongoDB.get_database()
    trace = await db.traces.find_one({"request_id": request_id})
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")

    serialized = _serialize(trace)
    serialized["_id"] = str(trace.get("_id"))
    serialized["id"] = request_id
    serialized["status"] = _normalize_run_status(trace.get("status"), trace)
    return serialized


@router.post("/api/runs/submit", status_code=202)
async def submit_run(payload: RunSubmitRequest, _: dict = DeveloperRole):
    from app.tasks.agent_tasks import execute_agent_run

    db = MongoDB.get_database()
    run_id = str(uuid4())
    agent_name = None
    if payload.agent_id:
        agent_doc = await _get_agent_or_404(payload.agent_id)
        agent_name = agent_doc.get("name")

    now = datetime.now(timezone.utc)
    trace_doc = {
        "request_id": run_id,
        "session_id": payload.session_id,
        "agent_id": payload.agent_id,
        "agent_name": agent_name,
        "goal": payload.goal,
        "status": "queued",
        "plan": None,
        "steps": [],
        "observations": [],
        "final_answer": None,
        "cache_hit": False,
        "latency": {},
        "error": None,
        "queued_at": now,
        "timestamp": now,
    }
    await db.traces.insert_one(trace_doc)
    await db.run_events.insert_one(
        {
            "run_id": run_id,
            "event": "status_change",
            "data": {"status": "queued"},
            "timestamp": now,
        }
    )

    execute_agent_run.delay(run_id, payload.session_id, payload.goal, payload.agent_id)
    return {"run_id": run_id, "status": "queued"}


@router.get("/api/runs/{run_id}/status")
async def get_run_status(run_id: str, _: dict = ReadableRole):
    db = MongoDB.get_database()
    trace = await db.traces.find_one({"request_id": run_id})
    if not trace:
        raise HTTPException(status_code=404, detail="Run not found")

    dto = _to_run_dto(trace)
    response = {
        "run_id": run_id,
        "status": dto["status"],
        "goal": dto["goal"],
        "agent_id": dto["agent_id"],
        "agent_name": dto["agent_name"],
        "started_at": dto["started_at"],
        "completed_at": dto["completed_at"],
        "cache_hit": dto["cache_hit"],
        "latency_total": dto["latency_total"],
        "error": dto["error"],
    }
    if dto["status"] == "completed":
        response["result"] = trace.get("final_answer")
    return response


@router.get("/api/feature-flags")
async def get_feature_flags():
    return feature_flags_payload()
