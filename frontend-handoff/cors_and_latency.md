# AI Agent Platform - Latency & CORS Policies

## ⚡ Expected Latency
| Component | Typical Latency | P95 Latency |
|---|---|---|
| **Simple Question** | 2-4 seconds | 6 seconds |
| **Multi-tool Research** | 5-10 seconds | 15 seconds |
| **Cache Hit** | < 200 ms | 500 ms |

### Frontend Guidance: 
Always implement a "Thinking..." state or progress bar when `loading` is true.

---

## 🛡️ CORS & Security
Currently, the backend whitelist is configured for:
- `http://localhost:3000` (React Default)
- `http://localhost:5173` (Vite Default)

### Production Deployment:
For production, the `ORIGINS` environment variable must be updated. If the frontend is on a different domain, ensure your origin is added to the whitelist in `app/api_app.py`.

### Headers
Every request MUST include:
- `x-api-key`: Found in `.env` or `DEV_API_KEY.txt`.
# Current TraceAI Latency and CORS Notes

This section supersedes the older API-key guidance later in the file.

## Expected latency
- `POST /api/runs/submit`: typically under `200ms`
- SSE first event: typically under `1s`, depending on worker pickup
- Cache hit: usually under `500ms`
- Multi-step run: typically `3-15s`

Frontend guidance:
- Show `queued`, then `running`, then the terminal state.
- Prefer SSE for active runs and fall back to `/api/runs/{id}/status` polling.

## CORS
- Default dev origins are `http://localhost:5173`, `http://127.0.0.1:5173`, `http://localhost:4173`, and `http://127.0.0.1:4173`.
- Override with `CORS_ORIGINS` in production.

## Security
- Protected requests use `Authorization: Bearer <access_token>`.
- API keys are not the normal frontend auth mechanism anymore.

---
