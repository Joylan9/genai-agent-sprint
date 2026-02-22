# AI Agent Platform - Acceptance Tests

Before finalizing integration, the frontend should verify the following scenarios:

| Test Case | Step | Expected Result |
|---|---|---|
| **1. Service Ping** | GET `/health` | Status 200, `{"status": "ok"}` |
| **2. Simple Run** | POST `/agent/run` with goal "Hi" | Returns `trace_id` and `response` |
| **3. Policy Check** | POST `/agent/run` with "Delete my database" | Returns 403 or `policy_violation` in metadata |
| **4. Long Query** | POST `/agent/run` with complex research | Handle timeout (poll `/traces/{id}`) |
| **5. Auth Check** | POST `/agent/run` with NO API key | Returns 401 Unauthorized |
