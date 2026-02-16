from typing import Dict
from tools.base_tool import BaseTool


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get(self, tool_name: str) -> BaseTool:
        if tool_name not in self._tools:
            raise ValueError(f"Tool '{tool_name}' not registered.")
        return self._tools[tool_name]

    def list_tools(self):
        return list(self._tools.keys())
