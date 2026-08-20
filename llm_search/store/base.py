from __future__ import annotations

from abc import ABC, abstractmethod


class VectorStore(ABC):
    @abstractmethod
    def upsert(self, items: list[dict]) -> None:
        """items: list of {"id": str, "vector": list[float], "payload": dict}."""

    @abstractmethod
    def search(self, vector: list[float], top_k: int = 5) -> list[dict]:
        """Return list of {"id", "score", "payload"} sorted by relevance desc."""

    @abstractmethod
    def count(self) -> int: ...
