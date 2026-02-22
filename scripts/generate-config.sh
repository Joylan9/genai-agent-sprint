#!/usr/bin/env bash
# generate-config.sh
# Usage: REFRESH_ENDPOINT=/api/auth/refresh TELEMETRY_ENDPOINT=https://telemetry.example.com API_BASE=https://api.example.com ./generate-config.sh > frontend/public/config.js

API_BASE="${API_BASE:-http://localhost:8000}"
API_KEY="${API_KEY:-}"
APP_VERSION="${APP_VERSION:-0.0.0-LOCAL}"
REFRESH_ENDPOINT="${REFRESH_ENDPOINT:-/api/auth/refresh}"
TELEMETRY_ENDPOINT="${TELEMETRY_ENDPOINT:-}"

cat <<EOF
window.__APP_CONFIG__ = {
  VITE_API_BASE: "${API_BASE}",
  VITE_API_KEY: "${API_KEY}",
  APP_VERSION: "${APP_VERSION}",
  REFRESH_ENDPOINT: "${REFRESH_ENDPOINT}",
  TELEMETRY_ENDPOINT: "${TELEMETRY_ENDPOINT}"
};
EOF
