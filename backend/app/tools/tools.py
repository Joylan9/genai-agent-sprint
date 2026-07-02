"""
app/tools/tools.py
Base tool contract for registry compatibility.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    name: str

    @abstractmethod
    def execute(self, step: Dict[str, Any]) -> Dict[str, Any]:
        pass
