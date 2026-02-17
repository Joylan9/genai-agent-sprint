"""
app/services/planning_agent_service.py
Enterprise planning agent service with Smart Response Caching.
"""

from typing import Optional, List, Dict, Any
from ollama import chat
import json
import re
import time
import asyncio
import inspect

from datetime import datetime

from ..infra.logger import (
    StructuredLogger,
    generate_request_id,
    REQUEST_COUNTER,
    REQUEST_LATENCY,
)
from ..registry.tool_registry import ToolRegistry
from ..routing.intelligent_router import IntelligentRouter
from ..memory.memory_manager import MemoryManager
from ..memory.database import MongoDB
from ..cache.response_cache import ResponseCache


class PlanningAgentService:
    def __init__(
        self,
        model_name: str = "llama3:8b-instruct-q4_K_M",
        tool_registry: Optional[ToolRegistry] = None,
        router: Optional[IntelligentRouter] = None,
        logger: Optional[StructuredLogger] = None,
        max_json_retries: int = 2,
        memory_manager: Optional[MemoryManager] = None,
    ):
        self.model_name = model_name
        self.registry = tool_registry
        self.router = router
        self.logger = logger
        self.max_json_retries = max_json_retries
        self.memory = memory_manager or MemoryManager()

        # ✅ Initialize Cache
        db = MongoDB.get_database()
        self.cache = ResponseCache(db)

    # ============================================================
    # PLAN CREATION (unchanged)
    # ============================================================

    def create_plan(self, goal: str) -> str:
        available_tools = ", ".join(
            self.registry.list_tools() if self.registry else []
        )

        messages = [
            {
                "role": "system",
                "content": f"""
You are a planning agent.

You ONLY have access to:
{available_tools}

Return ONLY valid JSON:

{{
  "steps": [
    {{"tool": "<tool_name>", "query": "<query>"}}
  ]
}}

Rules:
- Use only listed tool names
- No markdown
- No explanations
"""
            },
            {"role": "user", "content": goal},
        ]

        response = chat(
            model=self.model_name,
            messages=messages,
            format="json",
            options={"temperature": 0},
        )

        content = response["message"]["content"]
        if isinstance(content, dict):
            plan_text = json.dumps(content)
        else:
            plan_text = content

        if self.logger:
            try:
                self.logger.log("planner_raw_output", {"raw": plan_text[:2000]})
            except Exception:
                pass

        return plan_text

    # ============================================================
    # JSON PARSING (unchanged)
    # ============================================================

    def parse_plan_json(self, plan_text: str) -> List[Dict[str, Any]]:
        def extract_json(text: str):
            match = re.search(r"\{.*?\}", text, re.DOTALL)
            return match.group(0) if match else None

        if isinstance(plan_text, dict):
            plan = plan_text
            if "steps" not in plan or not isinstance(plan["steps"], list):
                raise ValueError("Invalid 'steps' format.")
            for step in plan["steps"]:
                if (
                    not isinstance(step, dict)
                    or "tool" not in step
                    or "query" not in step
                ):
                    raise ValueError("Invalid step format.")
            return plan["steps"]

        attempt = 0
        current_text = plan_text

        while attempt <= self.max_json_retries:
            try:
                try:
                    plan = json.loads(current_text)
                except Exception:
                    extracted = extract_json(current_text)
                    if not extracted:
                        raise ValueError("No JSON found.")
                    plan = json.loads(extracted)

                if "steps" not in plan or not isinstance(plan["steps"], list):
                    raise ValueError("Invalid 'steps' format.")

                return plan["steps"]

            except Exception as e:
                if attempt >= self.max_json_retries:
                    raise ValueError(f"Plan parsing failed: {e}")

                repair_response = chat(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "Fix JSON only."},
                        {"role": "user", "content": current_text},
                    ],
                    format="json",
                    options={"temperature": 0},
                )

                repair_content = repair_response["message"]["content"]
                current_text = (
                    json.dumps(repair_content)
                    if isinstance(repair_content, dict)
                    else repair_content
                )

                attempt += 1

        raise ValueError("JSON parsing failure.")

    # ============================================================
    # EXECUTION (WITH SMART CACHE + ENTERPRISE PARALLEL TOOLS)
    # ============================================================

    async def execute_plan(self, session_id: str, goal: str, plan_text: str):
        request_id = generate_request_id()
        REQUEST_COUNTER.inc()
        total_start = time.time()

        planner_start = time.time()
        steps = self.parse_plan_json(plan_text)
        planner_latency = time.time() - planner_start

        observations = []

        async def _maybe_await(obj):
            if inspect.isawaitable(obj):
                return await obj
            return obj

        tool_total_latency = 0.0
        tool_wall_start = time.time()

        # ============================================================
        # ENTERPRISE PARALLEL TOOL EXECUTION
        # ============================================================

        MAX_PARALLEL_TOOLS = 4
        semaphore = asyncio.Semaphore(MAX_PARALLEL_TOOLS)

        async def execute_single_step(index, step):
            async with semaphore:
                try:
                    if self.router:
                        response = await _maybe_await(
                            self.router.execute(step, request_id=request_id)
                        )
                    else:
                        tool = self.registry.get(step["tool"])
                        response = await _maybe_await(tool.execute(step))

                    return {
                        "index": index,
                        "step": index + 1,
                        "tool": step["tool"],
                        "query": step["query"],
                        "response": response,
                    }

                except Exception as e:
                    return {
                        "index": index,
                        "step": index + 1,
                        "tool": step.get("tool"),
                        "query": step.get("query"),
                        "response": {
                            "status": "error",
                            "data": None,
                            "metadata": {"error": str(e)},
                        },
                    }

        tasks = [
            execute_single_step(index, step)
            for index, step in enumerate(steps)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_results = []

        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    "index": -1,
                    "step": -1,
                    "tool": "unknown",
                    "query": "",
                    "response": {
                        "status": "error",
                        "data": None,
                        "metadata": {"error": str(result)},
                    },
                })
            else:
                processed_results.append(result)

        processed_results.sort(key=lambda x: x["index"])

        for result in processed_results:
            response = result["response"]

            metadata = response.get("metadata", {})
            if "total_execution_time" in metadata:
                tool_total_latency += float(metadata["total_execution_time"])

            observations.append(
                {
                    "step": result["step"],
                    "tool": result["tool"],
                    "query": result["query"],
                    "response": response,
                }
            )

        tool_wall_time = time.time() - tool_wall_start

        memory_context = await self.memory.retrieve_context(
            session_id=session_id,
            query=goal,
            recent_limit=5,
            semantic_top_k=3
        )

        # ============================================================
        # CACHE CHECK (Before Synthesis)
        # ============================================================

        cached_response = await self.cache.get(goal, plan_text)

        if cached_response:
            final_answer = cached_response
            synthesis_latency = 0.0
            cache_hit = True
        else:
            cache_hit = False

            synthesis_start = time.time()
            final_answer = await _maybe_await(
                self.synthesize_answer(goal, observations, memory_context)
            )
            synthesis_latency = time.time() - synthesis_start

            await self.cache.set(goal, plan_text, final_answer)

        await self.memory.save_interaction(
            session_id=session_id,
            user_message=goal,
            assistant_message=final_answer
        )

        try:
            db = MongoDB.get_database()
            await db.traces.insert_one({
                "request_id": request_id,
                "session_id": session_id,
                "goal": goal,
                "plan": plan_text,
                "steps": steps,
                "observations": observations,
                "final_answer": final_answer,
                "cache_hit": cache_hit,
                "latency": {
                    "planner": planner_latency,
                    "tool_total": tool_total_latency,
                    "tool_wall_time": tool_wall_time,
                    "synthesis": synthesis_latency,
                    "total": time.time() - total_start
                },
                "timestamp": datetime.utcnow()
            })
        except Exception:
            pass

        total_latency = time.time() - total_start
        REQUEST_LATENCY.observe(total_latency)

        return {"result": final_answer, "request_id": request_id}
