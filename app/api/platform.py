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
    final_answer = trace.get("final_answer")
    status: Literal["pending", "running", "completed", "failed"]
    if final_answer:
        status = "completed"
    else:
        status = "failed"

    return {
        "id": trace.get("request_id"),
        "agent_id": trace.get("agent_id") or trace.get("session_id") or "default",
        "status": status,
        "started_at": _as_iso(trace.get("timestamp")),
        "completed_at": _as_iso(trace.get("timestamp")),
        "result": final_answer if isinstance(final_answer, str) else None,
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

@router.get("/api/feature-flags")
async def get_feature_flags():
    # Return empty dict, meaning all flags use their default fallback configurations
    return {}
