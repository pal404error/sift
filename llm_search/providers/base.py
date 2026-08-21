from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator


class EmbeddingProvider(ABC):
    dim: int = 384

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text."""


class CachedEmbeddingProvider(EmbeddingProvider):
    """Transparent LRU-ish cache around an :class:`EmbeddingProvider`.

    Embeddings are expensive (model inference or API calls) and the same chunk
    text is embedded repeatedly across re-indexes and evaluation sweeps. This
    wrapper memoizes per-text vectors so each unique string is computed once.
    The cache is bounded; on overflow it is cleared rather than growing unbounded.
    """

    def __init__(self, delegate: EmbeddingProvider, maxsize: int = 65536) -> None:
        self._delegate = delegate
        self.dim = delegate.dim
        self._maxsize = maxsize
        self._cache: dict[str, list[float]] = {}

    def embed(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float] | None] = [None] * len(texts)
        miss_idx: list[int] = []
        miss_texts: list[str] = []
        for i, t in enumerate(texts):
            vec = self._cache.get(t)
            if vec is None:
                miss_idx.append(i)
                miss_texts.append(t)
            else:
                out[i] = vec
        if miss_idx:
            vecs = self._delegate.embed(miss_texts)
            for idx, vec in zip(miss_idx, vecs, strict=True):
                self._cache[texts[idx]] = vec
                out[idx] = vec
            if len(self._cache) > self._maxsize:
                self._cache.clear()
        return [v for v in out if v is not None]


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system: str, prompt: str) -> str:
        """Return a generated completion."""

    def stream(self, system: str, prompt: str) -> Iterator[str]:
        """Yield the answer as a sequence of text chunks.

        Default implementation yields the full `generate` output in a single chunk so
        every provider streams without overriding. Subclasses with native token streaming
        (OpenAI, Anthropic) override this for true incremental output.
        """
        yield self.generate(system, prompt)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    import math

    # strict=True so a dimension mismatch raises instead of silently truncating to the
    # shorter vector (which would yield a wrong, non-zero similarity and mis-rank results).
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
