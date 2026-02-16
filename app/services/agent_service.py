from ollama import chat


class AgentService:
    def __init__(self, model_name="llama3", tool=None):
        self.model_name = model_name
        self.tool = tool

    def run(self, goal, max_iterations=5):
        messages = [
            {
                "role": "system",
                "content": """
You are an intelligent agent.
You can either:
1. Respond with: Action: search
   Action Input: <query>
OR
2. Respond with: Final Answer: <answer>

Only use these formats.
"""
            },
            {"role": "user", "content": goal}
        ]

        for _ in range(max_iterations):

            response = chat(
                model=self.model_name,
                messages=messages
            )

            output = response["message"]["content"]
            print("\nAgent Output:\n", output)

            if "Final Answer:" in output:
                return output

            if "Action:" in output:
                lines = output.split("\n")
                action = lines[0].split(":")[1].strip()
                action_input = lines[1].split(":")[1].strip()

                if action == "search" and self.tool:
                    observation = self.tool.search(action_input)

                    messages.append(
                        {"role": "assistant", "content": output}
                    )

                    messages.append(
                        {"role": "user", "content": f"Observation: {observation}"}
                    )

        return "Agent stopped without final answer."
