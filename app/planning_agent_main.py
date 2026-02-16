from services.planning_agent_service import PlanningAgentService
from services.rag_search_tool import RAGSearchTool
from services.embedding_service import EmbeddingService
from core.vector_store import VectorStore
from services.retriever_service import RetrieverService


DATA_PATH = "data/sample.txt"
STORE_PATH = "data/vector_store.pkl"


def main():
    embedding_service = EmbeddingService()
    vector_store = VectorStore(DATA_PATH, STORE_PATH, embedding_service.model)
    retriever = RetrieverService(vector_store)

    rag_tool = RAGSearchTool(embedding_service, retriever)

    agent = PlanningAgentService(tool=rag_tool)

    goal = input("Enter complex goal: ")

    print("\n--- Generating Plan ---")
    plan = agent.create_plan(goal)
    print(plan)

    print("\n--- Executing Plan ---")
    result = agent.execute_plan(goal, plan)

    print("\nFinal Result:\n", result)


if __name__ == "__main__":
    main()
