from ollama import chat
import json


class PlanningAgentService:
    def __init__(self, model_name="llama3", tool=None):
        self.model_name = model_name
        self.tool = tool

    # ---------------------------------------
    # STEP 1: JSON-STRUCTURED PLAN CREATION
    # ---------------------------------------
    def create_plan(self, goal):
        messages = [
            {
                "role": "system",
                "content": """
You are a planning agent.

You ONLY have access to:
- search

Return a valid JSON object with this exact structure:

{
  "steps": [
    {"tool": "search", "query": "<query1>"},
    {"tool": "search", "query": "<query2>"}
  ]
}

Rules:
- Return ONLY valid JSON.
- No explanations.
- No markdown.
- No extra text.
"""
            },
            {"role": "user", "content": goal}
        ]

        response = chat(
            model=self.model_name,
            messages=messages
        )

        return response["message"]["content"]

    # ---------------------------------------
    # STEP 2: STRICT JSON VALIDATION
    # ---------------------------------------
    def parse_plan_json(self, plan_text):
        try:
            plan = json.loads(plan_text)

            if "steps" not in plan:
                raise ValueError("Missing 'steps' key")

            if not isinstance(plan["steps"], list):
                raise ValueError("'steps' must be a list")

            for step in plan["steps"]:
                if "tool" not in step or "query" not in step:
                    raise ValueError("Each step must contain 'tool' and 'query'")
                if step["tool"] != "search":
                    raise ValueError(f"Unsupported tool: {step['tool']}")

            return plan["steps"]

        except Exception as e:
            raise ValueError(f"Invalid plan JSON: {e}")

    # ---------------------------------------
    # STEP 3: DETERMINISTIC EXECUTION
    # ---------------------------------------
    def execute_plan(self, goal, plan_text):
        try:
            steps = self.parse_plan_json(plan_text)
        except ValueError as e:
            return f"Plan parsing failed: {e}"

        if not self.tool:
            return "No tool available."

        observations = []

        print("\n--- Executing Structured Plan ---")

        for index, step in enumerate(steps):
            query = step["query"]

            print(f"\nExecuting Step {index + 1}: search -> {query}")

            try:
                result = self.tool.search(query)
            except Exception as e:
                result = f"Tool execution failed: {e}"

            print("Observation preview:", result[:300], "...")

            observations.append({
                "step": index + 1,
                "query": query,
                "result": result
            })

        return self.synthesize_answer(goal, observations)

    # ---------------------------------------
    # STEP 4: FINAL SYNTHESIS
    # ---------------------------------------
    def synthesize_answer(self, goal, observations):
        observation_text = ""

        for obs in observations:
            observation_text += (
                f"\nStep {obs['step']} ({obs['query']}):\n"
                f"{obs['result']}\n"
            )

        messages = [
            {
                "role": "system",
                "content": """
You are a summarization agent.

Using ONLY the provided observations,
produce a complete final answer to the goal.
"""
            },
            {
                "role": "user",
                "content": f"Goal:\n{goal}\n\nObservations:\n{observation_text}"
            }
        ]

        response = chat(
            model=self.model_name,
            messages=messages
        )

        return response["message"]["content"]
