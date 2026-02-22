# Architecture & Operations Blueprint

## 🏛️ Layered Architecture
The application follows a strict domain-driven design (DDD) structure to ensure scalability and isolation.

### 1. AppShell (Infrastructure)
- **Global Layout**: Sidebar navigation, TopNav with health monitoring.
- **Error Handling**: `GlobalErrorBoundary` catches unhandled exceptions at the root.
- **Routing**: React Router v7 with RBAC protection (`RequireRole`).

### 2. Features (Domain Modules)
- **Agent Feature**: CRUD, health checks, and stat visualizations.
- **Run Feature**: Execution tracking, log viewing, and trace visualization.
- **Playground**: Interactive prompt engineering with telemetry tracking.

### 3. Shared (Foundation)
- **UI Primitives**: Atomic components (Button, Input, Badge, Table) with accessibility compliance.
- **Lib**: Typed utilities and design tokens.
- **API Client**: Centralized Axios instance with telemetry interceptors.

## 🔐 Security Model
- **RBAC**: Role-based access control via `usePermission` hook.
- **CSP**: Content Security Policy enforced via Meta tags.
- **Governance**: Policy engine integration on the backend is reflected in UI through status indicators.

## 📈 Observability & Reliability
- **Telemetry**: Behavior tracking for key user journeys (agent runs, errors).
- **Health**: Real-time polling of API and ML model availability.
- **Tests**: Automated unit tests + Accessibility scans (8/8 passing).

## 🛡️ Scale & Resilience (Harden 100%)
- **Runtime Injection**: Zero-rebuild deployments via `window.__APP_CONFIG__` (loaded from `/config.js`).
- **Adaptive UI**: Automated system degradation via `StatusBanner` and execution guards in `Playground`.
- **Session Recovery**: 401 interceptor logic in the core API client.
- **Diagnostics**: Version-pinned telemetry (`X-App-Version`) and synthetic health endpoints (`/health-frontend.json`).
