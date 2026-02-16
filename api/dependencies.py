"""
api/dependencies.py
Dependency builder for constructing the enterprise agent stack.
"""

from app.infra.retry_policy import RetryPolicy
from app.infra.timeout_executor import TimeoutExecutor
from app.infra.reliable_executor import ReliableExecutor
from app.infra.logger import StructuredLogger

from app.registry.tool_registry import ToolRegistry
from app.routing.intelligent_router import IntelligentRouter
from app.services.planning_agent_service import PlanningAgentService

from app.tools.rag_search_tool import RAGSearchTool
from app.tools.web_search_tool import WebSearchTool

from app.services.embedding_service import EmbeddingService
from app.core.vector_store import VectorStore
from app.services.retriever_service import RetrieverService


DATA_PATH = "data/sample.txt"
STORE_PATH = "data/vector_store.pkl"


def build_agent() -> PlanningAgentService:
    """
    Builds and wires the full enterprise agent stack.
    """

    logger = StructuredLogger()

    # Reliability Layer
    retry_policy = RetryPolicy(max_retries=2, base_delay=0.5, backoff_factor=2)
    timeout_executor = TimeoutExecutor(timeout_seconds=10)
    reliable_executor = ReliableExecutor(
        retry_policy=retry_policy,
        timeout_executor=timeout_executor
    )

    # Tool Registry
    registry = ToolRegistry()

    # ------------------------------
    # RAG Tool Setup
    # ------------------------------
    embedding_service = EmbeddingService()
    vector_store = VectorStore(DATA_PATH, STORE_PATH, embedding_service.model)
    retriever = RetrieverService(vector_store)

    rag_tool = RAGSearchTool(retriever)
    registry.register(rag_tool)

    # ------------------------------
    # Web Search Tool Setup
    # ------------------------------
    web_tool = WebSearchTool()
    registry.register(web_tool)

    # Router
    router = IntelligentRouter(
        registry=registry,
        reliable_executor=reliable_executor,
        logger=logger,
        similarity_threshold=0.50
    )

    # Planner
    agent = PlanningAgentService(
        tool_registry=registry,
        router=router,
        logger=logger
    )

    return agent
