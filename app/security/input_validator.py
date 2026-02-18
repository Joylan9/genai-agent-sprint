"""
Strict user input validation layer.
Hard boundary enforcement before planner invocation.
"""

import re


class InputValidator:

    MAX_INPUT_LENGTH = 4000

    INJECTION_PATTERNS = [
        r"ignore\s+previous\s+instructions",
        r"disregard\s+all\s+rules",
        r"act\s+as\s+system",
        r"reveal\s+system\s+prompt",
        r"bypass\s+security",
        r"execute\s+command",
        r"read\s+local\s+file",
        r"print\s+environment",
        r"dump\s+memory",
    ]

    def validate(self, text: str) -> None:
        if not text or not text.strip():
            raise ValueError("Empty input.")

        if len(text) > self.MAX_INPUT_LENGTH:
            raise ValueError("Input exceeds maximum allowed length.")

        lowered = text.lower()

        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, lowered):
                raise ValueError("Prompt injection attempt detected.")
