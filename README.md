---
# GenAI Agent Engine — Runbook & Execution Guide

> Professional runbook with step-by-step instructions to run, verify, and troubleshoot the platform locally and in production-like environments.

## Table of Contents
- [Project overview](#project-overview)
- [Repo layout](#repo-layout)
- [Prerequisites](#prerequisites)
- [Required environment variables](#required-environment-variables)
- [Setup (one-time)](#setup-one-time)
- [Local development — backend](#local-development--backend)
- [Local development — Celery & workers](#local-development--celery--workers)
- [Local development — frontend](#local-development--frontend)
- [Generating runtime config.js](#generating-runtime-configjs)
- [Quick full local run (copy-paste)](#quick-full-local-run-copy-paste)
- [Health checks & verification](#health-checks--verification)
- [Creating an agent & running a smoke test](#creating-an-agent--running-a-smoke-test)
- [Troubleshooting & logs collection](#troubleshooting--logs-collection)
- [CI/CD & deployment notes](#cicd--deployment-notes)
- [Security & operational notes](#security--operational-notes)
- [Contact & ownership](#contact--ownership)
- [Changelog / version](#changelog--version)

### Project overview
The GenAI Agent Engine is a robust, full-stack platform designed to orchestrate, manage, and execute AI agent workflows. Built with FastAPI for a high-performance backend, it integrates Celery and Redis to handle asynchronous inference tasks without blocking the main API thread. MongoDB ensures horizontal scaling for agent configurations, LLM interactions, and long-term memory access. The platform natively interacts with local Ollama or remote LLM providers through a unified interface.

The frontend is a React + Vite Single Page Application providing a highly responsive Agent Directory, realtime interactive Chat Playground, and System Health Monitor. This authoritative execution runbook details exactly how to deploy and configure the stack on local development workstations, debug connectivity, scale up testing endpoints, and track production health parameters.

### Repo layout
- `./frontend` — React 18, Vite config, local e2e spec scripts. Uncompiled source resides inside `src`.
- `./app` — Python 3 FastAPI application. Structured strictly with routes, schemas, core infrastructure bindings, and ML components.
- `./scripts` — Shell scripts (`generate-config.sh`) and python verifiers (`smoke_test.py`) for CD processes.
- `docker-compose.yml` — Container composition file enabling instantaneous database & worker spinup.
- `README.md` — This execution runbook.

### Prerequisites
- Git
- Node >= 20, npm
- Python 3.11+
- Docker & docker-compose (for streamlined backend orchestration)
- Optional: Ollama installed locally OR active API credentials for an external LLM provider 

### Required environment variables (names only)
These variables must be populated (preferably in .env files, Docker profiles, or CI secrets):
- `API_BASE`
- `VITE_API_BASE`
- `VITE_API_KEY`
- `APP_VERSION`
- `MONGO_URI`
- `REDIS_URL`
- `OLLAMA_HOST`
- `REFRESH_ENDPOINT`
- `TELEMETRY_ENDPOINT`
- `GHCR_USERNAME`
- `GHCR_TOKEN`

### Setup (one-time)
To instantiate the repository contexts for the first time on a fresh environment, run:

```bash
git clone <REPO_URL>
cd <REPO_ROOT>

# Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm ci
cd ..
```

### Local development — backend
All dependencies including Redit, MongoDB, and the API can be spun via Docker Compose. Ensure `docker daemon` is running.

```bash
# 1. Initialize databases in background
docker compose up -d mongodb redis

# 2. Run the FastAPI development server
source .venv/bin/activate
uvicorn app.api_app:app --host 0.0.0.0 --port 8000 --reload
```

### Local development — Celery & workers
The Celery worker manages intensive agent runs asynchronously.

```bash
# In a new terminal, activate python venv
source .venv/bin/activate
celery -A app.core.celery_app worker -l info
```

### Local development — frontend
React fast-reload loop for UI layout editing:

```bash
cd frontend
npm run dev
# Vite runs at http://localhost:5173
```
To run the production bundle locally (often requires built backend config files):
```bash
npm run build
npm run preview
```

### Generating runtime config.js
To decouple React build constants from actual deployment logic, `config.js` is rendered strictly at startup.

```bash
cd scripts
chmod +x generate-config.sh
./generate-config.sh
# Check frontend/public/config.js. Secret variables will be proactively redacted.
```

### Quick full local run (copy-paste)
In a hurry? Use this composite script block:

```bash
# Bring up API, Worker, Redis, and Mongo natively in containers
docker compose up --build -d

# Drop into the frontend UI layer
cd frontend
npm install
npm run dev
```

### Health checks & verification
To ensure every subcomponent is responsive, trigger the diagnostic links:

- **Liveness probe:** `curl http://localhost:8000/ready`
  - Expected: `{"status":"ready"}`
- **System diagnostics:** `curl http://localhost:8000/health`
  - Expected (abbreviated): `{"status": "healthy", "db": "connected", "redis": "connected", ...}`
- **Browser access:** Navigating to `http://localhost:5173/status` opens the green-lights System Status React visualizer. 

### Creating an agent & running a smoke test
Testing via the CLI confirms backend operational capability instantly.

**Create Agent:**
```bash
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: <YOUR_API_KEY>" \
  -d '{"name":"SmokeTestAgent","version":"1.0.0","description":"Platform Verifier"}'
# Keep the returned 'id'.
```

**Run Agent Workflow:**
```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: <YOUR_API_KEY>" \
  -d '{"agent_id":"<ID>","user_id":"admin","goal":"Ping test"}'
```

Alternatively, invoke the packaged Python end-to-end evaluator:
```bash
python scripts/smoke_test.py
```

### Troubleshooting & logs collection
For debugging API failures, capture the docker logs:

- API logs: `docker compose logs -f api`
- Background processor logs: `docker compose logs -f celery-worker`
- Database access logs: `docker compose logs -f mongodb`

If hitting 500 Timeouts specific to LLM inference or Ollama hanging, inspect that `OLLAMA_HOST` is reachable, and the specified models have physically resolved inside the Ollama daemon. `llm_call` prometheus counters explicitly record duration. Network Refusals (`ECONNREFUSED`) are indicative of inactive Docker resources in the backend.

### CI/CD & deployment notes
- **Frontend Cloudflare Pages:** Commits merged across the main branch initiate Vite compilation sequences automatically pushed to Cloudflare Pages edge relays using `actions/cloudflare-pages`.
- **Backend Docker Images:** Core FastAPI/Celery container layers are rebuilt via `.github/workflows/` and securely transferred into a GHCR image bucket.
- **Production Upstash & Atlas:** Rely heavily on remote persistent state for high concurrency deployments instead of local Docker. 

### Security & operational notes
We employ a zero-trust runtime policy:
- No keys, passwords, URIs, tokens, or JWTs are bundled during the Vite artifact building.
- Redaction layers (`generate-config.sh`) explicitly strip secrets from browser context maps.
- Circuit Breaking protects upstream inference limits avoiding unbounded concurrency spirals.

### Contact & ownership
Submit pull requests against the main branch or execute tickets inside the primary issue tracker for infrastructure routing and maintenance. Ensure all pull requests are prefixed structurally (`chore(docs):`, `fix(api):`).

### Changelog / version
- **v1.0.0** — Completed End-To-End Readiness. Unified API error boundaries, health telemetry hooks, offline degradation UI, and dynamic environment injection modules installed successfully.
---
