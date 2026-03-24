# AI Agent Platform - Frontend API Reference

This documentation provides everything the frontend team needs to integrate with the AI Agent backend.

## 🔗 Base URLs
- **Development**: `http://localhost:8000`
- **Staging/Prod**: *[To be provided by DevOps]*

## 🔑 Authentication
All protected endpoints require an `x-api-key` header.
- Header: `x-api-key: <YOUR_API_KEY>`
- *Note: See `DEV_API_KEY.txt` for a temporary token.*

## 🚀 Core Endpoint: `POST /agent/run`
Executes an AI goal and returns a result + trace ID.

### Request Body
```json
{
  "session_id": "unique-user-id",
  "goal": "Explain RAG simply",
  "options": { 
    "max_steps": 6, 
    "use_cache": true 
  }
}
```

### Success Response (200)
```json
{
  "trace_id": "uuid-v4",
  "response": "Final synthesized answer...",
  "metadata": {
    "llm_latency_ms": 1024,
    "tools_used": ["rag_search"],
    "cache_hit": false
  }
}
```

## 🔍 Trace Lookup: `GET /traces/{id}`
Returns the full execution trace for debugging or long-lived session history.

## 📊 Monitoring & Health
- **Health**: `GET /health` (200 OK)
- **Readiness**: `GET /ready` (Checks DB + LLM)
- **Metrics**: `GET /metrics` (Prometheus)

---

## 🛠️ Integration Pattern (Long-Running Tasks)
Agent execution can take 3-15 seconds. For the best UX:
1. Show a loading spinner immediately after `POST /agent/run`.
2. If the request exceeds your frontend timeout, the trace is still being generated in the backend.
3. You can poll `GET /traces/{trace_id}` to retrieve results when available.
# Current TraceAI Contract

This section supersedes any older API-key guidance later in this file.

## Authentication
- Protected endpoints use `Authorization: Bearer <access_token>`.
- Bootstrap with `GET /api/auth/me`.
- Refresh with `POST /api/auth/refresh` and body `{ "refresh_token": "..." }`.
- Auth responses include `user.role` with `admin | developer | viewer`.

## Primary run flow
- `POST /api/runs/submit` with `{ session_id, goal, agent_id? }` returns `{ run_id, status: "queued" }`.
- `GET /api/runs/{id}/status` returns canonical queued/run status fields.
- `GET /traces/{id}` returns the canonical persisted trace for the same run id.
- `GET /api/runs/{id}/stream` streams SSE lifecycle events.
- `POST /agent/run` remains as a synchronous compatibility/debug path and accepts the same optional `agent_id`.

## Canonical status vocabulary
- `queued`
- `running`
- `completed`
- `failed`

## Agent versions
- `GET /api/agents/{id}/versions`
- `POST /api/agents/{id}/versions`
- `POST /api/agents/{id}/versions/{version}/promote`

## Eval
- `GET /api/eval/suites`
- `POST /api/eval/run-suite` with `{ "suite_name": "default" }`
- The backend only accepts suite names from the whitelist under `eval/`.

## Monitoring
- `GET /health` is lightweight.
- `GET /ready` returns deep dependency checks and feature availability.

---
