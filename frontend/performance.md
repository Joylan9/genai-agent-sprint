# Performance Budgets & Targets

To ensure an enterprise-grade experience, we enforce the following performance budgets.

## 📦 Bundle Size
| Metric | Budget (Gzip) | Priority |
| :--- | :--- | :--- |
| **Initial JS Bundle** | < 300kb | P0 |
| **Initial CSS Bundle** | < 50kb | P1 |
| **Total Route Payload** | < 500kb | P2 |

## ⚡ Loading Performance
| Metric | Target | Description |
| :--- | :--- | :--- |
| **TTI (Time to Interactive)** | < 2.5s | Functional under 3G slow |
| **FCP (First Contentful Paint)** | < 1.2s | Layout shell visible |
| **Route Transition** | < 300ms | Navigation responsiveness |

## 🎨 Rendering Quality
| Metric | Target | Description |
| :--- | :--- | :--- |
| **Log Viewer FPS** | 60 fps | Smooth scrolling in virtualized logs |
| **Layout Shift (CLS)** | < 0.1 | Stable UI during async loading |
| **Long Tasks** | < 50ms | No main thread blocking > 50ms |

## 🛠️ Enforcement
- [ ] Add `bundlesize` check to GitHub Actions.
- [ ] Run Lighthouse in CI for every PR.
- [ ] Monitor Core Web Vitals via Telemetry.
