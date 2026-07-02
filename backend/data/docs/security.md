# Security and Guardrails

The system implements multi-layered security:
1. Input Validation: Detects prompt injection and malicious payloads.
2. Policy Engine: Enforces tool whitelists and step limits.
3. Redaction: Automatically detects and hides sensitive data (API keys, PII) in responses.
4. Memory Protection: Prevents memory poisoning attempts.
