import sys
import traceback

from services.planning_agent_service import PlanningAgentService
from services.rag_search_tool import RAGSearchTool
from services.embedding_service import EmbeddingService
from core.vector_store import VectorStore
from services.retriever_service import RetrieverService


DATA_PATH = "data/sample.txt"
STORE_PATH = "data/vector_store.pkl"


def main():
    try:
        print("🔄 Initializing system...")

        # ----------------------------
        # Initialize Core Components
        # ----------------------------
        embedding_service = EmbeddingService()
        vector_store = VectorStore(DATA_PATH, STORE_PATH, embedding_service.model)
        retriever = RetrieverService(vector_store)

        rag_tool = RAGSearchTool(embedding_service, retriever)

        agent = PlanningAgentService(tool=rag_tool)

        print("✅ System ready.\n")

        # ----------------------------
        # Get Goal Input (Validated)
        # ----------------------------
        goal = input("Enter complex goal: ").strip()

        if not goal:
            print("❌ Goal cannot be empty. Exiting.")
            return

        # Optional: Basic domain validation
        if len(goal) < 5:
            print("❌ Goal too short. Provide a meaningful objective.")
            return

        # ----------------------------
        # Planning Phase
        # ----------------------------
        print("\n--- Generating Plan ---")
        plan = agent.create_plan(goal)

        if not plan or "Unsupported goal domain" in plan:
            print("❌ Planner could not generate valid plan.")
            return

        print(plan)

        # ----------------------------
        # Execution Phase
        # ----------------------------
        print("\n--- Executing Plan ---")
        result = agent.execute_plan(goal, plan)

        print("\n--- Final Result ---")
        print(result)

    except FileNotFoundError as e:
        print(f"❌ File error: {e}")
    except Exception as e:
        print("❌ Unexpected system error occurred.")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
