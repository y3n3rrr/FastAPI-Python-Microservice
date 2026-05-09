from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AssistantAgent(ABC):
    name: str

    @abstractmethod
    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
