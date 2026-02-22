# 💎 GenAI Agent Platform: Universal Enterprise Handbook

[![Frontend Status](https://img.shields.io/badge/Frontend-10/10_Production_Ready-blue?logo=react)](./frontend/Architecture.md)
[![Backend Status](https://img.shields.io/badge/Backend-Production_Certified-green?logo=fastapi)](./app/api_app.py)
[![DevOps Status](https://img.shields.io/badge/DevOps-CI/CD_Hardened-orange?logo=github)](./.github/workflows/frontend-cd.yml)

The **GenAI Agent Platform** is a professional-grade AI orchestration ecosystem. This singular manual provides an exhaustive, 360-degree view of the entire system—from the high-performance FastAPI execution engine to the production-hardened React Control Plane.

---

## 🏛️ 1. Platform Architecture & Topology

The platform is designed as a **fault-tolerant service mesh**, separating the control plane (UI) from the execution plane (API/Workers) and the compute layer (LLM).

```mermaid
graph TD
    User((🌍 Users)) --> |HTTPS| CDN[Global CDN / Cloudflare]
    CDN --> |Static Assets| FE[Frontend SPA: Nginx/React]
    FE -- |API Requests + X-Request-ID| GW[API Gateway: FastAPI]
    
    subgraph "Core Service Mesh"
        GW --> DB[(Primary Store: MongoDB)]
        GW --> Redis[(Queue Broker: Redis)]
        GW --> Ollama[LLM Engine: Ollama]
    end
    
    subgraph "Async Execution Plane"
        Redis --> Workers[Celery Cluster]
        Workers --> Ollama
        Workers --> VectorDB[(Vector DB: Local/Qdrant)]
    end
    
    subgraph "Enterprise Observability"
        FE --> Sentry[Sentry Error Tracking]
        FE --> Telemetry[Behavioral Analytics]
        GW --> Prom[Prometheus Metrics]
        Prom --> Grafana[Grafana Dashboards]
    end
```

---

## 📂 2. Universal Folder structure

```text
/genai-agent-sprint
├── .github/workflows/      # [CI/CD] Automated Engineering Gates
│   └── frontend-cd.yml     # Logic: Lint -> TypeCheck -> Vitest -> Docker Cache -> Push
├── app/                    # [BACKEND] Core Agent Engine Logic
│   ├── api/                # FastAPI Endpoints (Agent, Health, Readiness)
│   ├── core/               # Semantic Search & Vector Logic
│   ├── infra/              # Reliability: Circuit Breakers, Retry, Timeout Executors
│   ├── memory/             # Database Connector (MongoDB) & Conversation History
│   ├── observability/      # Health Monitoring & Prometheus Metrics
│   ├── registry/           # Agent Tool Inventory & Registry
│   ├── security/           # Policy Engine, PII Redaction, Input Sanitization
│   ├── services/           # Planning Agent, Embedding, and Retrieval logic
│   ├── tools/              # Specialized Tools (RAG Search, Web Search)
│   └── api_app.py          # Master API Gateway Orchestrator
├── frontend/               # [FRONTEND] Production-Hardened React Control Plane
│   ├── src/
│   │   ├── app/            # Infrastructure: Layout, Shell, Monitoring, Providers
│   │   ├── features/       # Domains: Agents, Runs, Playground, Status Dashboard
│   │   ├── shared/         # Foundation: UI Palette, Axios Client, Auth Interceptors
│   │   └── main.tsx        # Application Root
│   ├── nginx.conf          # Hardened Production Web Gateway (HSTS, CSP, Gzip)
│   └── Dockerfile          # Multi-stage optimized production build
├── data/                   # [KNOWLEDGE BASE]
│   ├── raw/                # Unstructured Technical Documentation
│   └── vector_store.pkl    # Compiled Semantic Database for RAG
├── scripts/                # [DEVOPS] Platform Utility Scripts
│   ├── build_vector_store.py # RAG Compiler & Vectorizer
│   └── validate_prod_ready.py # Enterprise Readiness Audit Script
├── tests/                  # [QUALITY] 54+ Tests (Unit & Integration)
├── docker-compose.yml      # Cloud-Native Infrastructure Orchestration
└── .env                    # Centralized Environment Secrets
```

---

## 🔥 3. Enterprise Hardening (The 10/10 Standard)

- **Adaptive Resilience**: The UI monitors system health in real-time. If the LLM or API Gateway is offline, execution features automatically degrade gracefully to prevent user frustration.
- **Circuit Breaker Logic**: Backend prevents cascading failures by isolating broken external tools (Web/RAG) with a stateful circuit breaker.
- **Zero-Rebuild Deployments**: Environment variables are injected at runtime via `/config.js`, allowing the same immutable Docker image to be promoted through all environments.
- **Distributed Tracing**: Every agent transaction carries a unique `X-Request-ID`, enabling end-to-end auditability from the React UI down to the MongoDB trace store.

---

## 🚀 4. Full Execution Handbook

### **Phase 1: Environment Setup**
1.  **Initialize Secrets**: 
    ```bash
    cp .env.example .env
    # Required: SERPAPI_KEY, API_KEY, MONGO_URI, OLLAMA_HOST
    ```
2.  **Start Infrastructure**: 
    ```bash
    docker-compose up -d
    # Spins up MongoDB, Redis, and Prometheus
    ```
3.  **Build AI Knowledge Base**: 
    ```bash
    python scripts/build_vector_store.py
    ```

### **Phase 2: Platform Startup**
1.  **Backend API**: 
    ```bash
    pip install -r requirements.txt
    python app/api_app.py
    ```
2.  **Frontend UI**: 
    ```bash
    cd frontend && npm install
    npm run dev
    ```

---

## 🖱️ 5. UI User Guide: "How to Execute Your First Agent"

Follow this path to verify the full project logic:

1.  **Check Pulse**: Open the app and verify the **Green Indicator** in the TopNav.
2.  **NOC Monitoring**: Press `Ctrl+K`, type "Status", and hit Enter. Verify all system components are "Operational."
3.  **Agent Creation**:
    - Sidebar -> **Agents** -> **Create Agent**.
    - Goal: `Compare HSTS vs CSP for enterprise security`.
4.  **Live Execution**:
    - Sidebar -> **Playground** -> Select Agent -> **Execute**.
    - Watch the **Trace Timeline**. You will see the agent query the RAG store and synthesize a security-hardened response.
5.  **Audit Logs**: Click any step in the trace to view the raw JSON interchange and PII redaction logic in action.

---

## 🛠️ 6. Maintenance & Quality
- **Testing**: `pytest` (Backend) | `npm run test` (Frontend).
- **Audit**: Run `python scripts/validate_prod_ready.py` for a full security scan.
- **Production Logs**: `docker logs genai-agent-api -f`.

---

<p align="center">
  <sub>Generated by the Enterprise Architecture Team. Ready for scale.</sub>
</p>
