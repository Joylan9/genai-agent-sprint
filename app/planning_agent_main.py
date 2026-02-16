"""
app/planning_agent_main.py
Enterprise CLI entrypoint.
"""

import sys
import traceback

from .infra.validators import InputValidator
from .registry.tool_registry import ToolRegistry
from .routing.intelligent_router import IntelligentRouter
from .services.planning_agent_service import PlanningAgentService

from .infra.retry_policy import RetryPolicy
from .infra.timeout_executor import TimeoutExecutor
from .infra.reliable_executor import ReliableExecutor
from .infra.logger import StructuredLogger

from .tools.rag_search_tool import RAGSearchTool
from .tools.web_search_tool import WebSearchTool

from .services.embedding_service import EmbeddingService
from .core.vector_store import VectorStore
from .services.retriever_service import RetrieverService


DATA_PATH = "data/sample.txt"
STORE_PATH = "data/vector_store.pkl"


def initialize_registry(logger: StructuredLogger) -> ToolRegistry:
    registry = ToolRegistry()

    try:
        # ------------------------------
        # RAG Tool Setup
        # ------------------------------
        embedding_service = EmbeddingService()
        vector_store = VectorStore(DATA_PATH, STORE_PATH, embedding_service.model)
        retriever = RetrieverService(vector_store)

        rag_tool = RAGSearchTool(
            embedding_service=embedding_service,
            retriever=retriever,
        )

        registry.register(rag_tool)

        # ------------------------------
        # Web Tool Setup
        # ------------------------------
        web_tool = WebSearchTool()
        registry.register(web_tool)

        logger.log("tools_initialized", {"tools": registry.list_tools()})

    except Exception as e:
        logger.log("tool_initialization_failed", {"error": str(e)})
        raise

    return registry


def main():
    try:
        logger = StructuredLogger()

        # ------------------------------
        # Reliability Layer
        # ------------------------------
        retry_policy = RetryPolicy(max_retries=2, base_delay=0.5, backoff_factor=2)
        timeout_executor = TimeoutExecutor(timeout_seconds=10)
        reliable_executor = ReliableExecutor(
            retry_policy=retry_policy,
            timeout_executor=timeout_executor,
        )

        # ------------------------------
        # Registry + Router
        # ------------------------------
        registry = initialize_registry(logger)

        router = IntelligentRouter(
            registry=registry,
            reliable_executor=reliable_executor,
            logger=logger,
            similarity_threshold=0.50,
        )

        # ------------------------------
        # Planner
        # ------------------------------
        agent = PlanningAgentService(
            tool_registry=registry,
            router=router,
            logger=logger,
        )

        # ------------------------------
        # CLI Input
        # ------------------------------
        raw_goal = input("Enter complex goal: ")

        try:
            goal = InputValidator.validate_goal(raw_goal)
        except ValueError as e:
            logger.log("invalid_input", {"error": str(e)})
            print(f"❌ Invalid input: {e}")
            return

        print("\n--- Generating Plan ---")
        plan = agent.create_plan(goal)
        print(plan)

        print("\n--- Executing Plan ---")
        result = agent.execute_plan(goal, plan)

        print("\n--- Final Result ---")
        print(result)

    except Exception:
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
