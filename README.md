<p align="center">
  <h1 align="center"> Enterprise AI Agent Engine</h1>
  <p align="center">
    <strong>Production-ready, modular AI agent backend with planning, tool routing, RAG, memory, caching, guardrails, and observability.</strong>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-0.110+-green?logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/Ollama-LLaMA3-orange?logo=meta&logoColor=white" alt="Ollama" />
    <img src="https://img.shields.io/badge/MongoDB-6.0-47A248?logo=mongodb&logoColor=white" alt="MongoDB" />
    <img src="https://img.shields.io/badge/Redis-7.0-DC382D?logo=redis&logoColor=white" alt="Redis" />
    <img src="https://img.shields.io/badge/Celery-5.x-37814A?logo=celery&logoColor=white" alt="Celery" />
    <img src="https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white" alt="Docker" />
  </p>
</p>

---

## 📖 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Running the Application](#running-the-application)
  - [Enterprise Local Runbook](#-enterprise-local-runbook)
- [API Reference](#api-reference)
- [How It Works](#how-it-works)
- [Use Cases](#use-cases)
- [Deployment](#deployment)
- [License](#license)

---

## Overview

The **Enterprise AI Agent Engine** is a production-grade, modular AI backend system that goes far beyond a simple chatbot. It accepts a user goal, generates an intelligent multi-step execution plan using a local LLM (Ollama + LLaMA3), routes each step to the appropriate tool (RAG search, web search, etc.), executes them with enterprise reliability patterns, and synthesizes a final response — all with full observability, caching, memory, and security guardrails.

This project demonstrates real-world AI system engineering: the kind of architecture used internally at companies building AI-powered products at scale.

---

## Key Features

| Category | Feature |
|---|---|
| 🤖 **AI Planning** | LLM-powered multi-step plan generation with auto-repair for malformed JSON |
| 🔀 **Intelligent Routing** | Semantic similarity-based tool selection with configurable thresholds |
| 🔍 **RAG Pipeline** | Retrieval-Augmented Generation with local embeddings and vector search |
| 🌐 **Web Search** | Integrated web search tool for real-time information retrieval |
| 💾 **Response Caching** | Smart cache layer (MongoDB-backed) to avoid redundant LLM calls |
| 🧠 **Memory System** | Session-aware short-term + semantic long-term memory for context continuity |
| 🛡️ **Security Guardrails** | Input validation, prompt injection detection, tool whitelist enforcement, output sanitization |
| ⚡ **Reliability** | Retry policies, timeout executors, concurrent tool execution with semaphores |
| 📊 **Observability** | Structured logging, Prometheus metrics, full execution traces stored in MongoDB |
| 🔑 **API Key Auth** | Header-based API key authentication on protected endpoints |
| 🐳 **Docker Ready** | Multi-stage Dockerfile with Gunicorn + Uvicorn workers |
| 📦 **Async Workers** | Celery + Redis for background task processing |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Client (curl / Postman / Frontend)          │
└────────────────────────────────┬────────────────────────────────────┘
                                 │  HTTP (JSON)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FastAPI  (api/app.py)                         │
│  ┌──────────┐  ┌───────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ /health  │  │ /metrics  │  │ /agent/run   │  │ /traces/{id} │  │
│  └──────────┘  └───────────┘  └──────┬───────┘  └──────────────┘  │
│                                      │                             │
│           API Key Auth  ·  Input Validation  ·  Rate Limiting      │
└──────────────────────────────────────┬─────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PlanningAgentService  (app/services/)                  │
│                                                                     │
│   1. Guardrails → validate input                                    │
│   2. LLM (Ollama) → generate execution plan (JSON)                 │
│   3. Parse + auto-repair plan                                       │
│   4. Guardrails → validate plan (tool whitelist, step limits)       │
│   5. Cache check → return cached response if hit                    │
│   6. IntelligentRouter → execute each step via tools                │
│   7. Guardrails → sanitize tool outputs                             │
│   8. Memory → retrieve session context                              │
│   9. LLM (Ollama) → synthesize final answer                        │
│  10. Guardrails → validate final answer                             │
│  11. Cache + Memory → persist results                               │
│  12. Trace → store full execution trace in MongoDB                  │
└─────────┬───────────────────────────────────┬───────────────────────┘
          │                                   │
          ▼                                   ▼
┌──────────────────┐              ┌────────────────────┐
│  Tool Registry   │              │   Memory Manager   │
│  ┌────────────┐  │              │  ┌──────────────┐  │
│  │ RAG Search │  │              │  │  Short-term  │  │
│  │ Web Search │  │              │  │  Long-term   │  │
│  └────────────┘  │              │  │  (Semantic)  │  │
└──────────────────┘              │  └──────────────┘  │
                                  └────────────────────┘
          │                                   │
          ▼                                   ▼
┌──────────────────┐              ┌────────────────────┐
│   Redis (Broker) │              │  MongoDB (Storage)  │
│   Celery Worker  │              │  Traces · Cache     │
└──────────────────┘              │  Memory · Vectors   │
                                  └────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.11 |
| **Web Framework** | FastAPI (ASGI) |
| **LLM Runtime** | Ollama (local) with LLaMA3 8B Instruct |
| **Embeddings** | Sentence-Transformers (local) |
| **Database** | MongoDB 6.0 |
| **Message Broker** | Redis 7.0 |
| **Task Queue** | Celery 5.x |
| **Containerization** | Docker (multi-stage build) |
| **ASGI Server** | Uvicorn (dev) / Gunicorn + Uvicorn (prod) |
| **Metrics** | Prometheus client |
| **Validation** | Pydantic v2 |

---

## Project Structure

```
genai-agent-sprint/
│
├── api/                          # API layer (FastAPI)
│   ├── app.py                    # FastAPI entrypoint, middleware, routes
│   ├── dependencies.py           # Agent assembly & dependency injection
│   └── schemas.py                # Pydantic request/response models
│
├── app/                          # Core application logic
│   ├── services/                 # Business logic services
│   │   ├── planning_agent_service.py   # Main planning agent (plan → execute → synthesize)
│   │   ├── embedding_service.py        # Text embedding generation
│   │   └── retriever_service.py        # Vector similarity retrieval
│   │
│   ├── tools/                    # Agent tools
│   │   ├── rag_search_tool.py    # RAG-based document search
│   │   └── web_search_tool.py    # Web search integration
│   │
│   ├── routing/                  # Intelligent tool routing
│   │   └── intelligent_router.py # Semantic similarity-based routing
│   │
│   ├── registry/                 # Tool registration system
│   │   └── tool_registry.py      # Central tool registry
│   │
│   ├── memory/                   # Memory management
│   │   ├── memory_manager.py     # Short-term + long-term memory
│   │   └── database.py           # MongoDB connection & indexes
│   │
│   ├── cache/                    # Caching layer
│   │   └── response_cache.py     # Smart response caching
│   │
│   ├── security/                 # Security & guardrails
│   │   └── guardrails.py         # Input/output validation, injection detection
│   │
│   ├── infra/                    # Infrastructure utilities
│   │   ├── logger.py             # Structured logging + Prometheus metrics
│   │   ├── retry_policy.py       # Configurable retry with backoff
│   │   ├── timeout_executor.py   # Execution timeout enforcement
│   │   ├── reliable_executor.py  # Combined retry + timeout executor
│   │   ├── validators.py         # Input sanitization
│   │   └── celery_app.py         # Celery application config
│   │
│   ├── core/                     # Core components
│   │   └── vector_store.py       # Vector store for embeddings
│   │
│   ├── observability/            # Monitoring & tracing
│   └── reliability/              # Reliability patterns
│
├── data/                         # Data files
│   └── sample.txt                # Sample document for RAG
│
├── scripts/                      # Utility scripts
├── Dockerfile                    # Multi-stage production Docker build
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables
└── .gitignore
```

---

## Getting Started

### Prerequisites

| Requirement | Purpose |
|---|---|
| **Python 3.11+** | Runtime |
| **WSL 2 (Ubuntu)** | Linux environment on Windows |
| **Docker Desktop** | Running MongoDB & Redis containers |
| **Ollama** | Local LLM inference server |

### Installation

**1. Clone the repository**

```bash
git clone <your-repo-url>
cd genai-agent-sprint
```

**2. Create and activate virtual environment (WSL)**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**4. Pull the LLM model**

```bash
ollama pull llama3:8b-instruct-q4_K_M
```

**5. Configure environment**

Create a `.env` file in the project root (or edit the existing one):

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=agent_db
REDIS_URL=redis://localhost:6379/0
API_KEY=supersecretkey
```

---

## Running the Application

### 🚀 Enterprise Local Runbook

Your backend consists of **separate processes** that mirror production architecture:

| Process | Role | Terminal |
|---|---|---|
| **MongoDB** | Database (traces, cache, memory) | Docker |
| **Redis** | Message broker for Celery | Docker |
| **FastAPI** | HTTP API server | Terminal 1 |
| **Celery Worker** | Async task processing | Terminal 2 |

---

#### Step 1 — Start Infrastructure (Docker)

Open **WSL terminal** and start MongoDB & Redis (one-time after reboot):

```bash
# Check if already running
docker ps

# Start if not running
docker run -d --name mongo -p 27017:27017 mongo:6
docker run -d --name redis -p 6379:6379 redis:7
```

**✅ Verify:** `docker ps` should show both `mongo` and `redis` containers.

---

#### Step 2 — Start FastAPI Server (Terminal 1)

Open a **new WSL terminal**:

```bash
cd "/mnt/d/GenAI and AgenticAI/genai-agent-sprint"
source .venv/bin/activate

uvicorn api.app:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
```

**✅ Expected output:**

```
✅ MongoDB connected and indexes ensured.
Application startup complete
Uvicorn running on http://0.0.0.0:8000
```

> ⚠️ Keep this terminal running.

---

#### Step 3 — Start Celery Worker (Terminal 2)

Open **another WSL terminal**:

```bash
cd "/mnt/d/GenAI and AgenticAI/genai-agent-sprint"
source .venv/bin/activate

python -m celery \
  -A app.infra.celery_app worker \
  --loglevel=info \
  --concurrency=2
```

**✅ Expected output:**

```
Connected to redis://localhost:6379/0
celery@... ready.
```

> ⚠️ Keep this terminal running. Celery is **required** for full agent functionality.

---

#### Step 4 — Verify System Health

```bash
curl http://127.0.0.1:8000/health
```

**✅ Expected:**

```json
{"status": "ok"}
```

---

#### Step 5 — Test the Agent

```bash
curl -X POST http://127.0.0.1:8000/agent/run \
  -H "Content-Type: application/json" \
  -H "x-api-key: supersecretkey" \
  -d '{"session_id":"test-user","goal":"Explain RAG simply"}'
```

---

### Quick Reference (Copy-Paste)

```bash
# === TERMINAL 0: Infrastructure ===
docker start mongo redis    # if containers exist but stopped

# === TERMINAL 1: FastAPI ===
cd "/mnt/d/GenAI and AgenticAI/genai-agent-sprint"
source .venv/bin/activate
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

# === TERMINAL 2: Celery Worker ===
cd "/mnt/d/GenAI and AgenticAI/genai-agent-sprint"
source .venv/bin/activate
python -m celery -A app.infra.celery_app worker --loglevel=info --concurrency=2
```

---

## API Reference

### `GET /health`

Health check endpoint (no auth required).

```json
{"status": "ok"}
```

### `GET /ready`

Database readiness probe.

```json
{"status": "ready"}
```

### `GET /metrics`

Prometheus-compatible metrics endpoint.

### `POST /agent/run`

Execute an AI agent task.

**Headers:**

| Header | Value |
|---|---|
| `Content-Type` | `application/json` |
| `x-api-key` | Your API key |

**Request Body:**

```json
{
  "session_id": "unique-session-id",
  "goal": "Your question or task for the AI agent"
}
```

**Response:**

```json
{
  "result": "The agent's synthesized response",
  "request_id": "uuid-trace-id"
}
```

### `GET /traces/{request_id}`

Retrieve full execution trace for debugging (auth required).

---

## How It Works

```
User Goal → Input Guardrails → LLM Plan Generation → Plan Validation
    → Cache Check (hit? return cached) → Tool Execution (parallel)
    → Output Sanitization → Memory Retrieval → LLM Synthesis
    → Final Answer Guardrails → Cache + Memory Store → Response
```

1. **Input Validation** — The user's goal is checked for prompt injection and sanitized.
2. **Plan Generation** — The LLM creates a structured JSON plan with tool calls.
3. **Plan Validation** — Guardrails enforce tool whitelists and step limits.
4. **Cache Lookup** — If an identical request was previously processed, the cached result is returned instantly.
5. **Parallel Tool Execution** — Steps are executed concurrently (up to 4 at a time) via the intelligent router.
6. **Output Sanitization** — Each tool's output is scanned for sensitive data leakage.
7. **Context Retrieval** — Session memory and semantically relevant past interactions are fetched.
8. **Answer Synthesis** — The LLM combines observations + memory into a final response.
9. **Post-Validation** — The final answer is checked for data leakage before being returned.
10. **Persistence** — Results are cached, memory is updated, and a full trace is stored.

---

## Use Cases

- **Enterprise Knowledge Assistant** — Query internal documents with RAG-powered search
- **Research Agent** — Combine web search + document retrieval for comprehensive answers
- **Customer Support Backend** — Session-aware, context-rich AI responses
- **AI Workflow Automation** — Multi-step task planning and execution
- **Interview Portfolio Project** — Demonstrates production AI system design skills

---

## Deployment

### Docker (Production)

```bash
docker build -t ai-agent-engine .
docker run -p 8000:8000 \
  -e MONGO_URI=mongodb://mongo:27017 \
  -e REDIS_URL=redis://redis:6379/0 \
  -e API_KEY=your-production-key \
  ai-agent-engine
```

The Dockerfile uses a **multi-stage build** with Gunicorn + Uvicorn workers for production performance.

### Production Architecture

```
nginx (reverse proxy)
  └── Gunicorn + Uvicorn workers (FastAPI)
  └── Celery worker pool
  └── MongoDB (database)
  └── Redis (broker)
  └── Ollama (LLM server)
```

---

## Enterprise Design Highlights

| Concern | Implementation |
|---|---|
| **Separation of concerns** | API layer / services / tools / infra cleanly separated |
| **Dependency injection** | `build_agent()` wires all components at startup |
| **Reliability** | Retry with exponential backoff + timeout enforcement |
| **Security** | API key auth, input sanitization, prompt injection detection, output scanning |
| **Observability** | Structured logs, Prometheus metrics, full execution traces |
| **Performance** | Response caching, parallel tool execution, async I/O |
| **Memory** | Hybrid short-term (recent) + long-term (semantic) memory |
| **Scalability** | Celery workers, Docker-ready, stateless API design |

---

## License

This project is for educational and portfolio purposes.

---

<p align="center">
  <sub>Built with ❤️ as part of the GenAI & Agentic AI System Builder Sprint</sub>
</p>
