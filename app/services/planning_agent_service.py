"""
app/services/planning_agent_service.py
Enterprise planning agent service.
"""

from typing import Optional, List, Dict, Any
from ollama import chat
import json
import re
import time
import asyncio
import inspect

from ..infra.logger import StructuredLogger, generate_request_id
from ..registry.tool_registry import ToolRegistry
from ..routing.intelligent_router import IntelligentRouter
from ..memory.memory_manager import MemoryManager


class PlanningAgentService:
    def __init__(
        self,
        model_name: str = "llama3",
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

    # ============================================================
    # PLAN CREATION
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
                    or not isinstance(step["tool"], str)
                    or not isinstance(step["query"], str)
                ):
                    raise ValueError("Invalid step format.")
                if len(step["query"]) > 3000:
                    raise ValueError("Step query too long.")
                if self.registry and step["tool"] not in self.registry.list_tools():
                    raise ValueError(f"Unknown tool: {step['tool']}")
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

                for step in plan["steps"]:
                    if (
                        not isinstance(step, dict)
                        or "tool" not in step
                        or "query" not in step
                        or not isinstance(step["tool"], str)
                        or not isinstance(step["query"], str)
                    ):
                        raise ValueError("Invalid step format.")

                    if len(step["query"]) > 3000:
                        raise ValueError("Step query too long.")

                    if self.registry and step["tool"] not in self.registry.list_tools():
                        raise ValueError(f"Unknown tool: {step['tool']}")

                return plan["steps"]

            except Exception as e:
                if self.logger:
                    self.logger.log(
                        "plan_parse_attempt_failed",
                        {"error": str(e), "attempt": attempt},
                    )

                if attempt >= self.max_json_retries:
                    raise ValueError(f"Plan parsing failed: {e}")

                repair_prompt = f"""
Fix this malformed JSON. Return ONLY valid JSON:

{current_text}
"""

                repair_response = chat(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "Fix JSON only."},
                        {"role": "user", "content": repair_prompt},
                    ],
                    format="json",
                    options={"temperature": 0},
                )

                repair_content = repair_response["message"]["content"]
                if isinstance(repair_content, dict):
                    current_text = json.dumps(repair_content)
                else:
                    current_text = repair_content

                attempt += 1

        raise ValueError("JSON parsing failure.")

    # ============================================================
    # EXECUTION
    # ============================================================
    async def execute_plan(self, session_id: str, goal: str, plan_text: str):
        request_id = generate_request_id()
        start = time.time()

        if self.logger:
            self.logger.log(
                "request_started",
                {"request_id": request_id, "goal_preview": goal[:300]},
            )

        try:
            steps = self.parse_plan_json(plan_text)
        except ValueError as e:
            if self.logger:
                self.logger.log(
                    "request_failed_plan_parse",
                    {"request_id": request_id, "error": str(e)},
                )
            return {"result": f"❌ Plan parsing failed: {e}", "request_id": request_id}

        observations = []

        async def _maybe_await(obj):
            if inspect.isawaitable(obj):
                return await obj
            return obj

        for index, step in enumerate(steps):

            if self.router:
                response = await _maybe_await(self.router.execute(step, request_id=request_id))
            else:
                tool = self.registry.get(step["tool"])
                response = await _maybe_await(tool.execute(step))

            if not isinstance(response, dict):
                response = {
                    "status": "error",
                    "data": None,
                    "metadata": {"error": "Invalid tool response format."},
                }

            observations.append(
                {
                    "step": index + 1,
                    "tool": step["tool"],
                    "query": step["query"],
                    "response": response,
                }
            )

        # ----------------------------
        # Retrieve Memory Context
        # ----------------------------
        memory_context = await self.memory.retrieve_context(
            session_id=session_id,
            query=goal,
            recent_limit=5,
            semantic_top_k=3
        )

        final_answer = await _maybe_await(
            self.synthesize_answer(
                goal,
                observations,
                memory_context
            )
        )

        # ----------------------------
        # Save Interaction
        # ----------------------------
        await self.memory.save_interaction(
            session_id=session_id,
            user_message=goal,
            assistant_message=final_answer
        )

        if self.logger:
            self.logger.log(
                "execution_finished",
                {"request_id": request_id, "duration": time.time() - start},
            )

        return {"result": final_answer, "request_id": request_id}

    # ============================================================
    # SYNTHESIS
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
