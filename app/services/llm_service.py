from ollama import chat


class LLMService:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name

    def generate(self, query, contexts):
        combined_context = "\n".join(contexts)

        prompt = f"""
You are answering strictly based on the context below.

Context:
{combined_context}

Question:
{query}

Answer:
"""

        response = chat(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        return response["message"]["content"]
