from app.services.embedding_service import EmbeddingService
from app.core.vector_store import VectorStore
from app.services.retriever_service import RetrieverService
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService


DATA_PATH = "data/sample.txt"
STORE_PATH = "data/vector_store.pkl"


def main():
    # Initialize services
    embedding_service = EmbeddingService()
    vector_store = VectorStore(DATA_PATH, STORE_PATH, embedding_service.model)
    retriever = RetrieverService(vector_store)
    llm_service = LLMService()
    memory_service = MemoryService(max_messages=6)

    print("System ready. Type 'exit' to quit.\n")

    while True:
        question = input("Ask a question: ")

        if question.lower() == "exit":
            break

        # Step 1: Retrieve relevant context (RAG)
        query_embedding = embedding_service.encode([question])[0]
        contexts = retriever.retrieve(query_embedding)

        print("\nRetrieved Context:")
        for ctx in contexts:
            print("-", ctx)

        # Step 2: Add user question to memory
        memory_service.add_message("user", question)

        # Step 3: Generate response with memory + RAG context
        answer = llm_service.generate(
            question,
            contexts,
            memory_service.get_history()
        )

        # Step 4: Store assistant response in memory
        memory_service.add_message("assistant", answer)

        print("\nAI Answer:\n", answer)
        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()
