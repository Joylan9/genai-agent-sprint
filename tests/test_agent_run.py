from __future__ import annotations


def _login(client, email: str, password: str) -> dict[str, str]:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_register_and_bootstrap_me(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "new-user@example.com", "password": "Password123!", "name": "New User"},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["user"]["role"] == "developer"

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {payload['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "new-user@example.com"
    assert me.json()["role"] == "developer"


def test_legacy_password_hash_migrates_on_login(client, fake_db, seed_user):
    user = seed_user(email="legacy@example.com", password="Password123!", legacy=True)
    legacy_hash = user["password_hash"]

    response = client.post(
        "/api/auth/login",
        json={"email": "legacy@example.com", "password": "Password123!"},
    )

    assert response.status_code == 200
    stored_user = fake_db.users.docs[0]
    assert stored_user["password_hash"] != legacy_hash
    assert stored_user["password_hash"].startswith("scrypt$")


def test_sync_agent_run_requires_bearer_token(client):
    response = client.post("/agent/run", json={"session_id": "sync-test", "goal": "Explain RAG simply"})
    assert response.status_code == 401


def test_sync_agent_run_uses_canonical_payload(client, auth_headers, mock_agent):
    response = client.post(
        "/agent/run",
        json={"session_id": "sync-test", "goal": "Explain RAG simply", "agent_id": "agent-123"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"] == "Mocked final answer for testing"
    assert payload["request_id"] == "sync-run-001"
    assert payload["status"] == "completed"
    mock_agent.run_goal.assert_awaited()


def test_viewer_cannot_mutate_agents(client, seed_user):
    seed_user(email="viewer@example.com", password="Password123!", role="viewer", name="Viewer User")
    headers = _login(client, "viewer@example.com", "Password123!")

    response = client.post(
        "/api/agents",
        json={"name": "Blocked Agent", "version": "1.0.0", "description": "Should not be created"},
        headers=headers,
    )

    assert response.status_code == 403


def test_submit_run_creates_single_queued_trace(client, auth_headers, task_delay_mock):
    response = client.post(
        "/api/runs/submit",
        json={"session_id": "queue-test", "goal": "Collect findings", "agent_id": None},
        headers=auth_headers,
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "queued"

    status_response = client.get(f"/api/runs/{payload['run_id']}/status", headers=auth_headers)
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "queued"
    assert status_response.json()["completed_at"] is None

    trace_response = client.get(f"/traces/{payload['run_id']}", headers=auth_headers)
    assert trace_response.status_code == 200
    trace = trace_response.json()
    assert trace["request_id"] == payload["run_id"]
    assert trace["status"] == "queued"

    runs_response = client.get("/api/runs?status=queued", headers=auth_headers)
    assert runs_response.status_code == 200
    runs = runs_response.json()
    assert any(run["id"] == payload["run_id"] and run["status"] == "queued" for run in runs)
    task_delay_mock.assert_called_once()


def test_agent_version_snapshot_and_promote(client, auth_headers, seed_user):
    create_response = client.post(
        "/api/agents",
        json={
            "name": "Trace Agent",
            "version": "1.0.0",
            "description": "Initial snapshot",
            "status": "active",
            "metadata": {"owner": "platform"},
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    agent = create_response.json()
    assert agent["current_version"] == "1.0.0"
    assert len(agent["versions"]) == 1

    version_response = client.post(
        f"/api/agents/{agent['id']}/versions",
        json={"version": "1.1.0", "metadata": {"source": "test"}},
        headers=auth_headers,
    )
    assert version_response.status_code == 201
    assert version_response.json()["version"] == "1.1.0"

    seed_user(email="admin@example.com", password="Password123!", role="admin", name="Admin User")
    admin_headers = _login(client, "admin@example.com", "Password123!")

    promote_response = client.post(
        f"/api/agents/{agent['id']}/versions/1.1.0/promote",
        headers=admin_headers,
    )
    assert promote_response.status_code == 200
    promoted = promote_response.json()
    assert promoted["current_version"] == "1.1.0"


def test_eval_suite_whitelist_and_roles(client, auth_headers, seed_user):
    suites_response = client.get("/api/eval/suites", headers=auth_headers)
    assert suites_response.status_code == 200
    assert any(item["name"] == "default" for item in suites_response.json())

    unknown_suite_response = client.post(
        "/api/eval/run-suite",
        json={"suite_name": "does-not-exist"},
        headers=auth_headers,
    )
    assert unknown_suite_response.status_code == 400

    seed_user(email="viewer@example.com", password="Password123!", role="viewer", name="Viewer User")
    viewer_headers = _login(client, "viewer@example.com", "Password123!")
    forbidden_response = client.post(
        "/api/eval/run-suite",
        json={"suite_name": "default"},
        headers=viewer_headers,
    )
    assert forbidden_response.status_code == 403


def test_ready_reports_dependency_checks(client):
    response = client.get("/ready")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["checks"]["mongodb"]["status"] == "ready"
    assert payload["checks"]["redis"]["status"] == "ready"
    assert payload["checks"]["celery"]["status"] == "ready"
    assert payload["checks"]["web_search"]["optional"] is True
