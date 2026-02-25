"""
app/api/eval.py

Evaluation API router for running test suites and viewing results.

Endpoints:
  POST /api/eval/run-suite    — trigger an evaluation run
  GET  /api/eval/results      — list past evaluation runs
  GET  /api/eval/results/{id} — detailed result for a specific suite
"""

from __future__ import annotations

import json
import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from pymongo import DESCENDING

from app.memory.database import MongoDB
from app.services.eval_runner import EvalRunner

router = APIRouter(prefix="/api/eval", tags=["evaluation"])


class RunSuiteRequest(BaseModel):
    suite_name: str = Field(default="default", description="Name for this eval run")
    test_cases_path: Optional[str] = Field(
        default=None,
        description="Path to test cases JSON file. Uses eval/test_cases.json if not specified.",
    )


@router.post("/run-suite")
async def run_evaluation_suite(payload: RunSuiteRequest):
    """
    Trigger an evaluation suite run.
    Loads test cases and runs each through the agent pipeline.
    """
    # Load test cases
    path = payload.test_cases_path or os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "eval",
        "test_cases.json",
    )

    try:
        with open(path, "r") as f:
            test_cases = json.load(f)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Test cases file not found: {path}",
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON in test cases file",
        )

    runner = EvalRunner()
    result = await runner.run_suite(test_cases, suite_name=payload.suite_name)

    # Convert ObjectId for JSON response
    result.pop("_id", None)
    return result


@router.get("/results")
async def list_eval_results():
    """List all past evaluation suite runs with summary stats."""
    db = MongoDB.get_database()
    cursor = db.eval_results.find(
        {},
        {
            "suite_id": 1,
            "suite_name": 1,
            "total": 1,
            "passed": 1,
            "failed": 1,
            "avg_score": 1,
            "avg_latency": 1,
            "timestamp": 1,
        },
    ).sort("timestamp", DESCENDING)

    results = await cursor.to_list(length=50)
    for r in results:
        r["_id"] = str(r["_id"])
        if "timestamp" in r and hasattr(r["timestamp"], "isoformat"):
            r["timestamp"] = r["timestamp"].isoformat()

    return results


@router.get("/results/{suite_id}")
async def get_eval_result(suite_id: str):
    """Get detailed results for a specific evaluation suite run."""
    db = MongoDB.get_database()
    result = await db.eval_results.find_one({"suite_id": suite_id})
    if not result:
        raise HTTPException(status_code=404, detail="Evaluation result not found")

    result["_id"] = str(result["_id"])
    if "timestamp" in result and hasattr(result["timestamp"], "isoformat"):
        result["timestamp"] = result["timestamp"].isoformat()

    return result
