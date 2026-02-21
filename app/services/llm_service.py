from ..infra.ollama_client import get_ollama_client, get_ollama_model, llm_chat


class LLMService:
    def __init__(self, model_name=None):
        self.model_name = model_name or get_ollama_model()
        self.client = get_ollama_client()

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

        response = llm_chat(
            self.client,
            model=self.model_name,
            messages=messages,
            options={"num_ctx": 4096}
        )

        return response["message"]["content"]
