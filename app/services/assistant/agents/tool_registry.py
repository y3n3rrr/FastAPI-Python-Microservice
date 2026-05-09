from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


ToolHandler = Callable[[dict[str, Any]], Any]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, str]
    handler: ToolHandler

    def planner_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class ToolRegistry:
    def __init__(self, tools: list[ToolSpec]) -> None:
        self._tools: dict[str, ToolSpec] = {tool.name: tool for tool in tools}

    def list_for_planner(self) -> list[dict[str, Any]]:
        return [tool.planner_dict() for tool in self._tools.values()]

    def has_tool(self, name: str) -> bool:
        return name in self._tools

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        tool = self._tools.get(name)
        if tool is None:
            raise ValueError(f"Unknown tool: {name}")
        return tool.handler(arguments)
