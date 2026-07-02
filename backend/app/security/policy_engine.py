import re
from typing import List, Dict


class PolicyViolationError(Exception):
    """Exception raised for policy violations."""
    pass


class PolicyEngine:
    """
    Responsibilities:
    - Control tool whitelist
    - Enforce step limits
    - Detect and redact sensitive data (PII, API keys)
    """

    MAX_STEPS = 6

    # Pattern for sensitive data (API keys, passwords, etc)
    SENSITIVE_PATTERNS = [
        r"(?i)api_key[:=]\s*[a-zA-Z0-9-]{16,}",
        r"(?i)bearer\s+[a-zA-Z0-9.-]{16,}",
        r"(?i)ghp_[a-zA-Z0-9]{36}",
        r"(?i)sk-[a-zA-Z0-9]{48}",
        r"(?i)password[:=]\s*[^\s,]{4,}",
        r"(?i)aws_access_key_id[:=]\s*[A-Z0-9]{20}",
        r"(?i)aws_secret_access_key[:=]\s*[a-zA-Z0-9/+=]{40}",
    ]

    def __init__(self, allowed_tools: List[str]):
        self.allowed_tools = set(allowed_tools)
        self._compiled_patterns = [
            re.compile(p) for p in self.SENSITIVE_PATTERNS
        ]

    def validate_plan(self, steps: List[Dict]):
        if not isinstance(steps, list):
            raise PolicyViolationError("Plan must be a list.")

        if len(steps) == 0:
            raise PolicyViolationError("Plan cannot be empty.")

        if len(steps) > self.MAX_STEPS:
            raise PolicyViolationError(
                f"Plan exceeds maximum step limit of {self.MAX_STEPS}."
            )

        for step in steps:
            if "tool" not in step or "query" not in step:
                raise PolicyViolationError("Invalid plan step structure.")

            if step["tool"] not in self.allowed_tools:
                raise PolicyViolationError(f"Unauthorized tool: {step['tool']}")

            if not isinstance(step["query"], str) or len(step["query"]) > 2000:
                raise PolicyViolationError("Invalid tool query.")

    def validate_output(self, text: str):
        """Raise error if sensitive data is found in text."""
        if not text:
            return

        for pattern in self._compiled_patterns:
            if pattern.search(text):
                raise PolicyViolationError(
                    "Output blocked: sensitive data pattern detected."
                )

    def redact(self, text: str) -> str:
        """Replace sensitive patterns with [REDACTED]."""
        if not text:
            return text

        redacted_text = text
        for pattern in self._compiled_patterns:
            redacted_text = pattern.sub("[REDACTED]", redacted_text)

        return redacted_text
