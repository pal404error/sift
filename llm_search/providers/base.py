from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    dim: int = 384

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text."""


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system: str, prompt: str) -> str:
        """Return a generated completion."""


def cosine_similarity(a: list[float], b: list[float]) -> float:
    import math

    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
