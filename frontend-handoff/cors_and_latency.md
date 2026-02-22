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
