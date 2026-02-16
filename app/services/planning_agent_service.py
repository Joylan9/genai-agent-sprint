"""
app/services/planning_agent_service.py
Enterprise planning agent service.
"""

from typing import Optional, List, Dict, Any
from ollama import chat
import json
import re
import time

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

        response = chat(model=self.model_name, messages=messages)
        return response["message"]["content"]

    # ============================================================
    # JSON PARSING
    # ============================================================
    def parse_plan_json(self, plan_text: str) -> List[Dict[str, Any]]:
        def extract_json(text: str):
            match = re.search(r"\{.*\}", text, re.DOTALL)
            return match.group(0) if match else None

        attempt = 0
        current_text = plan_text

        while attempt <= self.max_json_retries:
            try:
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
                )

                current_text = repair_response["message"]["content"]
                attempt += 1

        raise ValueError("JSON parsing failure.")

    # ============================================================
    # EXECUTION
    # ============================================================
    def execute_plan(self, goal: str, plan_text: str) -> str:
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
            return f"❌ Plan parsing failed: {e}"

        if not self.registry:
            raise RuntimeError("Tool registry not configured.")

        observations = []

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

            if self.router:
                response = self.router.execute(step, request_id=request_id)
            else:
                tool = self.registry.get(step["tool"])
                response = tool.execute(step)

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

        return self.synthesize_answer(goal, observations)

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

        response = chat(model=self.model_name, messages=messages)
        return response["message"]["content"]
