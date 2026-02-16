# api/dependencies.py

from app.registry.tool_registry import ToolRegistry
from app.routing.intelligent_router import IntelligentRouter
from app.services.planning_agent_service import PlanningAgentService

from app.services.embedding_service import EmbeddingService
from app.services.retriever_service import RetrieverService
from app.core.vector_store import VectorStore

from app.tools.rag_search_tool import RAGSearchTool
from app.tools.web_search_tool import WebSearchTool

from app.infra.retry_policy import RetryPolicy
from app.infra.timeout_executor import TimeoutExecutor
from app.infra.reliable_executor import ReliableExecutor
from app.infra.logger import StructuredLogger


DATA_PATH = "data/sample.txt"
STORE_PATH = "data/vector_store.pkl"


def build_agent():

    logger = StructuredLogger()

    # ------------------------
    # Infra
    # ------------------------
    retry_policy = RetryPolicy(max_retries=2, base_delay=0.5, backoff_factor=2)
    timeout_executor = TimeoutExecutor(timeout_seconds=10)
    reliable_executor = ReliableExecutor(
        retry_policy=retry_policy,
        timeout_executor=timeout_executor
    )

    # ------------------------
    # Registry
    # ------------------------
    registry = ToolRegistry()

    # ------------------------
    # RAG Tool Setup (FIXED)
    # ------------------------
    embedding_service = EmbeddingService()
    vector_store = VectorStore(DATA_PATH, STORE_PATH, embedding_service.model)
    retriever = RetrieverService(vector_store)

    rag_tool = RAGSearchTool(
        embedding_service=embedding_service,
        retriever=retriever
    )

    registry.register(rag_tool)

    # ------------------------
    # Web Tool Setup
    # ------------------------
    web_tool = WebSearchTool()
    registry.register(web_tool)

    # ------------------------
    # Router
    # ------------------------
    router = IntelligentRouter(
        registry=registry,
        reliable_executor=reliable_executor,
        logger=logger,
        similarity_threshold=0.50
    )

    # ------------------------
    # Planning Agent
    # ------------------------
    agent = PlanningAgentService(
        tool_registry=registry,
        router=router,
        logger=logger
    )

    return agent
