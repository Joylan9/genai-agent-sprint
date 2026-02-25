"""
app/services/eval_runner.py

Evaluation engine for measuring agent quality.
Runs test cases through the agent pipeline and scores results using:
  - Keyword coverage (expected keywords found in answer)
  - Tool accuracy (expected tools used vs actual tools used)
  - Latency performance
  - LLM-as-judge scoring (optional, uses the same LLM)
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.memory.database import MongoDB
from app.infra.ollama_client import get_ollama_client, get_ollama_model, llm_chat


class EvalRunner:
    """Run evaluation suites against the agent pipeline."""

    def __init__(self):
        self.db = MongoDB.get_database()

    async def run_suite(self, test_cases: list[dict], suite_name: str = "default") -> dict:
        """
        Execute all test cases and return aggregated results.

        Returns:
            {
                suite_id: str,
                suite_name: str,
                total: int,
                passed: int,
                failed: int,
                avg_score: float,
                avg_latency: float,
                results: [per-case results]
            }
        """
        suite_id = str(uuid4())
        results = []

        for case in test_cases:
            result = await self._run_single_case(case)
            results.append(result)

        # Aggregate
        scores = [r["score"] for r in results]
        latencies = [r["latency"] for r in results if r["latency"] is not None]

        suite_result = {
            "suite_id": suite_id,
            "suite_name": suite_name,
            "total": len(results),
            "passed": sum(1 for r in results if r["passed"]),
            "failed": sum(1 for r in results if not r["passed"]),
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "avg_latency": sum(latencies) / len(latencies) if latencies else 0,
            "results": results,
            "timestamp": datetime.now(timezone.utc),
        }

        # Store in MongoDB
        await self.db.eval_results.insert_one(suite_result)

        return suite_result

    async def _run_single_case(self, case: dict) -> dict:
        """Run a single test case through the agent."""
        case_id = case.get("id", str(uuid4()))
        goal = case.get("goal", "")
        expected_tools = case.get("expected_tools", [])
        expected_keywords = case.get("expected_keywords", [])

        start = time.time()
        try:
            # Build agent and execute
            from api.dependencies import build_agent
            agent = build_agent()

            plan = await agent.create_plan(goal, session_id=f"eval-{case_id}")
            result = await agent.execute_plan(f"eval-{case_id}", goal, plan)

            latency = time.time() - start
            answer = result.get("result", "")
            observations = result.get("observations", [])

            # ---- Scoring ----
            keyword_score = self._score_keywords(answer, expected_keywords)
            tool_score = self._score_tools(observations, expected_tools)
            llm_score = await self._llm_judge(goal, answer)

            # Weighted overall score (0-100)
            overall_score = (
                keyword_score * 0.3 +
                tool_score * 0.3 +
                llm_score * 0.4
            )

            passed = overall_score >= 50

            return {
                "case_id": case_id,
                "goal": goal,
                "category": case.get("category", "general"),
                "difficulty": case.get("difficulty", "medium"),
                "passed": passed,
                "score": round(overall_score, 1),
                "keyword_score": round(keyword_score, 1),
                "tool_score": round(tool_score, 1),
                "llm_score": round(llm_score, 1),
                "latency": round(latency, 2),
                "answer_preview": answer[:500] if answer else None,
                "tools_used": [obs.get("tool") for obs in observations],
                "expected_tools": expected_tools,
                "error": None,
            }

        except Exception as e:
            return {
                "case_id": case_id,
                "goal": goal,
                "category": case.get("category", "general"),
                "difficulty": case.get("difficulty", "medium"),
                "passed": False,
                "score": 0,
                "keyword_score": 0,
                "tool_score": 0,
                "llm_score": 0,
                "latency": round(time.time() - start, 2),
                "answer_preview": None,
                "tools_used": [],
                "expected_tools": expected_tools,
                "error": str(e),
            }

    def _score_keywords(self, answer: str, expected: list[str]) -> float:
        """Score 0-100 based on what fraction of expected keywords appear in the answer."""
        if not expected or not answer:
            return 50.0  # neutral if no expectations
        answer_lower = answer.lower()
        found = sum(1 for kw in expected if kw.lower() in answer_lower)
        return (found / len(expected)) * 100

    def _score_tools(self, observations: list[dict], expected: list[str]) -> float:
        """Score 0-100 based on whether expected tools were used."""
        if not expected:
            return 100.0  # no tool expectations = pass
        if not observations:
            return 0.0
        used = {obs.get("tool", "") for obs in observations}
        found = sum(1 for t in expected if t in used)
        return (found / len(expected)) * 100

    async def _llm_judge(self, goal: str, answer: str) -> float:
        """
        Use the LLM as a judge to score answer quality.
        Returns 0-100 score.
        """
        if not answer:
            return 0.0

        try:
            client = get_ollama_client()
            model = get_ollama_model()

            messages = [
                {
                    "role": "system",
                    "content": """You are an evaluation judge.
Score the following answer on a scale of 0 to 100 based on:
- Relevance to the question (40%)
- Accuracy and correctness (30%)
- Completeness (30%)

Return ONLY a JSON object: {"score": <number>, "reason": "<brief reason>"}
"""
                },
                {
                    "role": "user",
                    "content": f"Question: {goal}\n\nAnswer: {answer[:1000]}"
                }
            ]

            response = await llm_chat(
                client,
                model=model,
                messages=messages,
                format="json",
                options={"temperature": 0, "num_ctx": 2048},
            )

            content = response["message"]["content"]
            if isinstance(content, str):
                parsed = json.loads(content)
            else:
                parsed = content

            return float(parsed.get("score", 50))

        except Exception:
            return 50.0  # neutral on judge failure
