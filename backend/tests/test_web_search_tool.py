import pytest

from app.infra.reliable_executor import ReliableExecutor
from app.tools.web_search_tool import WebSearchTool


@pytest.mark.asyncio
async def test_web_search_reports_unavailable_as_error(monkeypatch):
    monkeypatch.delenv("SERPAPI_KEY", raising=False)

    tool = WebSearchTool()
    result = await tool.execute({"query": "today technology news"})

    assert result["status"] == "error"
    assert result["data"] is None
    assert "SERPAPI_KEY" in result["metadata"]["error"]


@pytest.mark.asyncio
async def test_reliable_executor_preserves_tool_error_status():
    class NoRetry:
        async def execute(self, timeout_execute, tool_execute, step):
            return await tool_execute(step)

    class NoTimeout:
        async def execute(self, func, step):
            return await func(step)

    class ErrorTool:
        async def execute(self, step):
            return {"status": "error", "data": None, "metadata": {"error": "failed"}}

    executor = ReliableExecutor(NoRetry(), NoTimeout())
    result = await executor.execute(ErrorTool(), {"tool": "web_search", "query": "x"})

    assert result["status"] == "error"
    assert result["metadata"]["status"] == "error"
