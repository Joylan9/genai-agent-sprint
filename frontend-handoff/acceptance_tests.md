# AI Agent Platform - Acceptance Tests

Before finalizing integration, the frontend should verify the following scenarios:

| Test Case | Step | Expected Result |
|---|---|---|
| **1. Service Ping** | GET `/health` | Status 200, `{"status": "ok"}` |
| **2. Simple Run** | POST `/agent/run` with goal "Hi" | Returns `trace_id` and `response` |
| **3. Policy Check** | POST `/agent/run` with "Delete my database" | Returns 403 or `policy_violation` in metadata |
| **4. Long Query** | POST `/agent/run` with complex research | Handle timeout (poll `/traces/{id}`) |
| **5. Auth Check** | POST `/agent/run` with NO API key | Returns 401 Unauthorized |
# Current TraceAI Acceptance Matrix

Use this matrix instead of the legacy API-key-only checks below.

| Test Case | Step | Expected Result |
|---|---|---|
| Auth bootstrap | POST `/api/auth/register`, GET `/api/auth/me` | Bearer session established and `user.role` returned |
| Refresh | POST `/api/auth/refresh` | New access token issued from refresh token body |
| Sync compatibility | POST `/agent/run` | Returns `result`, `request_id`, `status` |
| Queued run | POST `/api/runs/submit` | Returns `run_id`, `status=queued` |
| Run polling | GET `/api/runs/{id}/status` | Canonical queued/running/completed/failed fields |
| Trace lookup | GET `/traces/{id}` | Same run id, canonical trace fields |
| SSE | GET `/api/runs/{id}/stream` | Ordered lifecycle events until terminal state |
| Agent versions | POST version then promote | `current_version` updates, history stays immutable |
| Eval whitelist | POST unknown suite | 400 |
| Eval RBAC | POST suite as `viewer` | 403 |
| Readiness | GET `/ready` | Structured dependency cards and feature flags |

---
