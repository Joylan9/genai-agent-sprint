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

# ---------- New import: Guardrails ----------
from ..security.guardrails import Guardrails


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

        # ---------- Initialize Guardrails ----------
        allowed_tools = []
        try:
            if self.registry:
                # registry.list_tools() expected to be sync returning list
                allowed_tools = self.registry.list_tools()
        except Exception:
            # if registry not ready or fails, default to empty whitelist (tightest)
            allowed_tools = []

        self.guardrails = Guardrails(allowed_tools=allowed_tools)

    # ============================================================
    # PLAN CREATION
    # ============================================================

    def create_plan(self, goal: str) -> str:
        # ---------- Validate input BEFORE planner ----------
        # Hard-block on injection attempts or invalid input
        self.guardrails.validate_user_input(goal)

        available_tools = ", ".join(
            self.registry.list_tools() if self.registry else []
        )

        # Stronger planner system prompt that requires at least one step
        messages = [
            {
                "role": "system",
                "content": f"""
You are an autonomous planning agent.

You ONLY have access to the following tools (exact names):
{available_tools}

Your job:
- Break the user's goal into an ordered list of actionable steps.
- Each step must be a JSON object with keys: "tool" and "query".
- You MUST return at least one step. An empty "steps" list is NOT allowed.
- Use only tool names from the list above. Do not invent tool names.
- Do NOT include any explanations, markdown, or text outside the JSON.
- Output MUST be valid JSON and follow the exact schema below.

Return ONLY valid JSON with this structure:

{{
  "steps": [
    {{"tool": "<tool_name>", "query": "<query>"}},
    ...
  ]
}}

Example (must follow schema):
{{
  "steps": [
    {{"tool": "rag_search", "query": "find summary about X"}},
    {{"tool": "web_search", "query": "recent news about X"}}
  ]
}}
"""
            },
            {"role": "user", "content": goal},
        ]

        # Initial planner call (deterministic)
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

        # --- Ensure non-empty plan by attempting to parse and repair if needed ---
        # Try to parse and ensure 'steps' non-empty. If parsing fails or steps empty,
        # attempt a JSON-only repair with the model, then fallback to a safe plan.
        try:
            steps = self.parse_plan_json(plan_text)
            if not steps:
                raise ValueError("Planner returned empty 'steps'.")
            # if we have valid non-empty steps, return original text
            return plan_text
        except Exception as first_err:
            # log the initial parsing/emptiness issue
            if self.logger:
                try:
                    self.logger.log("planner_parse_issue", {"error": str(first_err), "raw": plan_text[:2000]})
                except Exception:
                    pass

            # Attempt automated JSON-only repair using the model
            try:
                repair_messages = [
                    {"role": "system", "content": "Fix JSON only. Ensure the JSON follows the schema and contains at least one step. Do not add commentary."},
                    {"role": "user", "content": plan_text},
                ]

                repair_response = chat(
                    model=self.model_name,
                    messages=repair_messages,
                    format="json",
                    options={"temperature": 0},
                )

                repair_content = repair_response["message"]["content"]
                if isinstance(repair_content, dict):
                    repaired_text = json.dumps(repair_content)
                else:
                    repaired_text = repair_content

                if self.logger:
                    try:
                        self.logger.log("planner_repair_output", {"raw": repaired_text[:2000]})
                    except Exception:
                        pass

                # attempt parse repaired text
                try:
                    repaired_steps = self.parse_plan_json(repaired_text)
                    if repaired_steps:
                        return repaired_text
                    # fallthrough to fallback if empty
                except Exception as repair_err:
                    if self.logger:
                        try:
                            self.logger.log("planner_repair_failed", {"error": str(repair_err), "raw": repaired_text[:2000]})
                        except Exception:
                            pass
                    # continue to fallback
            except Exception as repair_call_err:
                if self.logger:
                    try:
                        self.logger.log("planner_repair_call_failed", {"error": str(repair_call_err)})
                    except Exception:
                        pass

            # Final fallback: construct a safe single-step plan using first allowed tool or 'rag_search'
            try:
                fallback_tool = "rag_search"
                try:
                    allowed = self.registry.list_tools() if self.registry else []
                    if allowed and isinstance(allowed, list) and len(allowed) > 0:
                        # prefer a retrieval/search style tool if present, else first
                        # choose rag_search if it's available
                        if "rag_search" in allowed:
                            fallback_tool = "rag_search"
                        elif "web_search" in allowed:
                            fallback_tool = "web_search"
                        else:
                            fallback_tool = allowed[0]
                except Exception:
                    # keep default
                    pass

                fallback_plan = {"steps": [{"tool": fallback_tool, "query": goal}]}
                fallback_text = json.dumps(fallback_plan)

                if self.logger:
                    try:
                        self.logger.log("planner_fallback_applied", {"fallback": fallback_plan})
                    except Exception:
                        pass

                return fallback_text
            except Exception as final_err:
                # as a last resort raise original parsing error
                if self.logger:
                    try:
                        self.logger.log("planner_fallback_failed", {"error": str(final_err)})
                    except Exception:
                        pass
                raise first_err

    # ============================================================
    # JSON PARSING
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
    # EXECUTION
    # ============================================================

    async def execute_plan(self, session_id: str, goal: str, plan_text: str):
        request_id = generate_request_id()
        REQUEST_COUNTER.inc()
        total_start = time.time()

        # ----------------------------
        # PLAN PARSE
        # ----------------------------
        planner_start = time.time()
        steps = self.parse_plan_json(plan_text)
        planner_latency = time.time() - planner_start

        # ---------- Guardrail: validate parsed plan ----------
        # Hard-block if plan fails rules (tool whitelist, step limits, step structure)
        self.guardrails.validate_plan(steps)

        # ============================================================
        # 🔥 ENTERPRISE CACHE CHECK (BEFORE TOOLS)
        # ============================================================

        cached_response = await self.cache.get(goal, plan_text)

        if cached_response:
            total_latency = time.time() - total_start

            try:
                db = MongoDB.get_database()
                await db.traces.insert_one({
                    "request_id": request_id,
                    "session_id": session_id,
                    "goal": goal,
                    "plan": plan_text,
                    "steps": steps,
                    "observations": [],
                    "final_answer": cached_response,
                    "cache_hit": True,
                    "latency": {
                        "planner": planner_latency,
                        "tool_total": 0.0,
                        "tool_wall_time": 0.0,
                        "synthesis": 0.0,
                        "total": total_latency
                    },
                    "timestamp": datetime.utcnow()
                })
            except Exception:
                pass

            REQUEST_LATENCY.observe(total_latency)

            return {"result": cached_response, "request_id": request_id}

        # ============================================================
        # 🚀 TOOL EXECUTION (ONLY IF CACHE MISS)
        # ============================================================

        observations = []

        async def _maybe_await(obj):
            if inspect.isawaitable(obj):
                return await obj
            return obj

        tool_total_latency = 0.0
        tool_wall_start = time.time()

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

        processed_results = [
            r for r in results if not isinstance(r, Exception)
        ]

        processed_results.sort(key=lambda x: x["index"])

        for result in processed_results:
            response = result["response"]
            metadata = response.get("metadata", {})

            # If tool published its own execution time, collect it
            if "total_execution_time" in metadata:
                try:
                    tool_total_latency += float(metadata["total_execution_time"])
                except Exception:
                    pass

            # ---------- Guardrail: sanitize tool output ----------
            # Try to extract a textual representation of data to scan for injection/leakage
            data_to_scan = ""
            if isinstance(response, dict):
                # prefer .get('data'), otherwise stringify the whole response
                data_to_scan = response.get("data", "")
                if data_to_scan is None:
                    data_to_scan = ""
                if not isinstance(data_to_scan, str):
                    # attempt to stringify reasonably
                    try:
                        data_to_scan = json.dumps(data_to_scan)
                    except Exception:
                        data_to_scan = str(data_to_scan)
            else:
                # non-dict, cast to str
                data_to_scan = str(response)

            try:
                # may raise ValueError (hard-block); we let it propagate up to caller
                self.guardrails.sanitize_tool_output(data_to_scan)
            except Exception as e:
                # convert to an error-style observation (so traces contain cause) then raise
                # we store as an error observation and abort after recording trace
                err_obs = {
                    "step": result["step"],
                    "tool": result.get("tool"),
                    "query": result.get("query"),
                    "response": {
                        "status": "error",
                        "data": None,
                        "metadata": {"error": f"guardrails: {str(e)}"}
                    }
                }
                # Persist trace indicating guardrail hit and then raise to block request
                try:
                    db = MongoDB.get_database()
                    await db.traces.insert_one({
                        "request_id": request_id,
                        "session_id": session_id,
                        "goal": goal,
                        "plan": plan_text,
                        "steps": steps,
                        "observations": [err_obs],
                        "final_answer": None,
                        "cache_hit": False,
                        "latency": {
                            "planner": planner_latency,
                            "tool_total": tool_total_latency,
                            "tool_wall_time": time.time() - tool_wall_start,
                            "synthesis": 0.0,
                            "total": time.time() - total_start
                        },
                        "timestamp": datetime.utcnow()
                    })
                except Exception:
                    pass

                # Hard-block: raise to caller
                raise

            observations.append(
                {
                    "step": result["step"],
                    "tool": result["tool"],
                    "query": result["query"],
                    "response": response,
                }
            )

        tool_wall_time = time.time() - tool_wall_start

        # ----------------------------
        # MEMORY
        # ----------------------------

        memory_context = await self.memory.retrieve_context(
            session_id=session_id,
            query=goal,
            recent_limit=5,
            semantic_top_k=3
        )

        # ----------------------------
        # SYNTHESIS
        # ----------------------------

        synthesis_start = time.time()
        final_answer = await _maybe_await(
            self.synthesize_answer(goal, observations, memory_context)
        )
        synthesis_latency = time.time() - synthesis_start

        # ---------- Guardrail: final answer check ----------
        # Hard-block on sensitive leakage in final answer
        self.guardrails.validate_final_answer(final_answer)

        # ---------- Guardrail: memory write protection ----------
        # Hard-block if final answer contains phrases that would poison memory if saved
        self.guardrails.validate_memory_write(final_answer)

        # At this point, final_answer passed guardrails; cache and persist
        await self.cache.set(goal, plan_text, final_answer)

        await self.memory.save_interaction(
            session_id=session_id,
            user_message=goal,
            assistant_message=final_answer
        )

        total_latency = time.time() - total_start

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
                "cache_hit": False,
                "latency": {
                    "planner": planner_latency,
                    "tool_total": tool_total_latency,
                    "tool_wall_time": tool_wall_time,
                    "synthesis": synthesis_latency,
                    "total": total_latency
                },
                "timestamp": datetime.utcnow()
            })
        except Exception:
            pass

        REQUEST_LATENCY.observe(total_latency)

        return {"result": final_answer, "request_id": request_id}

    # ============================================================
    # SYNTHESIS (ADDED BACK)
    # ============================================================

    def synthesize_answer(
        self,
        goal: str,
        observations: List[Dict[str, Any]],
        memory_context: Optional[Dict[str, Any]] = None
    ) -> str:

        observation_text = ""

        for obs in observations:
            observation_text += (
                f"\nStep {obs['step']} ({obs['tool']} - {obs['query']}):\n"
                f"{obs['response'].get('data', '')}\n"
            )

        memory_text = ""

        if memory_context:
            recent = memory_context.get("recent_messages", [])
            relevant = memory_context.get("relevant_memory", [])

            if recent:
                memory_text += "\nRecent Conversation:\n"
                for msg in recent:
                    memory_text += f"{msg.get('role')}: {msg.get('content')}\n"

            if relevant:
                memory_text += "\nRelevant Past Memory:\n"
                for mem in relevant:
                    memory_text += f"{mem.get('text')}\n"

        messages = [
            {
                "role": "system",
                "content": "Use ONLY provided observations and memory. Do not invent.",
            },
            {
                "role": "user",
                "content": f"""
Goal:
{goal}

Memory:
{memory_text}

Observations:
{observation_text}
""",
            },
        ]

        response = chat(model=self.model_name, messages=messages)
        content = response["message"]["content"]

        if isinstance(content, dict):
            if "answer" in content and isinstance(content["answer"], str):
                return content["answer"]
            return json.dumps(content)

        return content