"""
Minimal smoke tests for the GenAI Agent Platform API.
Run with: pytest tests/ -q
"""

from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client with mocked MongoDB."""
    with patch("app.api_app.MongoDB") as mock_mongo:
        mock_db = MagicMock()
        mock_mongo.connect.return_value = mock_db
        mock_mongo.initialize_indexes = AsyncMock()
        mock_mongo.get_database.return_value = mock_db

        from app.api_app import app
        with TestClient(app) as c:
            yield c


def test_root(client):
    """Root endpoint returns service info."""
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "GenAI Agent Platform"
    assert data["status"] == "running"


def test_health_endpoint_exists(client):
    """Health endpoint is reachable (may return unhealthy in test env)."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data


def test_ready_endpoint_exists(client):
    """Readiness endpoint is reachable."""
    resp = client.get("/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data


def test_metrics_endpoint(client):
    """Prometheus metrics endpoint returns text data."""
    resp = client.get("/metrics")
    assert resp.status_code == 200
