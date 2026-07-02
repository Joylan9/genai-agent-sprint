# Secrets Management

Best practices for managing sensitive configuration:
- Environment Variables: All credentials stored in .env (and not committed).
- Env Guards: App fails to start if critical keys (OLLAMA_HOST, SERPAPI_KEY) are missing.
- Rotation: Support for periodic API key rotation without downtime.
- Minimal Scoping: Service accounts with least-privilege permissions.
