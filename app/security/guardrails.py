"""
Enterprise Adversarial Guardrails Layer
Hard-block security enforcement.
"""

import re
from typing import List


class Guardrails:

    # ---------------------------
    # Prompt Injection Patterns
    # ---------------------------
    INJECTION_PATTERNS = [
        r"ignore\s+previous\s+instructions",
        r"disregard\s+all\s+rules",
        r"act\s+as\s+system",
        r"you\s+are\s+chatgpt",
        r"reveal\s+system\s+prompt",
        r"show\s+hidden\s+instructions",
        r"bypass\s+security",
        r"execute\s+command",
        r"open\s+file",
        r"read\s+local",
        r"send\s+api\s+key",
        r"print\s+environment",
        r"dump\s+memory",
    ]

    # ---------------------------
    # Tool Injection Patterns
    # ---------------------------
    TOOL_OUTPUT_BLOCK_PATTERNS = [
        r"ignore\s+all\s+previous",
        r"system\s+override",
        r"you\s+must\s+now",
        r"run\s+this\s+code",
        r"download\s+this",
        r"click\s+this",
        r"exfiltrate",
        r"steal",
    ]

    # ---------------------------
    # Sensitive Leak Patterns
    # ---------------------------
    SENSITIVE_PATTERNS = [
        r"api\s*key",
        r"secret",
        r"private\s*key",
        r"system\s*prompt",
        r"environment\s*variable",
    ]

    # ---------------------------
    # User Input Validation
    # ---------------------------
    def validate_user_input(self, text: str) -> None:
        lowered = text.lower()
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, lowered):
                raise ValueError("Security violation: prompt injection detected.")

    # ---------------------------
    # Tool Output Sanitization
    # ---------------------------
    def sanitize_tool_output(self, text: str) -> str:
        lowered = text.lower()
        for pattern in self.TOOL_OUTPUT_BLOCK_PATTERNS:
            if re.search(pattern, lowered):
                raise ValueError("Security violation: malicious tool output detected.")
        return text

    # ---------------------------
    # Memory Write Protection
    # ---------------------------
    def validate_memory_write(self, text: str) -> None:
        lowered = text.lower()
        if "from now on" in lowered or "always answer" in lowered:
            raise ValueError("Security violation: memory poisoning attempt detected.")

    # ---------------------------
    # Final Response Protection
    # ---------------------------
    def validate_final_answer(self, text: str) -> None:
        lowered = text.lower()
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, lowered):
                raise ValueError("Security violation: sensitive data leakage detected.")
