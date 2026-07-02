"""
Enterprise Adversarial Guardrails Layer
Hard-block security enforcement.
"""

import re
from typing import List, Optional


class Guardrails:
    """
    Production-ready guardrails.

    Responsibilities:
    - Prompt injection detection (user input)
    - Per-step/tool output sanitization
    - Plan validation (step count, tool whitelist, step shape)
    - Memory-write protection (poisoning detection)
    - Final answer sensitive-data leakage detection

    Usage:
    guard = Guardrails(allowed_tools=["tool_a","tool_b"])
    guard.validate_user_input(goal)
    guard.validate_plan(steps)
    guard.sanitize_tool_output(some_text)
    guard.validate_final_answer(answer)
    guard.validate_memory_write(answer)
    """

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
    # Tool Output Block Patterns
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
        r"aws_access_key_id",
        r"aws_secret_access_key",
        r"password",
        r"passwd",
        r"authorization\s*:",
    ]

    # ---------------------------
    # Limits / Defaults
    # ---------------------------
    MAX_PLAN_STEPS = 12
    MAX_STEP_QUERY_LENGTH = 2000
    MAX_INPUT_LENGTH = 16000

    def __init__(self, allowed_tools: Optional[List[str]] = None):
        self.allowed_tools = set(allowed_tools or [])

    # ---------------------------
    # User Input Validation
    # ---------------------------
    def validate_user_input(self, text: str) -> None:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Security violation: empty or invalid input.")

        if len(text) > self.MAX_INPUT_LENGTH:
            raise ValueError("Security violation: input exceeds maximum allowed length.")

        lowered = text.lower()
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, lowered):
                raise ValueError("Security violation: prompt injection detected.")

    # ---------------------------
    # Plan Validation
    # ---------------------------
    def validate_plan(self, steps) -> None:
        """
        Basic plan sanity checks:
        - steps is a list of dicts
        - number of steps within MAX_PLAN_STEPS
        - each step has 'tool' and 'query'
        - tool is whitelisted (if whitelist provided)
        - query length within limits
        """
        if not isinstance(steps, list):
            raise ValueError("Security violation: plan must be a list of steps.")

        if len(steps) == 0:
            raise ValueError("Security violation: plan cannot be empty.")

        if len(steps) > self.MAX_PLAN_STEPS:
            raise ValueError("Security violation: plan exceeds maximum allowed steps.")

        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                raise ValueError(f"Security violation: step {idx} invalid (not a dict).")

            tool = step.get("tool")
            query = step.get("query")

            if not tool or not isinstance(tool, str):
                raise ValueError(f"Security violation: step {idx} missing or invalid 'tool'.")

            if not query or not isinstance(query, str):
                raise ValueError(f"Security violation: step {idx} missing or invalid 'query'.")

            if len(query) > self.MAX_STEP_QUERY_LENGTH:
                raise ValueError(f"Security violation: step {idx} query too long.")

            if self.allowed_tools and tool not in self.allowed_tools:
                raise ValueError(f"Security violation: unauthorized tool '{tool}' in step {idx}.")

    # ---------------------------
    # Tool Output Sanitization
    # ---------------------------
    def sanitize_tool_output(self, text: str) -> str:
        """
        Inspect tool output for patterns that indicate an attempt to override control flow,
        execute code, or exfiltrate secrets. If pattern matches, raise exception (hard block).
        Otherwise return the original text unchanged.
        """
        if not isinstance(text, str):
            # non-string outputs are allowed but convert to str for scanning
            text = str(text)

        lowered = text.lower()
        for pattern in self.TOOL_OUTPUT_BLOCK_PATTERNS:
            if re.search(pattern, lowered):
                raise ValueError("Security violation: malicious tool output detected.")

        # Also check for direct sensitive tokens leaking
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, lowered):
                raise ValueError("Security violation: tool output contains sensitive data.")

        return text

    # ---------------------------
    # Memory Write Protection
    # ---------------------------
    def validate_memory_write(self, text: str) -> None:
        """
        Prevent memory poisoning attempts such as "from now on ..." or "always answer ..."
        or explicit instruction to modify agent behavior permanently.
        """
        if not isinstance(text, str):
            return

        lowered = text.lower()
        poison_indicators = [
            "from now on",
            "always answer",
            "always respond",
            "remember that",
            "do not forget",
            "store this permanently",
            "make this default",
        ]
        for indicator in poison_indicators:
            if indicator in lowered:
                raise ValueError("Security violation: memory poisoning attempt detected.")

    # ---------------------------
    # Final Response Protection
    # ---------------------------
    def validate_final_answer(self, text: str) -> None:
        """
        Scan final answer for sensitive token leakage. Hard block on detection.
        """
        if not isinstance(text, str):
            text = str(text)

        lowered = text.lower()
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, lowered):
                raise ValueError("Security violation: sensitive data leakage detected.")
