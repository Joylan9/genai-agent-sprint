# ⚛️ GenAI Agent Engine - Frontend SPA

This directory contains the **Enterprise Control Plane** for the GenAI Agent Engine. Built with React 19, TypeScript, and Vite, it is a production-hardened Single Page Application (SPA) designed for reliability and observability.

---

## 📖 Quick Links
- **Master Documentation**: [../README.md](../README.md) (Full Architecture & Setup)
- **Engineering Blueprint**: [Architecture.md](./Architecture.md)
- **Quality Standards**: [performance.md](./performance.md)

---

## 🛠️ Development Workflow

### **1. Setup**
```bash
npm install
```

### **2. Development Server**
```bash
npm run dev
```
*The app uses **MSW (Mock Service Worker)** for local development if the backend is not reachable.*

### **3. Production Verification**
Before pushing any code, ensure all quality gates pass:
```bash
# Type Checking
npm run typecheck

# Linting
npm run lint

# Unit & Accessibility Tests
npm run test
```

---

## 🛡️ Production Hardening Specs

### **Runtime Configuration**
Configuration is NOT hardcoded in the build. Edit `public/config.js` or mount it in Docker:
```javascript
window.__APP_CONFIG__ = {
  VITE_API_BASE: "https://api.yourdomain.com",
  APP_VERSION: "1.0.4-PROD"
};
```

### **Multi-Stage Dockerfile**
The Dockerfile uses a 2-stage build:
1.  **Builder**: Compiles TypeScript and runs Vite build.
2.  **Runner**: Nginx host with custom `nginx.conf` for SPA routing, HSTS, and aggressive caching.

---

## 📂 Features Implemented
- **Dashboard**: Real-time health indicators and stats.
- **Playground**: Interactive agent execution with streaming trace visualization.
- **Trace Viewer**: Step-by-step auditing of agent "thought" processes.
- **Status Dashboard**: Operational NOC-style health monitoring.
- **Reliability Layer**: Global 401 refresh queue and adaptive UI guards.

---

<p align="center">
  <sub>Part of the GenAI Agent Engine Enterprise Stack.</sub>
</p>
