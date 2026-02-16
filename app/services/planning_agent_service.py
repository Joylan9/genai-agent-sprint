from ollama import chat
import re


class PlanningAgentService:
    def __init__(self, model_name="llama3", tool=None):
        self.model_name = model_name
        self.tool = tool

    # ----------------------------
    # STEP 1: TOOL-AWARE PLANNING
    # ----------------------------
    def create_plan(self, goal):
        messages = [
            {
                "role": "system",
                "content": """
You are a planning agent.

You ONLY have access to this tool:
- search

Create a short numbered plan.
Each step MUST require using the search tool.
Keep it practical and executable.

Return only numbered steps.
"""
            },
            {"role": "user", "content": goal}
        ]

        response = chat(
            model=self.model_name,
            messages=messages
        )

        return response["message"]["content"]

    # ----------------------------
    # STEP 2: PARSE PLAN INTO STEPS
    # ----------------------------
    def parse_plan(self, plan_text):
        steps = re.findall(r"\d+\.\s*(.*)", plan_text)
        return steps

    # ----------------------------
    # STEP 3: ENTERPRISE EXECUTION
    # ----------------------------
    def execute_plan(self, goal, plan):

        steps = self.parse_plan(plan)

        if not steps:
            return "Invalid plan structure."

        observations = []

        print("\n--- Executing Plan Deterministically ---")

        for index, step in enumerate(steps):
            print(f"\nExecuting Step {index + 1}: {step}")

            # Extract search query from step
            query = step.lower().replace("search for", "").strip()

            if not self.tool:
                return "No tool available."

            result = self.tool.search(query)

            print("Observation:", result)

            observations.append(f"Step {index + 1}: {result}")

        # ----------------------------
        # STEP 4: FINAL SYNTHESIS
        # ----------------------------
        return self.synthesize_answer(goal, observations)

    # ----------------------------
    # STEP 5: FINAL ANSWER GENERATION
    # ----------------------------
    def synthesize_answer(self, goal, observations):

        combined_observations = "\n".join(observations)

        messages = [
            {
                "role": "system",
                "content": """
You are a summarization agent.

Based only on the provided observations,
produce a complete final answer to the goal.
"""
            },
            {
                "role": "user",
                "content": f"Goal:\n{goal}\n\nObservations:\n{combined_observations}"
            }
        ]

        response = chat(
            model=self.model_name,
            messages=messages
        )

        return response["message"]["content"]
