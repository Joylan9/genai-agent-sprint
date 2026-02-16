import sys
import traceback

from services.planning_agent_service import PlanningAgentService
from registry.tool_registry import ToolRegistry
from routing.intelligent_router import IntelligentRouter

from tools.rag_tool import RAGSearchTool
from tools.web_tool import WebSearchTool

from services.embedding_service import EmbeddingService
from core.vector_store import VectorStore
from services.retriever_service import RetrieverService


DATA_PATH = "data/sample.txt"
STORE_PATH = "data/vector_store.pkl"


def initialize_registry():
    registry = ToolRegistry()

    # ------------------------------
    # RAG Tool
    # ------------------------------
    try:
        embedding_service = EmbeddingService()
        vector_store = VectorStore(DATA_PATH, STORE_PATH, embedding_service.model)
        retriever = RetrieverService(vector_store)

        rag_tool = RAGSearchTool(retriever)
        registry.register(rag_tool)

        print("• RAG tool registered.")

    except Exception as e:
        print("⚠️ RAG initialization failed:", e)

    # ------------------------------
    # Web Tool
    # ------------------------------
    try:
        web_tool = WebSearchTool()
        registry.register(web_tool)

        print("• Web search tool registered.")

    except Exception as e:
        print("⚠️ Web tool initialization failed:", e)

    return registry


def main():
    try:
        print("🔄 Initializing system (enterprise agent)...")

        registry = initialize_registry()

        if not registry.list_tools():
            print("❌ No tools registered.")
            return

        router = IntelligentRouter(registry, similarity_threshold=0.50)

        agent = PlanningAgentService(
            tool_registry=registry,
            router=router
        )

        print("✅ System ready.\n")

        goal = input("Enter complex goal: ").strip()

        if not goal:
            print("❌ Goal cannot be empty.")
            return

        print("\n--- Generating Plan ---")
        plan = agent.create_plan(goal)
        print(plan)

        print("\n--- Executing Plan ---")
        result = agent.execute_plan(goal, plan)

        print("\n--- Final Result ---")
        print(result)

    except Exception:
        print("❌ Unexpected system error occurred.")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
