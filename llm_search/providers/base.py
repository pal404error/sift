from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator


class EmbeddingProvider(ABC):
    dim: int = 384

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text."""


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

    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
