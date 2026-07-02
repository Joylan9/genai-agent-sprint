"""
app/api/stream.py

Server-Sent Events (SSE) endpoint for real-time run progress.

Clients connect via:
    GET /api/runs/{run_id}/stream

Events emitted:
    status_change   — queued/running/completed/failed
    planner_start   — planner LLM call started
    planner_complete — planner finished, plan preview
    execution_start  — tool execution beginning
    tool_start       — individual tool starting
    tool_complete    — individual tool finished
    execution_complete — all tools done
    synthesis_start  — synthesis LLM call started
    synthesis_complete — synthesis finished
    result           — final answer
    error            — execution error
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from app.api.auth import get_current_user_from_access_token
from app.memory.database import MongoDB

router = APIRouter(tags=["streaming"])

# How often to poll for new events (seconds)
_POLL_INTERVAL = 0.5
# Maximum time to keep SSE connection open (seconds)
_MAX_STREAM_DURATION = 300


def _serialize_event(event_type: str, data: dict) -> str:
    """Format an SSE event string."""
    payload = json.dumps(data, default=str)
    return f"event: {event_type}\ndata: {payload}\n\n"


async def _event_generator(run_id: str) -> AsyncGenerator[str, None]:
    """
    Yield SSE events by polling the run_events collection.
    Terminates when status reaches completed/failed or timeout.
    """
    db = MongoDB.get_database()
    seen_ids: set = set()
    start_time = asyncio.get_event_loop().time()

    # Send initial keepalive
    yield _serialize_event("connected", {"run_id": run_id, "message": "Stream connected"})

    while True:
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > _MAX_STREAM_DURATION:
            yield _serialize_event("timeout", {"message": "Stream timeout reached"})
            break

        # Fetch new events since last check
        cursor = db.run_events.find(
            {"run_id": run_id}
        ).sort("timestamp", 1)

        events = await cursor.to_list(length=100)

        for event in events:
            event_id = str(event["_id"])
            if event_id not in seen_ids:
                seen_ids.add(event_id)
                yield _serialize_event(
                    event.get("event", "update"),
                    event.get("data", {})
                )

                # Check for terminal events
                if event.get("event") == "status_change":
                    status = event.get("data", {}).get("status")
                    if status in ("completed", "failed"):
                        return

        await asyncio.sleep(_POLL_INTERVAL)


@router.get("/api/runs/{run_id}/stream")
async def stream_run_events(
    run_id: str,
    request: Request,
    access_token: str | None = Query(default=None),
):
    """
    SSE endpoint for real-time run progress.

    Usage (JavaScript):
        const source = new EventSource('/api/runs/{run_id}/stream');
        source.addEventListener('status_change', (e) => {
            console.log(JSON.parse(e.data));
        });
    """
    bearer_token = access_token
    if not bearer_token:
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            bearer_token = auth_header.split(" ", 1)[1].strip()
    await get_current_user_from_access_token(bearer_token)
    db = MongoDB.get_database()
    trace = await db.traces.find_one({"request_id": run_id})
    if not trace:
        raise HTTPException(status_code=404, detail="Run not found")

    return StreamingResponse(
        _event_generator(run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
