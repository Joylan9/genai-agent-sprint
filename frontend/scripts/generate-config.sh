#!/usr/bin/env sh
# frontend/scripts/generate-config.sh
# Runtime config generator used by frontend Docker entrypoint.

API_BASE="${API_BASE:-http://localhost:8000}"
API_KEY="${API_KEY:-}"
APP_VERSION="${APP_VERSION:-0.0.0-LOCAL}"
REFRESH_ENDPOINT="${REFRESH_ENDPOINT:-/api/auth/refresh}"
TELEMETRY_ENDPOINT="${TELEMETRY_ENDPOINT:-}"
ENABLE_AUTH_REFRESH="${ENABLE_AUTH_REFRESH:-false}"

cat <<EOF
window.__APP_CONFIG__ = {
  VITE_API_BASE: "${API_BASE}",
  VITE_API_KEY: "${API_KEY}",
  APP_VERSION: "${APP_VERSION}",
  REFRESH_ENDPOINT: "${REFRESH_ENDPOINT}",
  TELEMETRY_ENDPOINT: "${TELEMETRY_ENDPOINT}",
  ENABLE_AUTH_REFRESH: "${ENABLE_AUTH_REFRESH}"
};
EOF
