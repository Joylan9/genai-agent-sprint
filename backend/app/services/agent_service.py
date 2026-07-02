from ..infra.ollama_client import get_ollama_client, get_ollama_model, llm_chat


class AgentService:
    def __init__(self, model_name=None, tool=None):
        self.model_name = model_name or get_ollama_model()
        self.client = get_ollama_client()
        self.tool = tool

    def run(self, goal, max_iterations=5):
        messages = [
            {
                "role": "system",
                "content": """
You are an intelligent agent.

You must respond in ONE of these formats:

1)
Action: search
Action Input: <query>

OR

2)
Final Answer: <answer>

Do not say anything else.
"""
            },
            {"role": "user", "content": goal}
        ]

        for _ in range(max_iterations):

            response = llm_chat(
                self.client,
                model=self.model_name,
                messages=messages,
                options={"num_ctx": 4096}
            )

            output = response["message"]["content"]
            print("\nAgent Output:\n", output)

            # CASE 1: Final Answer
            if "Final Answer:" in output:
                return output

            # CASE 2: Tool Action
            if "Action:" in output:

                # Safer parsing
                lines = output.split("\n")

                action = None
                action_input = None

                for line in lines:
                    if line.startswith("Action:"):
                        action = line.replace("Action:", "").strip()
                    if line.startswith("Action Input:"):
                        action_input = line.replace("Action Input:", "").strip()

                if not action or not action_input:
                    print("⚠️ Invalid agent format. Retrying...")
                    continue

                if action == "search" and self.tool:
                    observation = self.tool.search(action_input)

                    # Add assistant action to history
                    messages.append(
                        {"role": "assistant", "content": output}
                    )

                    # Feed tool result back
                    messages.append(
                        {"role": "user", "content": f"Observation: {observation}"}
                    )

                    continue

        return "Agent stopped without producing a final answer."
