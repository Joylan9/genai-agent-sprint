"""
app/infra/ollama_client.py
Worker-local singleton Ollama client with:
  - hard timeout (30s)
  - concurrency guard (semaphore)
  - inference observability (latency + success/failure metrics)

After Gunicorn forks, each worker gets its own _client instance
on first call to get_ollama_client(). No shared sockets, no stale
connections.
"""

import os
import time
import asyncio
import logging
import requests
from ollama import Client

from .logger import (
    LLM_CALL_COUNTER,
    LLM_CALL_LATENCY,
    LLM_FAILURE_COUNTER,
    StructuredLogger,
)

_client = None
_logger = logging.getLogger("ollama_client")

# Concurrency guard: max 2 simultaneous LLM calls per worker
_llm_semaphore = None


def get_ollama_client() -> Client:
    """Return a worker-local cached Ollama Client (singleton per process)."""
    global _client
    if _client is None:
        _client = Client(
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            timeout=30,
        )
    return _client


def get_ollama_model() -> str:
    """Return the configured model name from env."""
    return os.getenv("OLLAMA_MODEL", "llama3:8b-instruct-q4_K_M")


def get_llm_semaphore() -> asyncio.Semaphore:
    """Return a worker-local LLM concurrency semaphore (max 2 parallel calls)."""
    global _llm_semaphore
    if _llm_semaphore is None:
        max_concurrent = int(os.getenv("LLM_MAX_CONCURRENCY", "2"))
        _llm_semaphore = asyncio.Semaphore(max_concurrent)
    return _llm_semaphore


def llm_chat(client: Client, **kwargs) -> dict:
    """
    Observable wrapper around client.chat().

    Automatically records:
      - inference latency (Prometheus histogram)
      - success/failure counts (Prometheus counters)
      - structured log entry with duration
    """
    start = time.time()
    model = kwargs.get("model", "unknown")

    try:
        response = client.chat(**kwargs)
        duration = time.time() - start

        # Prometheus metrics
        LLM_CALL_COUNTER.labels(status="success").inc()
        LLM_CALL_LATENCY.observe(duration)

        # Structured log
        _logger.info(
            f"llm_call model={model} duration={duration:.2f}s status=success"
        )

        return response

    except requests.exceptions.Timeout as e:
        duration = time.time() - start
        LLM_CALL_COUNTER.labels(status="error").inc()
        LLM_FAILURE_COUNTER.labels(error_type="timeout").inc()
        _logger.error(
            f"llm_call model={model} duration={duration:.2f}s status=timeout"
        )
        raise RuntimeError("LLM request timed out") from e

    except requests.exceptions.ConnectionError as e:
        duration = time.time() - start
        LLM_CALL_COUNTER.labels(status="error").inc()
        LLM_FAILURE_COUNTER.labels(error_type="connection").inc()
        _logger.error(
            f"llm_call model={model} duration={duration:.2f}s status=connection_error"
        )
        raise RuntimeError("LLM unavailable") from e

    except requests.exceptions.RequestException as e:
        duration = time.time() - start
        LLM_CALL_COUNTER.labels(status="error").inc()
        LLM_FAILURE_COUNTER.labels(error_type="request").inc()
        _logger.error(
            f"llm_call model={model} duration={duration:.2f}s status=error error={e}"
        )
        raise RuntimeError("LLM unavailable") from e
