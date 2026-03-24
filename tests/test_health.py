"""
Smoke tests for the canonical TraceAI application entrypoint.
"""


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "TraceAI Enterprise Control Plane"
    assert payload["status"] == "running"


def test_health_endpoint_exists(client):
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert "status" in payload
    assert "features" in payload


def test_ready_endpoint_exists(client):
    response = client.get("/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert "checks" in payload


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
