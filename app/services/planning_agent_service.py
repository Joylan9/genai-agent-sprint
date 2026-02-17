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


class PlanningAgentService:
    def __init__(
        self,
        model_name: str = "llama3",
        tool_registry: Optional[ToolRegistry] = None,
        router: Optional[IntelligentRouter] = None,
        logger: Optional[StructuredLogger] = None,
        max_json_retries: int = 2,
    ):
        self.model_name = model_name
        self.registry = tool_registry
        self.router = router
        self.logger = logger
        self.max_json_retries = max_json_retries

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

        # === ENFORCE JSON FORMAT + DETERMINISTIC OUTPUT ===
        response = chat(
            model=self.model_name,
            messages=messages,
            format="json",
            options={"temperature": 0},
        )

        content = response["message"]["content"]
        # If the client already parsed JSON into a dict, convert to string for downstream parsing
        if isinstance(content, dict):
            plan_text = json.dumps(content)
        else:
            plan_text = content

        # log raw plan if logger present
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
            # non-greedy match to avoid grabbing trailing braces beyond the JSON block
            match = re.search(r"\{.*?\}", text, re.DOTALL)
            return match.group(0) if match else None

        # If an already-parsed dict was passed in, accept it directly
        if isinstance(plan_text, dict):
            plan = plan_text
            # validate immediately below
            if "steps" not in plan or not isinstance(plan["steps"], list):
                raise ValueError("Invalid 'steps' format.")
            # minimal validation loop reused from below
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
                # First try: direct parse (in case the text is pure JSON string)
                try:
                    plan = json.loads(current_text)
                except Exception:
                    # Fallback: extract JSON substring and parse
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

                # Ask the model to repair the JSON — enforce JSON format + deterministic output
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

                # log repair attempt
                if self.logger:
                    try:
                        self.logger.log(
                            "plan_repair_attempt",
                            {"attempt": attempt, "repair_preview": current_text[:1000]},
                        )
                    except Exception:
                        pass

                attempt += 1

        raise ValueError("JSON parsing failure.")

    # ============================================================
    # EXECUTION
    # ============================================================
    async def execute_plan(self, goal: str, plan_text: str):
        """
        Asynchronous execution pipeline.
        This method is async but compatible with sync router/tools because of _maybe_await helper.
        """
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

        if not self.registry:
            raise RuntimeError("Tool registry not configured.")

        observations = []

        async def _maybe_await(obj):
            # Await if coroutine/awaitable, else return directly
            if inspect.isawaitable(obj):
                return await obj
            return obj

        for index, step in enumerate(steps):

            if self.logger:
                self.logger.log(
                    "step_started",
                    {
                        "request_id": request_id,
                        "step": index + 1,
                        "tool": step.get("tool"),
                    },
                )

            # Execute step via router (if present) or direct tool
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

        if self.logger:
            self.logger.log(
                "execution_finished",
                {"request_id": request_id, "duration": time.time() - start},
            )

        # Synthesize answer (synchronous by default, but safe to await if it becomes async)
        final_answer = await _maybe_await(self.synthesize_answer(goal, observations))

        return {"result": final_answer, "request_id": request_id}

    # ============================================================
    # SYNTHESIS
    # ============================================================
    def synthesize_answer(
        self, goal: str, observations: List[Dict[str, Any]]
    ) -> str:

        observation_text = ""

        for obs in observations:
            observation_text += (
                f"\nStep {obs['step']} ({obs['tool']} - {obs['query']}):\n"
                f"{obs['response'].get('data', '')}\n"
            )

        messages = [
            {
                "role": "system",
                "content": "Use ONLY provided observations. Do not invent.",
            },
            {
                "role": "user",
                "content": f"Goal:\n{goal}\n\nObservations:\n{observation_text}",
            },
        ]

        # Synthesis should be human-readable free-form text — do not force JSON here.
        response = chat(model=self.model_name, messages=messages)
        content = response["message"]["content"]
        if isinstance(content, dict):
            # If structured, try to extract a text answer field if present, otherwise dump
            if "answer" in content and isinstance(content["answer"], str):
                return content["answer"]
            return json.dumps(content)
        return content
