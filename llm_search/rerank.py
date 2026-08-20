from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Callable

from llm_search.config import Settings, get_settings


class Reranker(ABC):
    @abstractmethod
    def rerank(self, query: str, items: list[dict], top_n: int) -> list[dict]:
        """Reorder retrieved items (each with 'payload' containing 'text')."""


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class LexicalReranker(Reranker):
    """TF-style overlap score between query and chunk text."""

    def rerank(self, query: str, items: list[dict], top_n: int) -> list[dict]:
        q_tokens = _tokens(query)
        q_set = set(q_tokens)
        if not q_set:
            return items[:top_n]
        scored = []
        for it in items:
            text = it.get("payload", {}).get("text", "")
            t_tokens = _tokens(text)
            overlap = sum(1 for t in t_tokens if t in q_set)
            # normalize by chunk length to avoid favoring only long chunks
            norm = overlap / (len(t_tokens) + 1)
            scored.append((norm, it))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [it for _, it in scored[:top_n]]


class FakeReranker(Reranker):
    """Deterministic pass-through (used in tests)."""

    def rerank(self, query: str, items: list[dict], top_n: int) -> list[dict]:
        return items[:top_n]


class CrossEncoderReranker(Reranker):
    """Precision reranker using a cross-encoder scorer over (query, chunk) pairs.

    `scorer` is injectable for tests/air-gapped use. If None, lazily loads a
    sentence-transformers CrossEncoder (guarded; optional dependency).
    """

    def __init__(
        self,
        model_name: str = "",
        scorer: Callable[[list[tuple[str, str]]], list[float]] | None = None,
    ) -> None:
        self.model_name = model_name
        self._scorer = scorer
        self._model = None

    def _scores(self, pairs: list[tuple[str, str]]) -> list[float]:
        if self._scorer is not None:
            return self._scorer(pairs)
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
            except ImportError as e:  # pragma: no cover
                raise RuntimeError(
                    "sentence-transformers required for cross-encoder reranker"
                ) from e
            self._model = CrossEncoder(self.model_name or "cross-encoder/ms-marco-MiniLM-L-6-v2")
        return [float(s) for s in self._model.predict(pairs)]  # type: ignore[attr-defined]

    def rerank(self, query: str, items: list[dict], top_n: int) -> list[dict]:
        if not items:
            return []
        pairs = [(query, it.get("payload", {}).get("text", "")) for it in items]
        scores = self._scores(pairs)
        order = sorted(range(len(items)), key=lambda i: scores[i], reverse=True)
        return [items[i] for i in order[:top_n]]


def build_reranker(settings: Settings | None = None) -> Reranker:
    s = settings or get_settings()
    name = s.reranker
    if name == "none":
        return FakeReranker()
    if name == "fake":
        return FakeReranker()
    if name == "lexical":
        return LexicalReranker()
    if name == "cross-encoder":
        return CrossEncoderReranker(model_name=s.rerank_model)
    raise ValueError(f"Unknown reranker: {name}")
