"""
app/tasks/agent_tasks.py

Celery task definitions for asynchronous agent execution.
Decouples long-running LLM + tool work from the FastAPI API process.

Flow:
  POST /api/runs/submit → creates trace(status=queued) → enqueues this task
  Worker picks up → status=running → execute → status=completed|failed
"""

import asyncio
import traceback
from datetime import datetime, timezone

from app.infra.celery_app import celery_app
from app.memory.database import MongoDB


def _get_event_loop():
    """Get or create an event loop for running async code in sync Celery tasks."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("closed")
        return loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    loop = _get_event_loop()
    return loop.run_until_complete(coro)


async def _update_trace(db, run_id: str, update: dict):
    """Update a trace document by run_id (request_id)."""
    await db.traces.update_one(
        {"request_id": run_id},
        {"$set": update}
    )


async def _emit_event(db, run_id: str, event_type: str, data: dict = None):
    """Write a progress event for SSE consumption (Phase 2 ready)."""
    await db.run_events.insert_one({
        "run_id": run_id,
        "event": event_type,
        "data": data or {},
        "timestamp": datetime.now(timezone.utc),
    })


async def _execute_agent_async(run_id: str, session_id: str, goal: str):
    """
    Core async execution logic.
    Called from the sync Celery task via _run_async().
    """
    # ---- Connect to MongoDB (worker process) ----
    MongoDB.connect()
    db = MongoDB.get_database()

    try:
        # ---- Mark as running ----
        await _update_trace(db, run_id, {
            "status": "running",
            "started_at": datetime.now(timezone.utc),
        })
        await _emit_event(db, run_id, "status_change", {"status": "running"})

        # ---- Build the agent (same factory as API) ----
        from api.dependencies import build_agent
        agent = build_agent()

        # ---- Plan ----
        await _emit_event(db, run_id, "planner_start")
        plan = await agent.create_plan(goal, session_id=session_id)
        await _emit_event(db, run_id, "planner_complete", {"plan_preview": plan[:500]})

        await _update_trace(db, run_id, {
            "plan": plan,
            "status": "running",
        })

        # ---- Execute ----
        await _emit_event(db, run_id, "execution_start")
        result = await agent.execute_plan(session_id, goal, plan)
        await _emit_event(db, run_id, "execution_complete")

        # ---- Mark completed ----
        await _update_trace(db, run_id, {
            "status": "completed",
            "final_answer": result.get("result"),
            "completed_at": datetime.now(timezone.utc),
        })
        await _emit_event(db, run_id, "status_change", {"status": "completed"})

        return {"status": "completed", "run_id": run_id}

    except Exception as e:
        # ---- Mark failed ----
        error_detail = f"{type(e).__name__}: {str(e)}"
        tb = traceback.format_exc()

        await _update_trace(db, run_id, {
            "status": "failed",
            "error": error_detail,
            "error_traceback": tb,
            "completed_at": datetime.now(timezone.utc),
        })
        await _emit_event(db, run_id, "status_change", {
            "status": "failed",
            "error": error_detail,
        })

        return {"status": "failed", "run_id": run_id, "error": error_detail}


# ============================================================
# CELERY TASK DEFINITION
# ============================================================

@celery_app.task(
    name="agent.execute_run",
    bind=True,
    max_retries=1,
    default_retry_delay=5,
    acks_late=True,
    reject_on_worker_lost=True,
    time_limit=300,       # hard kill after 5 min
    soft_time_limit=240,  # SoftTimeLimitExceeded after 4 min
)
def execute_agent_run(self, run_id: str, session_id: str, goal: str):
    """
    Celery task: execute an agent run asynchronously.

    Called by the API with:
        execute_agent_run.delay(run_id, session_id, goal)

    The trace document must already exist with status='queued'.
    """
    try:
        return _run_async(_execute_agent_async(run_id, session_id, goal))
    except Exception as e:
        # If async execution itself crashes, mark as failed
        try:
            _run_async(_update_trace(
                MongoDB.get_database(),
                run_id,
                {
                    "status": "failed",
                    "error": f"Worker crash: {str(e)}",
                    "completed_at": datetime.now(timezone.utc),
                }
            ))
        except Exception:
            pass
        raise