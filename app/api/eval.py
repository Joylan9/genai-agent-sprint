'''
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
'''

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from pymongo import DESCENDING

from app.api.auth import get_current_user, require_role
from app.memory.database import MongoDB
from app.services.eval_runner import EvalRunner

router = APIRouter(prefix="/api/eval", tags=["evaluation"])
ReadableRole = Depends(get_current_user)
DeveloperRole = Depends(require_role("developer", "admin"))
EVAL_DIR = Path(__file__).resolve().parents[2] / "eval"


class RunSuiteRequest(BaseModel):
    suite_name: str = Field(default="default", description="Whitelisted eval suite name.")


def _suite_registry() -> dict[str, Path]:
    registry: dict[str, Path] = {}
    for candidate in sorted(EVAL_DIR.glob("*.json")):
        registry[candidate.stem] = candidate
    if "test_cases" in registry and "default" not in registry:
        registry["default"] = registry["test_cases"]
    return registry


@router.get("/suites")
async def list_eval_suites(_: dict = ReadableRole):
    registry = _suite_registry()
    return [
        {"name": name, "path": path.name}
        for name, path in sorted(registry.items(), key=lambda item: item[0])
    ]


@router.post("/run-suite")
async def run_evaluation_suite(payload: RunSuiteRequest, _: dict = DeveloperRole):
    registry = _suite_registry()
    suite_path = registry.get(payload.suite_name)
    if not suite_path:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown suite '{payload.suite_name}'. Allowed suites: {', '.join(sorted(registry))}",
        )

    try:
        test_cases = json.loads(suite_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Suite file not found: {suite_path.name}") from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in suite file: {suite_path.name}") from exc

    runner = EvalRunner()
    result = await runner.run_suite(test_cases, suite_name=payload.suite_name, suite_source=suite_path.name)
    result.pop("_id", None)
    return result


@router.get("/results")
async def list_eval_results(_: dict = ReadableRole):
    db = MongoDB.get_database()
    cursor = db.eval_results.find(
        {},
        {
            "suite_id": 1,
            "suite_name": 1,
            "suite_source": 1,
            "total": 1,
            "passed": 1,
            "failed": 1,
            "avg_score": 1,
            "avg_latency": 1,
            "timestamp": 1,
        },
    ).sort("timestamp", DESCENDING)

    results = await cursor.to_list(length=50)
    for result in results:
        result["_id"] = str(result["_id"])
        if "timestamp" in result and hasattr(result["timestamp"], "isoformat"):
            result["timestamp"] = result["timestamp"].isoformat()
    return results


@router.get("/results/{suite_id}")
async def get_eval_result(suite_id: str, _: dict = ReadableRole):
    db = MongoDB.get_database()
    result = await db.eval_results.find_one({"suite_id": suite_id})
    if not result:
        raise HTTPException(status_code=404, detail="Evaluation result not found")
    result["_id"] = str(result["_id"])
    if "timestamp" in result and hasattr(result["timestamp"], "isoformat"):
        result["timestamp"] = result["timestamp"].isoformat()
    return result
