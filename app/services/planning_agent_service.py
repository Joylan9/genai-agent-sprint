"""
services/planning_agent_service.py
Planner service: creates JSON-structured plans via LLM, validates/repairs JSON,
delegates step execution to the router, and synthesizes a final answer.
"""

from typing import Optional, List, Dict, Any
from ollama import chat
import json
import re
import time

from infra.logger import StructuredLogger, generate_request_id
from registry.tool_registry import ToolRegistry
from routing.intelligent_router import IntelligentRouter


class PlanningAgentService:
    def __init__(
        self,
        model_name: str = "llama3",
        tool_registry: Optional[ToolRegistry] = None,
        router: Optional[IntelligentRouter] = None,
        logger: Optional[StructuredLogger] = None,
        max_json_retries: int = 2
    ):
        self.model_name = model_name
        self.registry = tool_registry
        self.router = router
        self.logger = logger
        self.max_json_retries = max_json_retries

    # ============================================================
    # STEP 1: JSON-STRUCTURED PLAN CREATION
    # ============================================================
    def create_plan(self, goal: str) -> str:
        available_tools = ", ".join(self.registry.list_tools() if self.registry else [])

        messages = [
            {
                "role": "system",
                "content": f"""
You are a planning agent.

You ONLY have access to these tools:
{available_tools}

Return a valid JSON object with this structure:

{{
  "steps": [
    {{"tool": "<tool_name>", "query": "<query1>"}}
  ]
}}

Rules:
- Use only listed tool names.
- Return ONLY valid JSON.
- No markdown.
- No explanations.
"""
            },
            {"role": "user", "content": goal}
        ]

        response = chat(model=self.model_name, messages=messages)
        return response["message"]["content"]

    # ============================================================
    # STEP 2: STRICT JSON PARSING
    # ============================================================
    def parse_plan_json(self, plan_text: str) -> List[Dict[str, Any]]:
        def extract_json(text: str) -> Optional[str]:
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
                    if "tool" not in step or "query" not in step:
                        raise ValueError("Each step must have 'tool' and 'query'.")

                    if self.registry and step["tool"] not in self.registry.list_tools():
                        raise ValueError(f"Unknown tool: {step['tool']}")

                return plan["steps"]

            except Exception as e:
                # Log parse attempt failure
                if self.logger:
                    self.logger.log("plan_parse_attempt_failed", {
                        "error": str(e),
                        "attempt": attempt,
                        "current_text_preview": (current_text[:500] + "...") if len(current_text) > 500 else current_text
                    })

                if attempt >= self.max_json_retries:
                    raise ValueError(f"Plan parsing failed: {e}")

                # Ask LLM to repair JSON
                repair_prompt = f"""
Fix this malformed JSON. Return ONLY valid JSON:

{current_text}
"""
                repair_response = chat(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a JSON repair assistant. Fix the JSON and return only the JSON."},
                        {"role": "user", "content": repair_prompt}
                    ]
                )
                current_text = repair_response["message"]["content"]
                attempt += 1

        raise ValueError("JSON parsing failure.")

    # ============================================================
    # STEP 3: ROUTER-BASED EXECUTION
    # ============================================================
    def execute_plan(self, goal: str, plan_text: str) -> str:
        request_id = generate_request_id()
        start = time.time()

        if self.logger:
            self.logger.log("request_started", {"request_id": request_id, "goal_preview": (goal[:300] + "...") if len(goal) > 300 else goal})

        try:
            steps = self.parse_plan_json(plan_text)
        except ValueError as e:
            if self.logger:
                self.logger.log("request_failed_plan_parse", {"request_id": request_id, "error": str(e)})
            return f"❌ Plan parsing failed: {e}"

        if not self.registry:
            if self.logger:
                self.logger.log("request_failed_no_registry", {"request_id": request_id})
            return "❌ Tool registry not configured."

        observations: List[Dict[str, Any]] = []

        if self.logger:
            self.logger.log("execution_started", {"request_id": request_id, "num_steps": len(steps)})

        for index, step in enumerate(steps):
            tool_name = step.get("tool")
            query = step.get("query")

            if self.logger:
                self.logger.log("step_started", {"request_id": request_id, "step": index + 1, "tool": tool_name, "query_preview": (query[:200] + "...") if query and len(query) > 200 else query})

            # Delegate execution to router if present, otherwise call tool directly
            if self.router:
                response = self.router.execute(step, request_id=request_id)
            else:
                tool = self.registry.get(tool_name)
                response = tool.execute(step)

            # Ensure structured response
            response.setdefault("metadata", {})
            observations.append({
                "step": index + 1,
                "tool": tool_name,
                "query": query,
                "response": response
            })

            if self.logger:
                self.logger.log("step_completed", {
                    "request_id": request_id,
                    "step": index + 1,
                    "tool": tool_name,
                    "status": response.get("status"),
                    "metadata": response.get("metadata", {})
                })

            # Optional: if a step returns a fatal error, decide to stop early (policy decision).
            # For now, we continue and include the error in final synthesis.

        total_time = time.time() - start

        if self.logger:
            self.logger.log("execution_finished", {"request_id": request_id, "total_time": total_time, "num_observations": len(observations)})

        # Synthesize final answer
        final = self.synthesize_answer(goal, observations)

        if self.logger:
            self.logger.log("request_completed", {"request_id": request_id, "duration": time.time() - start})

        return final

    # ============================================================
    # STEP 4: FINAL SYNTHESIS
    # ============================================================
    def synthesize_answer(self, goal: str, observations: List[Dict[str, Any]]) -> str:
        observation_text = ""
        for obs in observations:
            data = obs.get("response", {}).get("data", "")
            status = obs.get("response", {}).get("status", "unknown")
            observation_text += (
                f"\nStep {obs['step']} ({obs['tool']} - {obs['query']}):\n"
                f"status: {status}\n"
                f"{data}\n"
            )

        if self.logger:
            self.logger.log("synthesis_requested", {"observations_count": len(observations)})

        messages = [
            {
                "role": "system",
                "content": """
You are a summarization agent.

Using ONLY the provided observations,
produce a complete final answer.
Do not invent information.
"""
            },
            {
                "role": "user",
                "content": f"Goal:\n{goal}\n\nObservations:\n{observation_text}"
            }
        ]

        response = chat(model=self.model_name, messages=messages)
        final_answer = response["message"]["content"]

        if self.logger:
            self.logger.log("synthesis_completed", {"length": len(final_answer)})

        return final_answer
