# Reliability and Resilience

The Enterprise AI Agent Engine uses several patterns to ensure reliability:
1. Circuit Breakers: Protect external services like Ollama and Web Search from cascading failures.
2. Retries: Exponential backoff for transient network issues.
3. Timeouts: Enforce strict execution limits on all tool calls.
4. Fallbacks: If RAG search confidence is low, the system automatically falls back to Web Search.
