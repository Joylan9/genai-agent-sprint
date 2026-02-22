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

## 🔥 3. Enterprise Hardening (The 11/10 Standard)

1.  **Adaptive Resilience**: The UI monitors system health in real-time. If the LLM or API Gateway is offline, execution features automatically degrade gracefully.
2.  **Edge Security & Traffic Control**:
    - **Nginx Rate Limiting**: Enforced at 10r/s with 20 burst capacity to prevent DOS.
    - **TLS termination**: Production template ready for port 443 with HSTS (`max-age=63072000`) and TLS 1.3.
    - **Strict CSP**: Production-tightened Content Security Policy with zero "unsafe" sources.
3.  **CI/CD Registry Integration**: Production-ready images are automatically audited via `npm audit` and pushed to the **GitHub Container Registry (GHCR)**.
4.  **Zero-Rebuild Deployments**: Environment variables are injected at runtime via `/config.js`, ensuring immutable build artifacts.
5.  **Distributed Tracing**: Every agent transaction carries a unique `X-Request-ID` traceable from the UI to the backend logs.

---

## 🚀 4. Full Execution Handbook (Step-by-Step)

### **A. Environment Preparation**
```bash
# 1. Initialize Secrets
cp .env.example .env

# 2. Start Core Infrastructure (DB/Cache)
docker-compose up -d

# 3. Compiling the AI Knowledge Base (RAG)
python scripts/build_vector_store.py
```

### **B. Backend Deployment**
```bash
# 1. Setup Python Runtime
pip install -r requirements.txt

# 2. Launch the Orchestrator
python app/api_app.py
```

### **C. Frontend Deployment**
```bash
# 1. Install Dependencies
cd frontend && npm install

# 2. Start Control Plane (Dev)
npm run dev

# 3. Registry Push (CI)
# Images are pushed to: ghcr.io/${{ github.repository }}/genai-agent-frontend:latest
```

---

## 🖱️ 5. User Guide: "How to Execute Your First Agent"

Follow these steps to experience the full platform logic:

1.  **Verify Health**: Check the **TopNav**. If the indicator is **Green**, the LLM is ready.
2.  **NOC Monitoring**: Press `Ctrl+K` and go to **Status**. Verify that latency is `< 200ms`.
3.  **Readiness Probe**: Check `http://localhost:80/ready` to verify Nginx is active and stable.
4.  **Agent Creation**:
    - Sidebar -> **Agents** -> **Create Agent**.
    - Set Objective: `Explain the impact of Breadth-First-Search on large graphs`.
5.  **Execution & Tracing**:
    - Sidebar -> **Playground**.
    - Select your Agent and click **Execute**.
    - Watch the **Trace Timeline** populate. Click any step to see exactly how the agent queried the RAG vector store or redacted sensitive data.
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
