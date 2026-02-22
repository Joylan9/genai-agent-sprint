# � GenAI Agent Engine - Universal Enterprise Platform

[![Frontend Status](https://img.shields.io/badge/Frontend-10/10_Production_Ready-blue?logo=react)](./frontend/Architecture.md)
[![Backend Status](https://img.shields.io/badge/Backend-Production_Certified-green?logo=fastapi)](./api_app.py)
[![DevOps Status](https://img.shields.io/badge/DevOps-CI/CD_Hardened-orange?logo=github)](./.github/workflows/frontend-cd.yml)

The **GenAI Agent Engine** is a professional-grade AI orchestration platform. This manual provides an exhaustive, 360-degree view of the entire system, from the high-performance FastAPI backend to the production-hardened React Control Plane.

---

## �️ 1. Platform Architecture & Topology

The platform is designed as a **fault-tolerant service mesh**, ensuring that agent execution remains reliable even if individual components fail.

```mermaid
graph TD
    User((🌍 Users)) --> |HTTPS| CDN[Global CDN / Cloudflare]
    CDN --> |Static Assets| FE[Frontend SPA: Nginx/React]
{{ ... }}
    end
```

---

## 📂 2. Universal Folder structure

```text
/genai-agent-sprint
├── .github/workflows/      # [CI/CD] Automated Engineering Gates
│   └── frontend-cd.yml     # Logic: Lint -> TypeCheck -> Vitest -> Docker GHA Cache
├── app/                    # [BACKEND] Core Agent Engine Logic
│   ├── api/                # FastAPI Endpoints (Agent, Health, Readiness)
│   ├── core/               # Semantic Search & Vector Logic
│   ├── infra/              # Reliability: Circuit Breakers, Retry, Reliable Executor
│   ├── memory/             # Database Connector (MongoDB) & History Management
│   ├── observability/      # Health Monitoring & Prometheus Exporters
│   ├── registry/           # Agent Tool Inventory
│   ├── security/           # Policy Engine, PII Redaction, Input Sanitization
│   ├── services/           # Planning Agent & Embedding Logic
│   ├── tools/              # Specialized Tools (RAG Search, Web Search)
│   └── api_app.py          # Master API Orchestrator
├── frontend/               # [FRONTEND] Production-Hardened React Control Plane
│   ├── src/
│   │   ├── app/            # Infrastructure: Layout, Shell, Monitoring, Providers
│   │   ├── features/       # Domains: Agents, Runs, Playground, Status
│   │   ├── shared/         # Foundation: UI Palette, Axios Client, Auth Interceptors
│   │   └── main.tsx        # Application Root
│   ├── nginx.conf          # Hardened Production Web Gateway
│   └── Dockerfile          # Multi-stage optimized build
├── data/                   # [KNOWLEDGE BASE]
│   ├── raw/                # Unstructured Technical Docs
│   └── vector_store.pkl    # Compiled Semantic Database
├── scripts/                # [DEVOPS] Platform Utility Scripts
│   ├── build_vector_store.py # RAG Compiler
│   └── validate_prod_ready.py # Enterprise Readiness Audit
├── tests/                  # [QUALITY] 54+ Tests (Unit & Integration)
├── docker-compose.yml      # Local Cloud-Native Orchestration
└── .env                    # Centralized Power Configuration
```

---

## 🔥 3. Enterprise Hardening (The 10/10 Standard)

1.  **Adaptive Resilience**: The UI monitors system health and automatically disables "Execute" buttons if the LLM or API Gateway is offline.
2.  **Circuit Breaker Logic**: Backend prevents cascading failures by isolating broken tools (Web/RAG) with a stateful circuit breaker.
3.  **Zero-Rebuild Deployments**: Environment variables are injected at runtime via `/config.js`, allowing the same Docker image to move from Staging to Production.
4.  **Distributed Tracing**: Every agent thought is timestamped and carries a unique `X-Request-ID` for end-to-end auditability.

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

# 2. Start Control Plane
npm run dev
```

---

## 🖱️ 5. User Guide: "How to Execute Your First Agent"

Follow these steps to experience the full platform logic:

1.  **Verify Health**: Check the **TopNav**. If the indicator is **Green**, the LLM is ready.
2.  **NOC Monitoring**: Press `Ctrl+K` and go to **Status**. Verify that latency is `< 200ms`.
3.  **Agent Creation**:
    - Sidebar -> **Agents** -> **Create Agent**.
    - Set Objective: `Explain the impact of Breadth-First-Search on large graphs`.
4.  **Execution & Tracing**:
    - Sidebar -> **Playground**.
    - Select your Agent and click **Execute**.
    - Watch the **Trace Timeline** populate. Click any step to see exactly how the agent queried the RAG vector store or redact sensitive data.
5.  **Artifact Access**:
    - Once finished, view the **Final Synthesis** and download any generated artifacts from the side panel.

---

## 🛠️ 6. Maintenance & Troubleshooting

- **Tests**: Run `pytest` for backend and `cd frontend && npm run test` for UI.
- **Audit**: Run `python scripts/validate_prod_ready.py` to check for security misconfigurations.
- **Logs**: Access `docker logs genai-agent-api` for real-time traffic monitoring.

---

<p align="center">
  <sub>Generated by the Enterprise Architecture Team. Ready for scale.</sub>
</p>
