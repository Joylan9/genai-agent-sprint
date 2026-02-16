from ollama import chat
import json
import re


class PlanningAgentService:
    def __init__(
        self,
        model_name="llama3",
        tool_registry=None,
        router=None,
        max_json_retries=2
    ):
        self.model_name = model_name
        self.registry = tool_registry
        self.router = router
        self.max_json_retries = max_json_retries

    # ============================================================
    # STEP 1: JSON-STRUCTURED PLAN CREATION
    # ============================================================
    def create_plan(self, goal):

        available_tools = ", ".join(self.registry.list_tools())

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
    def parse_plan_json(self, plan_text):

        def extract_json(text):
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

                    if step["tool"] not in self.registry.list_tools():
                        raise ValueError(f"Unknown tool: {step['tool']}")

                return plan["steps"]

            except Exception as e:
                if attempt >= self.max_json_retries:
                    raise ValueError(f"Plan parsing failed: {e}")

                repair_prompt = f"""
Fix this malformed JSON. Return ONLY valid JSON:

{current_text}
"""

                repair_response = chat(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You fix JSON."},
                        {"role": "user", "content": repair_prompt}
                    ]
                )

                current_text = repair_response["message"]["content"]
                attempt += 1

        raise ValueError("JSON parsing failure.")

    # ============================================================
    # STEP 3: ROUTER-BASED EXECUTION
    # ============================================================
    def execute_plan(self, goal, plan_text):

        try:
            steps = self.parse_plan_json(plan_text)
        except ValueError as e:
            return f"❌ Plan parsing failed: {e}"

        if not self.registry:
            return "❌ Tool registry not configured."

        observations = []

        print("\n--- Executing Structured Plan ---")

        for index, step in enumerate(steps):

            print(f"\nStep {index + 1}: {step['tool']} -> {step['query']}")

            if self.router:
                response = self.router.execute(step)
            else:
                tool = self.registry.get(step["tool"])
                response = tool.execute(step)

            observations.append({
                "step": index + 1,
                "tool": step["tool"],
                "query": step["query"],
                "response": response
            })

        return self.synthesize_answer(goal, observations)

    # ============================================================
    # STEP 4: FINAL SYNTHESIS
    # ============================================================
    def synthesize_answer(self, goal, observations):

        observation_text = ""

        for obs in observations:
            data = obs["response"].get("data", "")

            observation_text += (
                f"\nStep {obs['step']} ({obs['tool']} - {obs['query']}):\n"
                f"{data}\n"
            )

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
        return response["message"]["content"]
