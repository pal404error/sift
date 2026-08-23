from __future__ import annotations

from llm_search.config import Settings, get_settings
from llm_search.store.base import VectorStore
from llm_search.store.faiss_store import FaissStore
from llm_search.store.memory import InMemoryStore
from llm_search.store.qdrant import QdrantStore


def build_store(settings: Settings | None = None) -> VectorStore:
    s = settings or get_settings()
    if s.vector_store == "qdrant":
        return QdrantStore(
            url=s.qdrant_url,
            collection=s.qdrant_collection,
            dim=s.vector_dim,
            api_key=s.qdrant_api_key,
        )
    if s.vector_store == "faiss":
        return FaissStore(dim=s.vector_dim)
    return InMemoryStore()
