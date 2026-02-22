"""
tests/test_router.py
Unit tests for the IntelligentRouter.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

from app.routing.intelligent_router import IntelligentRouter


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_registry():
    reg = MagicMock()
    reg.list_tools.return_value = ["rag_search", "web_search"]

    rag_tool = MagicMock()
    rag_tool.name = "rag_search"
    web_tool = MagicMock()
    web_tool.name = "web_search"

    def _get(name):
        return {"rag_search": rag_tool, "web_search": web_tool}[name]
    reg.get = MagicMock(side_effect=_get)

    return reg


@pytest.fixture
def mock_executor():
    executor = MagicMock()
    # Default: successful execution
    executor.execute = MagicMock(return_value={
        "status": "success",
        "data": "result data",
        "metadata": {"similarity": 0.85},
    })
    return executor


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def router(mock_registry, mock_executor, mock_logger):
    return IntelligentRouter(
        registry=mock_registry,
        reliable_executor=mock_executor,
        logger=mock_logger,
        similarity_threshold=0.50,
    )


# ===========================================================================
# Tests
# ===========================================================================

class TestRouterExecution:

    @pytest.mark.asyncio
    async def test_normal_execution(self, router, mock_executor):
        """Tool executes normally and router returns result."""
        step = {"tool": "rag_search", "query": "what is RAG?"}
        result = await router.execute(step, request_id="test-123")

        assert result["status"] == "success"
        assert result["data"] == "result data"
        assert result["metadata"]["requested_tool"] == "rag_search"
        mock_executor.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_missing_tool_returns_error(self, router):
        """Step without 'tool' key returns error."""
        step = {"query": "no tool"}
        result = await router.execute(step)

        assert result["status"] == "error"
        assert "Missing 'tool'" in result["metadata"]["error"]

    @pytest.mark.asyncio
    async def test_tool_not_found_returns_error(self, router, mock_registry):
        """Unknown tool name returns error."""
        mock_registry.get = MagicMock(
            side_effect=KeyError("unknown_tool")
        )
        step = {"tool": "unknown_tool", "query": "test"}
        result = await router.execute(step, request_id="test-456")

        assert result["status"] == "error"
        assert "Tool not found" in result["metadata"]["error"]


class TestRouterFallback:

    @pytest.mark.asyncio
    async def test_failure_based_fallback_to_web_search(
        self, router, mock_executor, mock_registry
    ):
        """When primary tool fails, router falls back to web_search."""
        # First call (primary) fails, second call (fallback) succeeds
        mock_executor.execute = MagicMock(side_effect=[
            {
                "status": "error",
                "data": None,
                "metadata": {"error": "RAG failed"},
            },
            {
                "status": "success",
                "data": "web search result",
                "metadata": {},
            },
        ])
        step = {"tool": "rag_search", "query": "test fallback"}
        result = await router.execute(step, request_id="test-789")

        assert result["status"] == "success"
        assert result["data"] == "web search result"
        assert result["metadata"]["fallback_from"] == "rag_search"

    @pytest.mark.asyncio
    async def test_rag_low_confidence_fallback(
        self, router, mock_executor, mock_registry
    ):
        """When RAG returns low similarity, router falls back to web_search."""
        # Primary RAG returns low similarity
        mock_executor.execute = MagicMock(side_effect=[
            {
                "status": "success",
                "data": "low quality result",
                "metadata": {"similarity": 0.3},
            },
            {
                "status": "success",
                "data": "web search result",
                "metadata": {},
            },
        ])
        step = {"tool": "rag_search", "query": "obscure topic"}
        result = await router.execute(step, request_id="test-low")

        assert result["status"] == "success"
        assert result["data"] == "web search result"
        assert result["metadata"]["fallback_from"] == "rag_search"

    @pytest.mark.asyncio
    async def test_no_fallback_for_web_search_failure(
        self, router, mock_executor
    ):
        """When web_search itself fails, no double-fallback occurs."""
        mock_executor.execute = MagicMock(return_value={
            "status": "error",
            "data": None,
            "metadata": {"error": "SerpAPI down"},
        })
        step = {"tool": "web_search", "query": "test"}
        result = await router.execute(step, request_id="test-ws")

        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_rag_high_confidence_no_fallback(
        self, router, mock_executor
    ):
        """When RAG has high similarity, no fallback happens."""
        mock_executor.execute = MagicMock(return_value={
            "status": "success",
            "data": "high quality RAG result",
            "metadata": {"similarity": 0.92},
        })
        step = {"tool": "rag_search", "query": "well-known topic"}
        result = await router.execute(step, request_id="test-high")

        assert result["status"] == "success"
        assert result["data"] == "high quality RAG result"
        assert "fallback_from" not in result.get("metadata", {})
