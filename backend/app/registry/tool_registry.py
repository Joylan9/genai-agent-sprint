"""
app/registry/tool_registry.py
Enterprise tool registry implementation.
"""

from typing import Dict
from ..tools.tools import BaseTool  # Correct import


class ToolRegistry:
    """
    Simple registry that holds tool instances keyed by tool.name.

    Tools must implement the BaseTool contract (name, execute(...)).
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if not hasattr(tool, "name") or not isinstance(tool.name, str):
            raise ValueError("Tool must have a string 'name' attribute.")
        self._tools[tool.name] = tool

    def get(self, tool_name: str) -> BaseTool:
        if tool_name not in self._tools:
            raise KeyError(f"Tool '{tool_name}' not registered.")
        return self._tools[tool_name]

    def list_tools(self):
        return list(self._tools.keys())
