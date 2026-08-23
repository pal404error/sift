from __future__ import annotations

from typing import Any

import numpy as np

from llm_search.store.base import VectorStore


def _normalize(vector: list[float]) -> np.ndarray:
    """L2-normalize so inner product equals cosine similarity (matching InMemoryStore)."""
    a = np.asarray(vector, dtype=np.float32)
    norm = float(np.linalg.norm(a))
    if norm == 0.0:
        return a
    return a / norm


class FaissStore(VectorStore):
    """Optional ANN/in-memory-exact vector store backed by FAISS (``IndexFlatIP``).

    Vectors are L2-normalized on write and query, so the inner-product score is exactly
    cosine similarity — identical relevance to :class:`InMemoryStore`, but the scan runs in
    optimized C code and scales to large corpora far better than the pure-Python O(n) path.

    This is an OPTIONAL backend: ``faiss`` is not a base dependency. Install with
    ``pip install "llm-search[faiss]"`` (or ``pip install faiss-cpu``) and select it via
    ``SIFT_VECTOR_STORE=faiss``. The index dimension is inferred from the first upserted
    vector (all subsequent vectors must share that dimension).
    """

    def __init__(self, dim: int = 0) -> None:
        try:
            import faiss  # noqa: F401  (validate the optional dependency is present)
        except ImportError as e:  # pragma: no cover - exercised only without faiss
            raise RuntimeError(
                "faiss is required for SIFT_VECTOR_STORE=faiss. "
                "Install it with: pip install faiss-cpu"
            ) from e
        self.dim = dim
        self._index: Any = None  # built lazily once we know the dimension
        self._payloads: dict[int, dict] = {}
        self._str_to_int: dict[str, int] = {}
        self._int_to_str: dict[int, str] = {}
        self._next: int = 0

    def _ensure(self, dim: int) -> None:
        if self._index is None:
            import faiss

            self.dim = dim
            self._index = faiss.IndexIDMap(faiss.IndexFlatIP(dim))

    def upsert(self, items: list[dict]) -> None:
        if not items:
            return
        self._ensure(len(items[0]["vector"]))
        assert self._index is not None

        # Replace any previously-indexed ids (IndexIDMap has no in-place update).
        remove_ids = [iid for it in items if (iid := self._str_to_int.get(it["id"])) is not None]
        if remove_ids:
            self._index.remove_ids(np.array(remove_ids, dtype=np.int64))
            for iid in remove_ids:
                self._payloads.pop(iid, None)
                self._int_to_str.pop(iid, None)

        vectors: list[np.ndarray] = []
        int_ids: list[int] = []
        for it in items:
            iid = self._str_to_int.get(it["id"])
            if iid is None:
                iid = self._next
                self._next += 1
                self._str_to_int[it["id"]] = iid
            self._int_to_str[iid] = it["id"]
            self._payloads[iid] = it["payload"]
            vectors.append(_normalize(it["vector"]))
            int_ids.append(iid)

        arr = np.stack(vectors).astype(np.float32)
        self._index.add_with_ids(arr, np.array(int_ids, dtype=np.int64))

    def search(self, vector: list[float], top_k: int = 5) -> list[dict]:
        if self._index is None or self._index.ntotal == 0:
            return []
        q = _normalize(vector).reshape(1, -1).astype(np.float32)
        scores, idxs = self._index.search(q, top_k)
        out: list[dict] = []
        for score, iid in zip(scores[0], idxs[0], strict=True):
            if iid == -1:
                continue
            out.append(
                {
                    "id": self._int_to_str[int(iid)],
                    "score": float(score),
                    "payload": self._payloads[int(iid)],
                }
            )
        return out

    def count(self) -> int:
        return int(self._index.ntotal) if self._index is not None else 0
