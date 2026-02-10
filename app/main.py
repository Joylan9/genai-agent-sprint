from services.embedding_service import EmbeddingService
from core.vector_store import VectorStore
from services.retriever_service import RetrieverService
from services.llm_service import LLMService


DATA_PATH = "data/sample.txt"
STORE_PATH = "data/vector_store.pkl"


def main():
    embedding_service = EmbeddingService()
    vector_store = VectorStore(DATA_PATH, STORE_PATH, embedding_service.model)
    retriever = RetrieverService(vector_store)
    llm_service = LLMService()

    print("System ready. Type 'exit' to quit.\n")

    while True:
        question = input("Ask a question: ")

        if question.lower() == "exit":
            break

        query_embedding = embedding_service.encode([question])[0]
        contexts = retriever.retrieve(query_embedding)

        print("\nRetrieved Context:")
        for ctx in contexts:
            print("-", ctx)

        answer = llm_service.generate(question, contexts)

        print("\nAI Answer:\n", answer)
        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()
