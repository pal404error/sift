from __future__ import annotations

from llm_search.providers.base import cosine_similarity
from llm_search.store.base import VectorStore


class InMemoryStore(VectorStore):
    def __init__(self) -> None:
        self._items: list[dict] = []

    def upsert(self, items: list[dict]) -> None:
        seen = {it["id"] for it in items}
        self._items = [it for it in self._items if it["id"] not in seen]
        self._items.extend(items)

    def search(self, vector: list[float], top_k: int = 5) -> list[dict]:
        scored = [
            {
                "id": it["id"],
                "score": cosine_similarity(vector, it["vector"]),
                "payload": it["payload"],
            }
            for it in self._items
        ]
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def count(self) -> int:
        return len(self._items)
