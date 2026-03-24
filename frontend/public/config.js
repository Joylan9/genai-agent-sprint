// public/config.js
// Loaded before the app bootstraps to allow runtime config w/o rebuild.
// Example values; override in your hosting environment (nginx, CDN or cloud).
window.__APP_CONFIG__ = {
    VITE_API_BASE: "http://localhost:8000",
    APP_VERSION: "1.0.4-PROD", // pipeline should replace with actual version
    FEATURE_FLAGS_ENDPOINT: "/api/feature-flags",
    FRONTEND_HEALTH_ENDPOINT: "/health-frontend.json",
    ENABLE_AUTH_REFRESH: "true",
};
