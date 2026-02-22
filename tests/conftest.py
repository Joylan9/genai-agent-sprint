"""
tests/conftest.py
Shared fixtures for the GenAI Agent Platform test suite.

Mocks external dependencies (Ollama, MongoDB, Redis, SerpAPI)
so tests run without live infrastructure.
"""

import os
import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# ---------------------------------------------------------------------------
# Environment defaults (set BEFORE any app module is imported)
# ---------------------------------------------------------------------------
os.environ.setdefault("API_KEY", "supersecretkey")
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017/test")
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DB", "test_agent_db")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/0")
os.environ.setdefault("OLLAMA_HOST", "http://localhost:11434")
os.environ.setdefault("OLLAMA_MODEL", "llama3:8b-instruct-q4_K_M")
os.environ.setdefault("SERPAPI_KEY", "test-serpapi-key")
os.environ.setdefault("HF_TOKEN", "test-hf-token")


# ---------------------------------------------------------------------------
# Mock Ollama client
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_ollama(monkeypatch):
    """Mock the Ollama client so no real LLM calls are made."""
    mock_client = MagicMock()

    # Default: return a valid plan JSON from chat
    default_plan = json.dumps({
        "steps": [
            {"tool": "rag_search", "query": "test query"}
        ]
    })
    mock_client.chat.return_value = {
        "message": {"content": default_plan}
    }
    mock_client.list.return_value = MagicMock(
        models=[MagicMock(model="llama3:8b-instruct-q4_K_M")]
    )

    monkeypatch.setattr(
        "app.infra.ollama_client._client", mock_client
    )
    monkeypatch.setattr(
        "app.infra.ollama_client.get_ollama_client",
        lambda: mock_client,
    )
    return mock_client


# ---------------------------------------------------------------------------
# Mock MongoDB
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_mongodb(monkeypatch):
    """Mock MongoDB so no real database is needed."""
    mock_db = MagicMock()
    mock_db.command = AsyncMock(return_value={"ok": 1})
    mock_db.traces = MagicMock()
    mock_db.traces.find_one = AsyncMock(return_value=None)
    mock_db.traces.insert_one = AsyncMock()
    mock_db.cache = MagicMock()
    mock_db.cache.find_one = AsyncMock(return_value=None)
    mock_db.cache.insert_one = AsyncMock()
    mock_db.memory = MagicMock()
    mock_db.memory.find = MagicMock(return_value=MagicMock(
        sort=MagicMock(return_value=MagicMock(
            to_list=AsyncMock(return_value=[])
        ))
    ))
    mock_db.memory.insert_one = AsyncMock()

    mock_mongo_class = MagicMock()
    mock_mongo_class.connect = MagicMock()
    mock_mongo_class.initialize_indexes = AsyncMock()
    mock_mongo_class.get_database = MagicMock(return_value=mock_db)

    monkeypatch.setattr("app.memory.database.MongoDB", mock_mongo_class)
    monkeypatch.setattr("api.app.MongoDB", mock_mongo_class)

    return mock_db


# ---------------------------------------------------------------------------
# Mock Redis
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_redis(monkeypatch):
    """Mock Redis so no real broker is needed."""
    mock_r = MagicMock()
    mock_r.ping.return_value = True

    monkeypatch.setattr(
        "api.app.redis",
        MagicMock(from_url=MagicMock(return_value=mock_r)),
    )
    return mock_r


# ---------------------------------------------------------------------------
# Mock RAG tool
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_rag(monkeypatch):
    """Mock RAG search tool to avoid loading real embeddings."""
    mock_tool = MagicMock()
    mock_tool.name = "rag_search"
    mock_tool.execute.return_value = {
        "status": "success",
        "data": "RAG result: sample document content",
        "metadata": {"similarity": 0.85},
    }
    mock_tool.search_with_score.return_value = (
        ["sample document content"],
        [0.85],
    )
    return mock_tool


# ---------------------------------------------------------------------------
# Mock Web Search tool
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_web_search(monkeypatch):
    """Mock web search tool to avoid real SerpAPI calls."""
    mock_tool = MagicMock()
    mock_tool.name = "web_search"
    mock_tool.execute.return_value = {
        "status": "success",
        "data": "Web result: sample search result",
        "metadata": {},
    }
    return mock_tool
