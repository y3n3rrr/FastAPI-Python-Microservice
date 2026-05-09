from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PlannerStep(BaseModel):
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class PlannerOutput(BaseModel):
    intent: str = "unknown"
    steps: list[PlannerStep] = Field(default_factory=list)


class ToolExecutionResult(BaseModel):
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    success: bool
    data: Any = None
    error: str | None = None


class ValidationOutput(BaseModel):
    is_valid: bool
    issues: list[str] = Field(default_factory=list)
    results: list[ToolExecutionResult] = Field(default_factory=list)
