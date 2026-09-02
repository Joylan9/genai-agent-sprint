from pathlib import Path

from app.config.runtime import web_search_available
from app.core.vector_store import VectorStore
from app.infra.logger import StructuredLogger
from app.infra.reliable_executor import ReliableExecutor
from app.infra.retry_policy import RetryPolicy
from app.infra.timeout_executor import TimeoutExecutor
from app.registry.tool_registry import ToolRegistry
from app.routing.intelligent_router import IntelligentRouter
from app.services.embedding_service import EmbeddingService
from app.services.planning_agent_service import PlanningAgentService
from app.services.retriever_service import RetrieverService
from app.tools.rag_search_tool import RAGSearchTool
from app.tools.web_search_tool import WebSearchTool


BACKEND_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = str(BACKEND_ROOT / "data" / "sample.txt")
STORE_PATH = str(BACKEND_ROOT / "data" / "vector_store.pkl")


def build_agent():
    logger = StructuredLogger()

    retry_policy = RetryPolicy(max_retries=2, base_delay=0.5, backoff_factor=2)
    timeout_executor = TimeoutExecutor(timeout_seconds=10)
    reliable_executor = ReliableExecutor(
        retry_policy=retry_policy,
        timeout_executor=timeout_executor,
    )

    registry = ToolRegistry()

    embedding_service = EmbeddingService()
    vector_store = VectorStore(DATA_PATH, STORE_PATH, embedding_service.model)
    retriever = RetrieverService(vector_store)
    registry.register(
        RAGSearchTool(
            embedding_service=embedding_service,
            retriever=retriever,
        )
    )

    if web_search_available():
        registry.register(WebSearchTool())

    router = IntelligentRouter(
        registry=registry,
        reliable_executor=reliable_executor,
        logger=logger,
        similarity_threshold=0.50,
    )

    return PlanningAgentService(
        tool_registry=registry,
        router=router,
        logger=logger,
    )
