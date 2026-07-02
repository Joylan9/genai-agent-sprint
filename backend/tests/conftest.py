from __future__ import annotations

import copy
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
import pydantic.networks as pydantic_networks


class _EmailNotValidError(ValueError):
    pass


class _EmailParts:
    def __init__(self, email: str):
        local_part, _, domain = email.partition("@")
        self.normalized = f"{local_part}@{domain}".lower()
        self.local_part = local_part


class _EmailValidatorStub:
    EmailNotValidError = _EmailNotValidError

    @staticmethod
    def validate_email(email: str, check_deliverability: bool = False):
        if "@" not in email:
            raise _EmailNotValidError("An email address must contain a single @.")
        return _EmailParts(email)


pydantic_networks.email_validator = _EmailValidatorStub()
pydantic_networks.import_email_validator = lambda: None

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("JWT_SECRET", "traceai-test-secret")
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("MONGODB_DB", "traceai_test")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/0")
os.environ.setdefault("OLLAMA_HOST", "http://localhost:11434")
os.environ.setdefault("OLLAMA_MODEL", "llama3:8b-instruct-q4_K_M")
os.environ.setdefault("AUTH_DEV_BYPASS_ENABLED", "false")
os.environ.setdefault("DEV_EMAIL_OTP_ECHO_ENABLED", "true")
os.environ.setdefault("SERPAPI_KEY", "")


class FakeInsertResult:
    def __init__(self, inserted_id: str):
        self.inserted_id = inserted_id


class FakeUpdateResult:
    def __init__(self, matched_count: int, modified_count: int, upserted_id: str | None = None):
        self.matched_count = matched_count
        self.modified_count = modified_count
        self.upserted_id = upserted_id


class FakeDeleteResult:
    def __init__(self, deleted_count: int):
        self.deleted_count = deleted_count


class FakeCursor:
    def __init__(self, docs: list[dict[str, Any]]):
        self.docs = docs

    def sort(self, field: str, direction: int):
        reverse = direction == -1
        self.docs.sort(key=lambda doc: doc.get(field) or "", reverse=reverse)
        return self

    async def to_list(self, length: int | None = None):
        docs = self.docs if length is None else self.docs[:length]
        return [copy.deepcopy(doc) for doc in docs]


class FakeCollection:
    def __init__(self):
        self.docs: list[dict[str, Any]] = []

    async def create_index(self, *args, **kwargs):
        return "ok"

    def _clone(self, doc: dict[str, Any]) -> dict[str, Any]:
        return copy.deepcopy(doc)

    def _matches(self, doc: dict[str, Any], query: dict[str, Any] | None) -> bool:
        if not query:
            return True

        for key, expected in query.items():
            if key == "$or":
                return any(self._matches(doc, subquery) for subquery in expected)

            actual = doc.get(key)
            if isinstance(expected, dict):
                if "$regex" in expected:
                    import re

                    flags = re.IGNORECASE if "i" in expected.get("$options", "") else 0
                    if actual is None or re.search(expected["$regex"], str(actual), flags) is None:
                        return False
                else:
                    if actual != expected:
                        return False
            elif actual != expected:
                return False

        return True

    def _project(self, doc: dict[str, Any], projection: dict[str, int] | None) -> dict[str, Any]:
        if not projection:
            return self._clone(doc)

        include = {key for key, value in projection.items() if value}
        projected = {key: value for key, value in doc.items() if key in include or key == "_id"}
        return self._clone(projected)

    async def find_one(self, query: dict[str, Any]):
        for doc in self.docs:
            if self._matches(doc, query):
                return self._clone(doc)
        return None

    def find(self, query: dict[str, Any] | None = None, projection: dict[str, int] | None = None):
        return FakeCursor([
            self._project(doc, projection)
            for doc in self.docs
            if self._matches(doc, query)
        ])

    async def insert_one(self, doc: dict[str, Any]):
        if "_id" not in doc:
            doc["_id"] = f"doc-{len(self.docs) + 1}"
        self.docs.append(self._clone(doc))
        return FakeInsertResult(str(doc["_id"]))

    async def update_one(self, query: dict[str, Any], update: dict[str, Any], upsert: bool = False):
        for index, doc in enumerate(self.docs):
            if self._matches(doc, query):
                updated = self._clone(doc)
                for field, value in update.get("$set", {}).items():
                    updated[field] = value
                for field, value in update.get("$inc", {}).items():
                    updated[field] = updated.get(field, 0) + value
                self.docs[index] = updated
                return FakeUpdateResult(matched_count=1, modified_count=1)

        if upsert:
            inserted = {
                key: value
                for key, value in query.items()
                if not key.startswith("$") and not isinstance(value, dict)
            }
            for field, value in update.get("$set", {}).items():
                inserted[field] = value
            await self.insert_one(inserted)
            return FakeUpdateResult(matched_count=0, modified_count=0, upserted_id=str(inserted["_id"]))

        return FakeUpdateResult(matched_count=0, modified_count=0)

    async def delete_one(self, query: dict[str, Any]):
        for index, doc in enumerate(self.docs):
            if self._matches(doc, query):
                self.docs.pop(index)
                return FakeDeleteResult(deleted_count=1)
        return FakeDeleteResult(deleted_count=0)

    async def delete_many(self, query: dict[str, Any]):
        remaining = []
        deleted = 0
        for doc in self.docs:
            if self._matches(doc, query):
                deleted += 1
            else:
                remaining.append(doc)
        self.docs = remaining
        return FakeDeleteResult(deleted_count=deleted)


class FakeDatabase:
    def __init__(self):
        self.agents = FakeCollection()
        self.agent_versions = FakeCollection()
        self.conversations = FakeCollection()
        self.eval_results = FakeCollection()
        self.long_term_memory = FakeCollection()
        self.password_resets = FakeCollection()
        self.response_cache = FakeCollection()
        self.run_events = FakeCollection()
        self.traces = FakeCollection()
        self.users = FakeCollection()

    async def command(self, name: str):
        if name != "ping":
            raise ValueError(f"Unsupported command {name}")
        return {"ok": 1}


def make_legacy_hash(password: str, salt: str = "legacy-salt") -> str:
    digest = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
    return f"{salt}${digest}"


@pytest.fixture
def fake_db():
    return FakeDatabase()


@pytest.fixture
def mock_agent():
    agent = MagicMock()
    agent.run_goal = AsyncMock(
        return_value={
            "result": "Mocked final answer for testing",
            "request_id": "sync-run-001",
            "status": "completed",
            "observations": [
                {"step": 1, "tool": "rag_search", "query": "test", "response": {"status": "success", "data": "doc"}}
            ],
            "latency": {"total": 0.42},
        }
    )
    return agent


@pytest.fixture
def task_delay_mock():
    return MagicMock()


@pytest.fixture
def eval_run_mock():
    return AsyncMock(
        return_value={
            "suite_id": "suite-001",
            "suite_name": "default",
            "suite_source": "test_cases.json",
            "total": 1,
            "passed": 1,
            "failed": 0,
            "avg_score": 95.0,
            "avg_latency": 0.2,
            "results": [],
            "timestamp": datetime.now(timezone.utc),
        }
    )


@pytest.fixture
def client(monkeypatch, fake_db, mock_agent, task_delay_mock, eval_run_mock):
    from app.memory.database import MongoDB
    from app.services.eval_runner import EvalRunner
    import api.dependencies
    import app.api.agent as agent_module
    import app.observability.readiness as readiness_module
    import app.tasks.agent_tasks as task_module
    from app.api_app import app as fastapi_app

    monkeypatch.setattr(MongoDB, "connect", lambda: fake_db)
    monkeypatch.setattr(MongoDB, "get_database", lambda: fake_db)
    monkeypatch.setattr(MongoDB, "initialize_indexes", AsyncMock())

    monkeypatch.setattr(api.dependencies, "build_agent", lambda: mock_agent)
    monkeypatch.setattr(agent_module, "build_agent", lambda: mock_agent)
    agent_module._agent = None

    monkeypatch.setattr(task_module.execute_agent_run, "delay", task_delay_mock)
    monkeypatch.setattr(EvalRunner, "run_suite", eval_run_mock)

    ready_ollama = SimpleNamespace(list=lambda: {"models": [{"name": "test-model"}]})
    ready_redis = SimpleNamespace(ping=lambda: True)
    monkeypatch.setattr(readiness_module, "get_ollama_client", lambda: ready_ollama)
    monkeypatch.setattr(readiness_module.redis, "from_url", lambda *args, **kwargs: ready_redis)

    with TestClient(fastapi_app) as test_client:
        yield test_client


@pytest.fixture
def seed_user(fake_db):
    from app.api.auth import _hash_password

    def _seed_user(
        *,
        email: str,
        password: str,
        role: str = "developer",
        legacy: bool = False,
        name: str = "TraceAI User",
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        user = {
            "_id": f"user-{len(fake_db.users.docs) + 1}",
            "email": email.lower(),
            "name": name,
            "role": role,
            "password_hash": make_legacy_hash(password) if legacy else _hash_password(password),
            "created_at": now,
            "updated_at": now,
        }
        fake_db.users.docs.append(copy.deepcopy(user))
        return user

    return _seed_user


@pytest.fixture
def auth_headers(client, seed_user):
    seed_user(email="developer@example.com", password="Password123!", role="developer")
    response = client.post(
        "/api/auth/login",
        json={"email": "developer@example.com", "password": "Password123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
