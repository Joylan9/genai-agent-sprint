from ollama import chat

def ask_llm(prompt):
    response = chat(
        model="llama3",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response["message"]["content"]

if __name__ == "__main__":
    question = "Explain embeddings creatively using a cooking analogy."
    answer = ask_llm(question)
    print(answer)
