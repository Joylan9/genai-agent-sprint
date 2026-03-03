<div align="center">

<!-- HERO BANNER -->
<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbzFtZnFxcHFtbGVqbGFtdWJ6ZnRtdWhhanZtYm1wdnVpNXF2dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oKIPEqDGUULpEU0aQ/giphy.gif" width="100%" alt="Neural Network Animation"/>

<br/>

```
 ████████╗██████╗  █████╗  ██████╗███████╗     █████╗ ██╗
 ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝    ██╔══██╗██║
    ██║   ██████╔╝███████║██║     █████╗      ███████║██║
    ██║   ██╔══██╗██╔══██║██║     ██╔══╝      ██╔══██║██║
    ██║   ██║  ██║██║  ██║╚██████╗███████╗    ██║  ██║██║
    ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝    ╚═╝  ╚═╝╚═╝
```

### The AI Control Plane for Production-Grade Agent Operations

*Orchestrate, observe, enforce, and evaluate autonomous AI agents — with the reliability your infrastructure demands.*

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React_19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![MongoDB](https://img.shields.io/badge/MongoDB_7-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://mongodb.com)
[![Redis](https://img.shields.io/badge/Redis_7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev)
[![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

<br/>

[🚀 Launch in 60 Seconds](#-launch-in-60-seconds) · [🏗️ Architecture](#%EF%B8%8F-architecture) · [✨ Capabilities](#-capabilities) · [📊 Data Flow](#-end-to-end-data-flow) · [🐛 Report Bug](../../issues)

</div>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 🔭 Overview

**TraceAI** is a full-stack AI agent operations platform that provides **complete visibility into every planning step, tool call, and synthesis decision** your agents make. It doesn't just run agents — it gives you the runtime, evaluation lab, operations console, and debugging interface in a single cohesive system.

When something breaks, you don't see *"Error: something went wrong."* You see **what** failed, **why** it failed, **how to fix it**, and a **one-click retry** with the original goal pre-filled.

Built for **AI infrastructure engineers**, **GenAI platform teams**, and anyone operating agent systems that need to work beyond a demo.

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## ✨ Capabilities

<table align="center">
<tr>
<td width="50%" valign="top">

### ⚡ Plan → Execute → Synthesize
LLM-powered planner decomposes goals into subtasks, routes to tools with intelligent fallback, and synthesizes final answers — with every step traced and stored.

### 🔬 Execution Timeline
Animated proportional bars showing planner → tool → synthesis timing with hover tooltips, status indicators, and step-by-step trace drill-down.

### 🛡️ Smart Error Diagnostics
**What / Why / Fix / Retry** panels with pattern-based error categorization. Timeouts, auth failures, LLM errors — each gets specific, actionable guidance.

### 📊 Evaluation Lab
Benchmark agents against test suites with **3-score weighted evaluation**: keyword coverage (30%), tool accuracy (30%), and LLM-as-judge scoring (40%).

</td>
<td width="50%" valign="top">

### 🔐 5-Gate Security Guardrails
Prompt injection detection, plan validation, tool output sanitization, memory poisoning prevention, and sensitive data leakage scanning — all hard-blocks, not warnings.

### ⌨️ Command Palette & Power Shortcuts
**Ctrl+K** fuzzy search across pages, agents, runs, and actions. Global keyboard shortcuts (**R** run, **A** agents, **E** evals) for power-user workflows.

### 🔄 Circuit Breaker Pattern
Every external call (Ollama, web search, MongoDB) wrapped in an async circuit breaker with CLOSED → OPEN → HALF_OPEN state transitions to prevent cascade failures.

### 🐳 Production-Ready Infrastructure
One-command deployment via Docker Compose with health checks, readiness probes, Celery background tasks, L1+L2 response caching, and Prometheus observability.

</td>
</tr>
</table>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 📊 Stats at a Glance

<table align="center">
<tr>
<th>Metric</th>
<th>Value</th>
</tr>
<tr><td>🐍 <b>Backend Python Files</b></td><td>45+ across 16 sub-packages</td></tr>
<tr><td>⚛️ <b>Frontend TypeScript Files</b></td><td>60+ React components & modules</td></tr>
<tr><td>📐 <b>Backend Lines of Code</b></td><td>5,000+</td></tr>
<tr><td>🎨 <b>Frontend Lines of Code</b></td><td>15,000+</td></tr>
<tr><td>🧪 <b>Test Files</b></td><td>10 pytest suites + frontend a11y tests</td></tr>
<tr><td>🐳 <b>Docker Services</b></td><td>4 (API, Worker, MongoDB, Redis)</td></tr>
<tr><td>📦 <b>Python Dependencies</b></td><td>44 pinned packages</td></tr>
<tr><td>🔄 <b>CI/CD Pipelines</b></td><td>2 GitHub Actions (Trivy + CodeQL + GHCR)</td></tr>
<tr><td>🛡️ <b>Security Gates</b></td><td>5 hard-block guardrail layers</td></tr>
<tr><td>📡 <b>API Endpoints</b></td><td>7 routers, 20+ routes</td></tr>
</table>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 🏗️ Architecture

<p align="center">
  <img src="https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=1200" width="800" alt="AI Architecture"/>
</p>

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🖥️  FRONTEND  (React 19 + TypeScript + Vite 7)      │
│                                                                             │
│   Dashboard ─── Playground ─── Runs ─── Eval Lab ─── Agent Detail          │
│   CommandPalette (⌘K) ─── Sidebar ─── TopNav ─── ActivityDrawer            │
│   AuthContext ─── ErrorBoundary ─── SystemStatus ─── RunTimeline           │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │  HTTP / SSE
┌─────────────────────────────▼───────────────────────────────────────────────┐
│                        ⚡  API LAYER  (FastAPI + Gunicorn + Uvicorn)        │
│                                                                             │
│   ┌──────────┐  ┌───────────┐  ┌───────────┐  ┌────────┐  ┌────────────┐  │
│   │ Auth API │  │ Platform  │  │ Agent API │  │ Stream │  │ Eval API   │  │
│   │ (JWT)    │  │ (CRUD)    │  │ (Execute) │  │ (SSE)  │  │ (Suites)   │  │
│   └──────────┘  └───────────┘  └───────────┘  └────────┘  └────────────┘  │
│                                                                             │
│   Prometheus Middleware ─── CORS ─── API Key Guard ─── Readiness Probe     │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────────┐
│                        🧠  AGENT RUNTIME                                    │
│                                                                             │
│   ┌────────────────────────────────────────────────────────────────────┐    │
│   │  PlanningAgentService  (576 lines)                                 │    │
│   │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐   │    │
│   │  │ create_plan() │→│ execute_plan()│→│ synthesize_answer()     │   │    │
│   │  │  LLM → JSON  │  │ step-by-step │  │ observations → answer  │   │    │
│   │  └──────────────┘  └──────┬───────┘  └────────────────────────┘   │    │
│   └───────────────────────────┼────────────────────────────────────────┘    │
│                               │                                             │
│   ┌───────────────────────────▼────────────────────────────────────────┐    │
│   │  IntelligentRouter                                                 │    │
│   │  ├─ Primary Execution via ReliableExecutor                         │    │
│   │  ├─ Failure Fallback  → web_search                                 │    │
│   │  └─ Confidence Fallback (RAG similarity < 0.50) → web_search      │    │
│   └───────────────────────────┬────────────────────────────────────────┘    │
│                               │                                             │
│   ┌───────────┐  ┌───────────▼───┐  ┌─────────────┐  ┌────────────────┐   │
│   │ Guardrails│  │ ToolRegistry  │  │ PolicyEngine│  │ ResponseCache  │   │
│   │ (5 gates) │  │ RAG/Web/Calc  │  │ enforcement │  │ L1 mem + L2 DB │   │
│   └───────────┘  └───────────────┘  └─────────────┘  └────────────────┘   │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────────────┐
│                        🏗️  INFRASTRUCTURE                                   │
│                                                                             │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│   │   Ollama     │  │  MongoDB 7   │  │   Redis 7    │  │   Celery     │  │
│   │  Local LLM   │  │ Traces/Users │  │ Broker/Cache │  │  Background  │  │
│   │  llama3 8B   │  │  6 indexed   │  │  acks_late   │  │  agent tasks │  │
│   │              │  │  collections │  │              │  │  5min limit  │  │
│   │  ┌────────┐  │  └──────────────┘  └──────────────┘  └──────────────┘  │
│   │  │Circuit │  │                                                         │
│   │  │Breaker │  │  ┌──────────────────────────────────────────────────┐   │
│   │  │(async) │  │  │  Prometheus  ─── request count/latency           │   │
│   │  └────────┘  │  │                  LLM call count/latency/failures │   │
│   └──────────────┘  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

<br/>

<details>
<summary><h3>🧠 Agent Runtime — Deep Dive</h3></summary>

The core engine is `PlanningAgentService` (576 lines), implementing a **Plan → Execute → Synthesize** pipeline:

| Stage | Method | What Happens |
|-------|--------|-------------|
| **Plan** | `create_plan()` | Sends goal to LLM with structured prompt. Requests JSON plan with `tool` + `query` per step. Retries JSON parsing up to `max_json_retries` times |
| **Parse** | `parse_plan_json()` | Robust JSON extraction — handles markdown fences, partial JSON, nested structures |
| **Execute** | `execute_plan()` | Iterates plan steps, routes each to `IntelligentRouter`, collects observations, applies guardrail validation on every output, stores traces in MongoDB |
| **Synthesize** | `synthesize_answer()` | Combines all observations + memory context, generates final coherent answer via LLM |

**IntelligentRouter** adds two fallback strategies:
1. **Failure-based**: Primary tool errors → automatic fallback to `web_search`
2. **Confidence-based**: RAG returns similarity < 0.50 → transparent fallback to `web_search`

All routing decisions produce structured logs with `request_id`, tool names, and fallback reasons.

</details>

<details>
<summary><h3>🔐 Security — 5-Gate Guardrails</h3></summary>

Every request passes through **five independent security gates** — all hard-blocks that raise `ValueError` immediately:

| Gate | Method | Patterns Detected |
|------|--------|------------------|
| **Input Validation** | `validate_user_input()` | 13 prompt injection patterns: *"ignore previous instructions"*, *"reveal system prompt"*, *"dump memory"*, *"bypass security"* + 16KB input length limit |
| **Plan Validation** | `validate_plan()` | Max 12 steps, tool whitelist enforcement, step shape validation (requires `tool` + `query` per step) |
| **Output Sanitization** | `sanitize_tool_output()` | 8 malicious output patterns: *"system override"*, *"exfiltrate"*, *"steal"*, *"run this code"* + sensitive data scanning |
| **Memory Protection** | `validate_memory_write()` | 7 memory poisoning indicators: *"from now on"*, *"always answer"*, *"store this permanently"*, *"do not forget"* |
| **Answer Leakage** | `validate_final_answer()` | Scans for API keys, passwords, secrets, private keys, AWS credentials, authorization headers |

The **PolicyEngine** provides an additional enforcement layer on top of guardrails.

</details>

<details>
<summary><h3>🔄 Reliability — Circuit Breaker & Resilience</h3></summary>

Every external service call is wrapped in an **async circuit breaker**:

```
CLOSED (normal)  ──[N consecutive failures]──►  OPEN (rejecting all calls)
                                                       │
                                              [recovery_timeout elapsed]
                                                       │
                                                       ▼
                                                 HALF_OPEN (testing)
                                                   │          │
                                              [success]   [failure]
                                                   │          │
                                                   ▼          ▼
                                                CLOSED       OPEN
```

| Parameter | LLM Circuit | Default |
|-----------|-------------|---------|
| `failure_threshold` | 4 | 5 |
| `recovery_timeout` | 30s | 30s |
| `execution_timeout` | 150s | 15s |

**Additional resilience mechanisms:**
- **Concurrency semaphore** — max 2 parallel LLM calls per worker
- **RetryPolicy** — configurable retry with backoff
- **TimeoutExecutor** — hard timeout enforcement per operation
- **ReliableExecutor** — wraps tools with retry + timeout + error handling

</details>

<details>
<summary><h3>📦 Caching — L1 + L2 Response Cache</h3></summary>

Smart caching with two tiers to minimize redundant LLM calls:

| Layer | Storage | TTL | Speed |
|-------|---------|-----|-------|
| **L1** | In-memory dict (per process) | 1 hour | Instant |
| **L2** | MongoDB `response_cache` collection | TTL index auto-expiry | ~1ms |

**Lookup order:** L1 goal key → L1 plan key → L2 goal key → L2 plan key → cache miss → full agent execution.

Keys are SHA-256 hashes of normalized goal text and goal+plan combinations.

</details>

<details>
<summary><h3>⏳ Background Tasks — Celery Architecture</h3></summary>

Long-running agent executions are decoupled from the API via **Celery**:

```
POST /api/runs/submit
    → Create trace (status=queued) in MongoDB
    → celery_app.send_task("agent.execute_run")
    → Return run_id immediately

Celery Worker picks up:
    → status=running → create_plan() → execute_plan() → synthesize_answer()
    → status=completed | failed
    → Emit run_events for SSE streaming
```

| Config | Value |
|--------|-------|
| `max_retries` | 1 |
| `time_limit` | 300s (hard kill) |
| `soft_time_limit` | 240s (graceful) |
| `acks_late` | `True` (at-least-once) |
| `reject_on_worker_lost` | `True` |

</details>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## ⚙️ Backend Deep Dive

<p align="center">
  <img src="https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200" width="800" alt="Enterprise Infrastructure"/>
</p>

<details>
<summary><h3>📡 API Layer — 7 Routers, 20+ Endpoints</h3></summary>

| Router | File | Routes | Responsibility |
|--------|------|--------|---------------|
| **Auth** | `app/api/auth.py` (609 lines) | `/api/auth/*` | Register, login, refresh, profile, OTP forgot-password. Hand-rolled JWT (HMAC-SHA256), SHA-256 password hashing |
| **Platform** | `app/api/platform.py` (330 lines) | `/api/agents/*`, `/api/runs/*` | Agent CRUD, run history with search/filter, Celery-backed async run submission, feature flags |
| **Agent** | `app/api/agent.py` | `/agent/run` | Synchronous agent execution |
| **Stream** | `app/api/stream.py` | `/api/runs/{id}/stream` | Server-Sent Events for real-time run progress |
| **Eval** | `app/api/eval.py` | `/api/eval/*` | Evaluation suite execution and results |
| **Health** | `app/observability/health.py` | `GET /health` | Basic health status |
| **Readiness** | `app/observability/readiness.py` | `GET /ready` | Dependency health checks |

**Auth system highlights:**
- 8 Pydantic request/response models
- JWT via raw `hmac` / `hashlib` — zero external JWT dependencies
- `get_current_user` / `get_optional_user` FastAPI dependency injection
- OTP flow: 6-digit code → SMTP delivery → auto-fill in dev mode when SMTP unconfigured
- Full forgot-password: request OTP → verify → reset token → new password

</details>

<details>
<summary><h3>🧠 Tools & Routing</h3></summary>

**Three registered tools**, self-registering into `ToolRegistry` at import time:

| Tool | File | Mechanism |
|------|------|-----------|
| `rag_search` | `app/tools/rag_search_tool.py` | Vector similarity via **sentence-transformers** + scikit-learn. Returns similarity scores for confidence-based routing |
| `web_search` | `app/tools/web_search_tool.py` | **SerpAPI** web search. Acts as the universal fallback |
| `calculator` | `app/tools/tools.py` | Arithmetic evaluation |

</details>

<details>
<summary><h3>💾 Memory System — 3-Tier Architecture</h3></summary>

| Tier | File | Storage | Purpose |
|------|------|---------|---------|
| **Short-term** | `short_term_memory.py` | In-process buffer | Session context within a single run |
| **Long-term** | `long_term_memory.py` | MongoDB | Persistent cross-session memory |
| **Manager** | `memory_manager.py` | Orchestrator | Coordinates short + long term per session |

**MongoDB Collections & Indexes:**

| Collection | Indexes |
|------------|---------|
| `conversations` | `session_id`, `created_at` |
| `traces` | `request_id` (unique), `session_id`, `timestamp` |
| `agents` | `name_lower` (unique), `created_at` |
| `users` | `email` (unique), `created_at` |
| `run_events` | `run_id`, `timestamp` |
| `long_term_memory` | `session_id`, `created_at` |

</details>

<details>
<summary><h3>📊 Evaluation Engine</h3></summary>

`EvalRunner` (209 lines) runs test suites with **3-score weighted evaluation**:

| Scoring Method | Weight | Logic |
|---------------|--------|-------|
| **Keyword Coverage** | 30% | Fraction of expected keywords found in answer |
| **Tool Accuracy** | 30% | Expected tools used vs. actual tools observed |
| **LLM-as-Judge** | 40% | Same LLM scores relevance (40%), accuracy (30%), completeness (30%) |

Pass threshold: overall score ≥ 50. Results stored in MongoDB `eval_results`. Test cases defined in `eval/test_cases.json` — 5 cases covering knowledge retrieval and current events.

</details>

<details>
<summary><h3>📈 Observability Stack</h3></summary>

| Endpoint | Metrics Exposed |
|----------|----------------|
| `GET /health` | Basic health status |
| `GET /ready` | MongoDB, Ollama dependency checks |
| `GET /metrics` | Prometheus — `request_count`, `request_latency`, `llm_call_count`, `llm_call_latency`, `llm_failure_count` |

Every HTTP request is instrumented via Prometheus middleware. Every LLM call emits latency histograms, success/failure counters, and structured log entries.

</details>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 🖥️ Frontend Deep Dive

<p align="center">
  <img src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200" width="800" alt="Dashboard Analytics"/>
</p>

### 🛠️ Tech Stack

<table align="center">
<tr><th>Technology</th><th>Version</th><th>Role</th></tr>
<tr><td><b>React</b></td><td>19</td><td>UI framework with concurrent features</td></tr>
<tr><td><b>TypeScript</b></td><td>Strict mode</td><td>Type-safe components</td></tr>
<tr><td><b>Vite</b></td><td>7</td><td>Sub-second HMR, native ESM bundler</td></tr>
<tr><td><b>TanStack Query</b></td><td>Latest</td><td>Server state — polling, caching, revalidation</td></tr>
<tr><td><b>Tailwind CSS</b></td><td>v4</td><td>Utility-first styling with dark mode</td></tr>
<tr><td><b>React Router</b></td><td>Latest</td><td>SPA routing</td></tr>
</table>

### 🗺️ Routing Map

<table align="center">
<tr><th>Route</th><th>Page</th><th>Auth</th></tr>
<tr><td><code>/login</code></td><td>LoginPage</td><td>❌</td></tr>
<tr><td><code>/forgot-password</code></td><td>ForgotPasswordPage</td><td>❌</td></tr>
<tr><td><code>/</code></td><td>Dashboard</td><td>✅</td></tr>
<tr><td><code>/agents</code></td><td>AgentListPage</td><td>✅</td></tr>
<tr><td><code>/agents/:id</code></td><td>AgentDetailPage</td><td>✅</td></tr>
<tr><td><code>/runs</code></td><td>RunsListPage</td><td>✅</td></tr>
<tr><td><code>/runs/:id</code></td><td>RunDetailsPage</td><td>✅</td></tr>
<tr><td><code>/execute</code></td><td>PlaygroundPage</td><td>✅</td></tr>
<tr><td><code>/eval</code></td><td>EvalPage</td><td>✅</td></tr>
<tr><td><code>/status</code></td><td>SystemStatusPage</td><td>✅</td></tr>
</table>

### 📱 Pages (8 pages, ~121KB)

<table align="center">
<tr><th>Page</th><th>Capabilities</th></tr>
<tr><td><b>Dashboard</b></td><td>Real-time stat cards, system health monitor, recent runs, agent count, quick actions</td></tr>
<tr><td><b>Playground</b></td><td>Goal input, agent execution trigger, real-time SSE streaming, result display</td></tr>
<tr><td><b>RunDetails</b></td><td>Execution Timeline visualization, step-by-step trace, ErrorPanel for failed runs with What/Why/Fix/Retry</td></tr>
<tr><td><b>EvalPage</b></td><td>Test suite runner, pass/fail scoring, historical comparison, per-case drill-down</td></tr>
<tr><td><b>LoginPage</b></td><td>Premium login with animated background, form validation, registration</td></tr>
<tr><td><b>ForgotPasswordPage</b></td><td>Multi-step OTP flow: email → verify code → set new password</td></tr>
<tr><td><b>AgentDetailPage</b></td><td>Agent config viewer, run history, version management</td></tr>
<tr><td><b>Runs</b></td><td>Run list with search, status filtering (all/pending/running/completed/failed), delete</td></tr>
</table>

### 🧩 Shared UI Component Library (14 components)

<table align="center">
<tr><th>Component</th><th>Purpose</th></tr>
<tr><td><b>RunTimeline</b></td><td>Animated proportional timing bars — planner → tool → synthesis</td></tr>
<tr><td><b>ErrorPanel</b></td><td>What/Why/Fix/Retry error diagnostics with pattern-based categorization</td></tr>
<tr><td><b>CommandPalette</b></td><td>Ctrl+K fuzzy search with keyboard navigation across entire platform</td></tr>
<tr><td><b>EmptyState</b></td><td>Illustrated empty data states</td></tr>
<tr><td><b>StatusBanner</b></td><td>System status notification banners</td></tr>
<tr><td><b>Button / Input / Modal / Badge</b></td><td>Reusable primitives with consistent styling</td></tr>
<tr><td><b>Table / TableSkeleton</b></td><td>Data tables with animated loading states</td></tr>
<tr><td><b>PageLoader / InlineSpinner / Skeleton</b></td><td>Loading state components</td></tr>
</table>

### 🛡️ Cross-Cutting Concerns

<table align="center">
<tr><th>Module</th><th>Contents</th></tr>
<tr><td><code>app/auth/</code></td><td>AuthContext (JWT + user state), RequireRole (role guard), usePermission hook</td></tr>
<tr><td><code>app/errors/</code></td><td>ErrorBoundary, GlobalErrorBoundary, QueryErrorFallback</td></tr>
<tr><td><code>app/monitoring/</code></td><td>SystemStatus widget, SystemStatusPage, useHealthMonitor hook</td></tr>
<tr><td><code>app/providers/</code></td><td>App-wide providers (QueryClient, Router)</td></tr>
<tr><td><code>app/telemetry/</code></td><td>Client-side performance tracking</td></tr>
<tr><td><code>features/agent/</code></td><td>Agent API client, hooks, types, components</td></tr>
</table>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 🧪 Test Coverage

<table align="center">
<tr><th>Test File</th><th>Coverage Area</th></tr>
<tr><td><code>test_agent_run.py</code></td><td>Full agent execution pipeline — plan creation, execution, synthesis</td></tr>
<tr><td><code>test_guardrails.py</code></td><td>All 5 guardrail methods — injection, plan, output, memory, leakage</td></tr>
<tr><td><code>test_router.py</code></td><td>Intelligent router — tool resolution, failure fallback, confidence fallback</td></tr>
<tr><td><code>test_circuit_breaker.py</code></td><td>State transitions: CLOSED → OPEN → HALF_OPEN → CLOSED</td></tr>
<tr><td><code>test_policy_engine.py</code></td><td>Policy engine enforcement rules</td></tr>
<tr><td><code>test_retriever.py</code></td><td>RAG retriever service</td></tr>
<tr><td><code>test_health.py</code></td><td>Health and readiness endpoint responses</td></tr>
<tr><td><code>test_metrics.py</code></td><td>Prometheus metrics emission</td></tr>
<tr><td><code>e2e_smoke_test.py</code></td><td>End-to-end pipeline: API → planner → tools → synthesis</td></tr>
<tr><td><code>conftest.py</code></td><td>Shared fixtures — mocked Ollama, MongoDB, agent instances</td></tr>
</table>

Frontend testing: **Vitest** + **React Testing Library** with accessibility tests (`a11y.test.tsx`).

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 🚀 CI/CD Pipelines

### Backend CI (`ci.yml`)

```
lint-test ────────────────► docker-build
  │                            │
  ├─ Python 3.11 setup         ├─ docker compose build
  ├─ flake8 lint                └─ Trivy container scan
  ├─ bandit security scan          (HIGH/CRITICAL severity)
  └─ pytest suite
```

### Frontend CD (`frontend-cd.yml`)

```
build-and-package
  │
  ├─ CodeQL SAST (JavaScript/TypeScript)
  ├─ npm ci → TypeScript check → ESLint → Vitest → Vite build
  ├─ npm audit (moderate+ blocking)
  ├─ Upload build artifact
  ├─ CodeQL analysis
  └─ Docker build → push to GitHub Container Registry (GHCR)
```

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 🚀 Launch in 60 Seconds

> ℹ️ **Prerequisites:** Docker & Docker Compose, Ollama, Node.js 18+, Python 3.11+

<table align="center"><tr><td>

**1 — Infrastructure**

```bash
docker compose up -d mongo redis
```

**2 — LLM Engine**

```bash
ollama serve
ollama pull llama3:8b-instruct-q4_K_M
```

**3 — Backend**

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1            # Windows PowerShell
pip install -r requirements.txt
uvicorn app.api_app:app --reload --host 0.0.0.0 --port 8000
```

**4 — Celery Worker** *(new terminal)*

```bash
.venv\Scripts\Activate.ps1
celery -A app.infra.celery_app worker --loglevel=info --concurrency=1
```

**5 — Frontend** *(new terminal)*

```bash
cd frontend
npm install
npm run dev
```

**6 — Open** → **http://localhost:5173** → Register → Press `Ctrl+K`

</td></tr></table>

### 🐳 Full Docker Stack (Alternative)

```bash
docker compose up -d        # Starts: MongoDB, Redis, API, Celery Worker
cd frontend && npm run dev  # Frontend SPA (not Dockerized)
```

<table align="center">
<tr><th>Service</th><th>Container</th><th>Port</th><th>URL</th></tr>
<tr><td><b>Backend API</b></td><td><code>genai-api</code></td><td>8000</td><td><a href="http://localhost:8000">http://localhost:8000</a></td></tr>
<tr><td><b>API Docs</b></td><td>—</td><td>8000</td><td><a href="http://localhost:8000/docs">http://localhost:8000/docs</a></td></tr>
<tr><td><b>Frontend</b></td><td>—</td><td>5173</td><td><a href="http://localhost:5173">http://localhost:5173</a></td></tr>
<tr><td><b>MongoDB</b></td><td><code>genai-mongo</code></td><td>27017</td><td>—</td></tr>
<tr><td><b>Redis</b></td><td><code>genai-redis</code></td><td>6379</td><td>—</td></tr>
<tr><td><b>Ollama</b></td><td>—</td><td>11434</td><td><a href="http://localhost:11434">http://localhost:11434</a></td></tr>
</table>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 🔑 Key Technical Decisions

<table align="center">
<tr><th>Decision</th><th>Rationale</th></tr>
<tr><td><b>Local LLM (Ollama)</b> over cloud APIs</td><td>Zero cost, no rate limits, no vendor lock-in, full control over model quantization (Q4_K_M). Supports CPU fallback with smaller models</td></tr>
<tr><td><b>Hand-rolled JWT</b> (no PyJWT)</td><td>Uses stdlib <code>hmac</code>/<code>hashlib</code> for HMAC-SHA256. Zero external auth dependencies</td></tr>
<tr><td><b>Circuit breaker on every external call</b></td><td>Prevents cascade failures — Ollama, web search, MongoDB all wrapped. CLOSED → OPEN → HALF_OPEN state machine</td></tr>
<tr><td><b>L1 + L2 response cache</b></td><td>In-memory for speed, MongoDB for persistence + cross-process sharing. SHA-256 keyed on normalized goal text</td></tr>
<tr><td><b>Celery for long-running tasks</b></td><td>Decouples LLM inference from API process. <code>acks_late</code> + <code>reject_on_worker_lost</code> for at-least-once delivery</td></tr>
<tr><td><b>Multi-stage Docker</b></td><td>Build tools excluded from runtime image. Non-root <code>appuser</code> for security. HF cache dirs pre-created</td></tr>
<tr><td><b>Guardrails as hard-blocks</b></td><td>Immediate <code>ValueError</code> raise — not warnings, not logs. Production-safe by default</td></tr>
<tr><td><b>Error UX as a product feature</b></td><td>ErrorPanel categorizes by pattern (timeout → LLM Timeout, 401 → Auth Failed), suggests fixes, provides one-click retry</td></tr>
</table>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 📊 End-to-End Data Flow

```
 1.  User enters goal in Playground
 2.  POST /api/runs/submit
 3.  Create trace (status=queued) in MongoDB
 4.  Enqueue Celery task → agent.execute_run.delay(run_id, session_id, goal)
 5.  Worker picks up task
 6.  ➜ Guardrails.validate_user_input(goal)
 7.  ➜ ResponseCache.get(goal) → if hit, return cached answer immediately
 8.  ➜ PlanningAgentService.create_plan(goal)
          └─ LLM generates JSON plan: [{tool: "rag_search", query: "..."}, ...]
 9.  ➜ Guardrails.validate_plan(steps)
10.  ➜ For each step:
          a. IntelligentRouter.execute(step)
               └─ ReliableExecutor → CircuitBreaker → Tool
               └─ If error → fallback to web_search
               └─ If RAG similarity < 0.50 → fallback to web_search
          b. Guardrails.sanitize_tool_output(result)
          c. Store observation with timing metadata
11.  ➜ PlanningAgentService.synthesize_answer(observations + memory)
12.  ➜ Guardrails.validate_final_answer(answer)
13.  ➜ ResponseCache.set(goal, plan, answer)
14.  ➜ Update trace → status=completed, final_answer=answer
15.  SSE stream events push to frontend in real-time
16.  RunDetails page renders animated execution timeline
```

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 🤝 Contributing

Contributions welcome. Fork, branch, build, test, and submit:

```bash
# Fork the repo, create a feature branch
git checkout -b feature/your-feature

# Backend: lint, scan, test
flake8 app --max-line-length=120
bandit -r app -lll
pytest tests/ -v

# Frontend: type-check, lint, test
cd frontend
npx tsc --noEmit
npx vitest run

# Commit with conventional format
git commit -m "feat: add your feature description"
git push origin feature/your-feature
```

**Standards enforced:** PEP 8 + flake8 + bandit (backend), TypeScript strict mode + ESLint (frontend).

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 📄 License

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

Distributed under the **MIT License**. See `LICENSE` for details.

<br/>

**⭐ Star this repository if TraceAI resonated with you.**

*Built with FastAPI, React 19, TypeScript, Ollama, and an unreasonable amount of engineering discipline.*

> *"I don't just build features — I build systems that operators trust at 2 AM."*

</div>
