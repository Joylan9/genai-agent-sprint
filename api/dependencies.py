from infra.retry_policy import RetryPolicy
from infra.timeout_executor import TimeoutExecutor
from infra.reliable_executor import ReliableExecutor
from infra.logger import StructuredLogger

from registry.tool_registry import ToolRegistry
from routing.intelligent_router import IntelligentRouter
from services.planning_agent_service import PlanningAgentService

from tools.rag_tool import RAGSearchTool
from tools.web_tool import WebSearchTool
from services.embedding_service import EmbeddingService
from core.vector_store import VectorStore
from services.retriever_service import RetrieverService


DATA_PATH = "data/sample.txt"
STORE_PATH = "data/vector_store.pkl"


def build_agent():
    logger = StructuredLogger()

    retry_policy = RetryPolicy(max_retries=2)
    timeout_executor = TimeoutExecutor(timeout_seconds=10)
    reliable_executor = ReliableExecutor(retry_policy, timeout_executor)

    registry = ToolRegistry()

    # RAG
    embedding_service = EmbeddingService()
    vector_store = VectorStore(DATA_PATH, STORE_PATH, embedding_service.model)
    retriever = RetrieverService(vector_store)
    registry.register(RAGSearchTool(retriever))

    # Web
    registry.register(WebSearchTool())

    router = IntelligentRouter(
        registry=registry,
        reliable_executor=reliable_executor,
        logger=logger
    )

    agent = PlanningAgentService(
        tool_registry=registry,
        router=router,
        logger=logger
    )

    return agent
