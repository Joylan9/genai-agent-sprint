import re


class InputValidator:
    """
    Enterprise-level input validation.
    """

    MAX_INPUT_LENGTH = 5000

    @staticmethod
    def validate_goal(goal: str) -> str:
        if not isinstance(goal, str):
            raise ValueError("Goal must be a string.")

        goal = goal.strip()

        if not goal:
            raise ValueError("Goal cannot be empty.")

        if len(goal) > InputValidator.MAX_INPUT_LENGTH:
            raise ValueError("Goal exceeds maximum allowed length.")

        # Basic injection prevention patterns
        dangerous_patterns = [
            r"(?i)ignore previous instructions",
            r"(?i)system prompt",
            r"(?i)override instructions",
            r"(?i)execute arbitrary code",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, goal):
                raise ValueError("Input contains potentially unsafe instructions.")

        return goal
