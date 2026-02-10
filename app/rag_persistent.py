from sentence_transformers import SentenceTransformer
import numpy as np
from ollama import chat
import os
import pickle

# -------------------------------
# Configuration
# -------------------------------

DATA_PATH = "data/sample.txt"
EMBEDDING_FILE = "data/vector_store.pkl"

print("Loading embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# -------------------------------
# Indexing Phase (Only if needed)
# -------------------------------

def build_and_save_embeddings():
    print("Building embeddings...")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        document_text = f.read()

    documents = [chunk.strip() for chunk in document_text.split("\n") if chunk.strip()]
    embeddings = embedding_model.encode(documents)

    with open(EMBEDDING_FILE, "wb") as f:
        pickle.dump((documents, embeddings), f)

    print("Embeddings saved to disk.")
    return documents, embeddings


def load_embeddings():
    print("Loading embeddings from disk...")
    with open(EMBEDDING_FILE, "rb") as f:
        documents, embeddings = pickle.load(f)
    return documents, embeddings


# -------------------------------
# Startup Logic
# -------------------------------

if os.path.exists(EMBEDDING_FILE):
    documents, document_embeddings = load_embeddings()
else:
    documents, document_embeddings = build_and_save_embeddings()

print("System ready. Ask questions (type 'exit' to quit).\n")


# -------------------------------
# Retrieval Functions
# -------------------------------

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def retrieve_relevant_chunks(query, top_k=2):
    query_embedding = embedding_model.encode([query])[0]

    similarities = [
        cosine_similarity(query_embedding, doc_embedding)
        for doc_embedding in document_embeddings
    ]

    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return [documents[i] for i in top_indices]


def ask_llm_with_context(query, contexts):
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
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]


# -------------------------------
# Interactive Loop
# -------------------------------

while True:
    user_question = input("Ask a question: ")

    if user_question.lower() == "exit":
        print("Exiting system.")
        break

    contexts = retrieve_relevant_chunks(user_question)

    print("\nRetrieved Context:")
    for ctx in contexts:
        print("-", ctx)

    answer = ask_llm_with_context(user_question, contexts)

    print("\nAI Answer:\n", answer)
    print("\n" + "-" * 50 + "\n")
