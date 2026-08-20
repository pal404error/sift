from __future__ import annotations

from llm_search.store.base import VectorStore


class QdrantStore(VectorStore):
    def __init__(
        self,
        url: str,
        collection: str,
        dim: int,
        api_key: str | None = None,
    ) -> None:
        from qdrant_client import QdrantClient

        self.collection = collection
        self.client = QdrantClient(url=url, api_key=api_key)
        self._ensure_collection(dim)

    def _ensure_collection(self, dim: int) -> None:
        from qdrant_client.models import Distance, VectorParams

        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                self.collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def upsert(self, items: list[dict]) -> None:
        from qdrant_client.models import PointStruct

        points = [
            PointStruct(id=it["id"], vector=it["vector"], payload=it["payload"]) for it in items
        ]
        if points:
            self.client.upsert(collection_name=self.collection, points=points)

    def search(self, vector: list[float], top_k: int = 5) -> list[dict]:
        res = self.client.search(collection_name=self.collection, query_vector=vector, limit=top_k)
        return [{"id": str(p.id), "score": p.score, "payload": p.payload or {}} for p in res]

    def count(self) -> int:
        return self.client.count(self.collection).count
