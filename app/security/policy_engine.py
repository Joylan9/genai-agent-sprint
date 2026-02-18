"""
Enterprise Policy Engine
Controls tool access, plan sanity, step limits.
"""

from typing import List, Dict


class PolicyEngine:

    MAX_STEPS = 6

    def __init__(self, allowed_tools: List[str]):
        self.allowed_tools = set(allowed_tools)

    def validate_plan(self, steps: List[Dict]):
        if not isinstance(steps, list):
            raise ValueError("Plan must be a list.")

        if len(steps) == 0:
            raise ValueError("Plan cannot be empty.")

        if len(steps) > self.MAX_STEPS:
            raise ValueError("Plan exceeds maximum step limit.")

        for step in steps:
            if "tool" not in step or "query" not in step:
                raise ValueError("Invalid plan step structure.")

            if step["tool"] not in self.allowed_tools:
                raise ValueError(f"Unauthorized tool: {step['tool']}")

            if not isinstance(step["query"], str) or len(step["query"]) > 2000:
                raise ValueError("Invalid tool query.")
