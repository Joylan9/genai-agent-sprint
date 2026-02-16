"""
planning_agent_main.py
Entry point wiring: constructs infra components, registry, router and planner,
and runs an interactive command-line session.
"""

import sys
import traceback

from infra.validators import InputValidator
from registry.tool_registry import ToolRegistry
from routing.intelligent_router import IntelligentRouter
from services.planning_agent_service import PlanningAgentService

from infra.retry_policy import RetryPolicy
from infra.timeout_executor import TimeoutExecutor
from infra.reliable_executor import ReliableExecutor
from infra.logger import StructuredLogger

from tools.rag_tool import RAGSearchTool
from tools.web_tool import WebSearchTool

from services.embedding_service import EmbeddingService
from core.vector_store import VectorStore
from services.retriever_service import RetrieverService


DATA_PATH = "data/sample.txt"
STORE_PATH = "data/vector_store.pkl"


def initialize_registry(logger: StructuredLogger) -> ToolRegistry:
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
        logger.log("tool_registered", {"tool": "rag_search"})
        print("• RAG tool registered.")

    except Exception as e:
        logger.log("tool_registration_failed", {"tool": "rag_search", "error": str(e)})
        print("⚠️ RAG initialization failed:", e)

    # ------------------------------
    # Web Tool
    # ------------------------------
    try:
        web_tool = WebSearchTool()
        registry.register(web_tool)
        logger.log("tool_registered", {"tool": "web_search"})
        print("• Web search tool registered.")

    except Exception as e:
        logger.log("tool_registration_failed", {"tool": "web_search", "error": str(e)})
        print("⚠️ Web tool initialization failed:", e)

    return registry


def main():
    try:
        print("🔄 Initializing system (enterprise agent)...")

        # infra components
        logger = StructuredLogger()
        retry_policy = RetryPolicy(max_retries=2, base_delay=0.5, backoff_factor=2)
        timeout_executor = TimeoutExecutor(timeout_seconds=10)
        reliable_executor = ReliableExecutor(retry_policy=retry_policy, timeout_executor=timeout_executor)

        # registry + tools
        registry = initialize_registry(logger)

        if not registry.list_tools():
            logger.log("startup_no_tools", {"msg": "No tools registered; exiting"})
            print("❌ No tools registered.")
            return

        # router + planner
        router = IntelligentRouter(
            registry=registry,
            reliable_executor=reliable_executor,
            logger=logger,
            similarity_threshold=0.50
        )

        agent = PlanningAgentService(
            tool_registry=registry,
            router=router,
            logger=logger
        )

        print("✅ System ready.\n")

        # --------------------------
        # CLI input with validation
        # --------------------------
        raw_goal = input("Enter complex goal: ")

        try:
            goal = InputValidator.validate_goal(raw_goal)
        except ValueError as e:
            logger.log("invalid_input", {"error": str(e)})
            print(f"❌ Invalid input: {e}")
            return

        # Generate & run plan
        print("\n--- Generating Plan ---")
        plan = agent.create_plan(goal)
        print(plan)

        print("\n--- Executing Plan ---")
        result = agent.execute_plan(goal, plan)

        print("\n--- Final Result ---")
        print(result)

    except Exception:
        logger = locals().get("logger", None)
        if logger:
            logger.log("fatal_error", {"error": traceback.format_exc()})
        print("❌ Unexpected system error occurred.")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
