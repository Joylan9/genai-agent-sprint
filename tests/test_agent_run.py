"""
tests/test_agent_run.py
Smoke + functional tests for the FastAPI application.
"""

import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from httpx import AsyncClient, ASGITransport


# ---------------------------------------------------------------------------
# Helper: build a patched app for integration tests
# ---------------------------------------------------------------------------

def _make_mock_agent():
    """Build a mock PlanningAgentService that returns canned responses."""
    agent = MagicMock()
    agent.create_plan.return_value = json.dumps({
        "steps": [{"tool": "rag_search", "query": "test"}]
    })
    agent.execute_plan = AsyncMock(return_value={
        "result": "Mocked final answer for testing",
        "request_id": "test-request-id-001",
    })
    return agent


@pytest.fixture
async def patched_app(mock_mongodb, mock_ollama, mock_redis):
    """
    Create a FastAPI app with all external deps mocked.
    The startup_event runs with mocked MongoDB/Ollama/Redis.
    """
    # Patch build_agent to return our mock agent
    mock_agent = _make_mock_agent()
    with patch("api.app.build_agent", return_value=mock_agent):
        from api.app import app
        yield app, mock_agent


# ===========================================================================
# Health & Readiness Smoke Tests
# ===========================================================================

class TestHealthEndpoints:

    @pytest.mark.asyncio
    async def test_health_returns_200(self, patched_app):
        app, _ = patched_app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r = await ac.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert "status" in data

    @pytest.mark.asyncio
    async def test_metrics_returns_200(self, patched_app):
        app, _ = patched_app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r = await ac.get("/metrics")
        assert r.status_code == 200


# ===========================================================================
# Agent Run Tests
# ===========================================================================

class TestAgentRun:

    @pytest.mark.asyncio
    async def test_agent_run_requires_api_key(self, patched_app):
        """POST /agent/run without api key should return 401."""
        app, _ = patched_app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r = await ac.post(
                "/agent/run",
                json={"session_id": "test", "goal": "hello"},
            )
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_agent_run_happy_path(self, patched_app):
        """POST /agent/run with valid key returns result + request_id."""
        app, mock_agent = patched_app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r = await ac.post(
                "/agent/run",
                json={"session_id": "test-user", "goal": "Explain RAG simply"},
                headers={"x-api-key": "supersecretkey"},
            )
        assert r.status_code == 200
        data = r.json()
        assert "result" in data
        assert "request_id" in data
        assert data["result"] == "Mocked final answer for testing"

    @pytest.mark.asyncio
    async def test_agent_run_with_wrong_api_key(self, patched_app):
        """POST /agent/run with wrong key should return 401."""
        app, _ = patched_app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r = await ac.post(
                "/agent/run",
                json={"session_id": "test", "goal": "hello"},
                headers={"x-api-key": "wrong-key"},
            )
        assert r.status_code == 401


# ===========================================================================
# Trace Endpoint
# ===========================================================================

class TestTraceEndpoint:

    @pytest.mark.asyncio
    async def test_trace_not_found_returns_404(self, patched_app):
        """GET /traces/{id} for unknown trace returns 404."""
        app, _ = patched_app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r = await ac.get(
                "/traces/nonexistent-id",
                headers={"x-api-key": "supersecretkey"},
            )
        assert r.status_code == 404

    @pytest.mark.asyncio
    async def test_trace_requires_api_key(self, patched_app):
        """GET /traces/{id} without api key returns 401."""
        app, _ = patched_app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r = await ac.get("/traces/some-id")
        assert r.status_code == 401
