from ollama import chat


class PlanningAgentService:
    def __init__(self, model_name="llama3", tool=None):
        self.model_name = model_name
        self.tool = tool

    def create_plan(self, goal):
        messages = [
            {
                "role": "system",
                "content": """
You are a planning agent.
Break the user goal into clear numbered steps.
Only return the plan.
"""
            },
            {"role": "user", "content": goal}
        ]

        response = chat(
            model=self.model_name,
            messages=messages
        )

        return response["message"]["content"]

    def execute_plan(self, goal, plan, max_iterations=5):

        messages = [
            {
                "role": "system",
                "content": """
You are an execution agent.

Follow the given plan step by step.

You may respond with:

Action: search
Action Input: <query>

OR

Final Answer: <answer>

Only use these formats.
"""
            },
            {"role": "user", "content": f"Goal:\n{goal}\n\nPlan:\n{plan}"}
        ]

        for _ in range(max_iterations):

            response = chat(
                model=self.model_name,
                messages=messages
            )

            output = response["message"]["content"]
            print("\nExecution Output:\n", output)

            if "Final Answer:" in output:
                return output

            if "Action:" in output:
                lines = output.split("\n")

                action = None
                action_input = None

                for line in lines:
                    if line.startswith("Action:"):
                        action = line.replace("Action:", "").strip()
                    if line.startswith("Action Input:"):
                        action_input = line.replace("Action Input:", "").strip()

                if not action or not action_input:
                    print("⚠️ Invalid format. Retrying...")
                    continue

                if action == "search" and self.tool:
                    observation = self.tool.search(action_input)

                    messages.append(
                        {"role": "assistant", "content": output}
                    )

                    messages.append(
                        {"role": "user", "content": f"Observation: {observation}"}
                    )

        return "Agent stopped without final answer."
