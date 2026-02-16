from ollama import chat


class LLMService:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name

    def generate(self, query, contexts, memory_history):
        combined_context = "\n".join(contexts)

        system_prompt = f"""
You are answering strictly based on the context below.

Context:
{combined_context}
"""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(memory_history)
        messages.append({"role": "user", "content": query})

        response = chat(
            model=self.model_name,
            messages=messages
        )

        return response["message"]["content"]
