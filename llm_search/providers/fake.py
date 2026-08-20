from __future__ import annotations

import hashlib
import math
import re

from llm_search.providers.base import EmbeddingProvider, LLMProvider


def _hash_vec(text: str, dim: int) -> list[float]:
    """Deterministic lexical pseudo-embedding for tests/dev.

    Hashes tokens into a bag-of-words vector, so cosine similarity tracks token
    overlap. This makes offline retrieval + eval produce sensible (non-random)
    rankings without any network or API keys. NOT semantic — swap in a real
    provider for production relevance.
    """
    vec = [0.0] * dim
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    if not tokens:
        tokens = ["<empty>"]
    for tok in tokens:
        h = hashlib.sha256(tok.encode()).digest()
        idx = int.from_bytes(h[:4], "big") % dim
        vec[idx] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


class FakeEmbedding(EmbeddingProvider):
    def __init__(self, dim: int = 384) -> None:
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [_hash_vec(t, self.dim) for t in texts]


class FakeLLM(LLMProvider):
    """Deterministic stand-in: echoes a grounded stub from the prompt."""

    def generate(self, system: str, prompt: str) -> str:
        context = prompt.split("Context:", 1)[-1].strip()
        snippet = context[:120].replace("\n", " ")
        return f"[fake-answer] Based on the provided context: {snippet} (system={system[:20]!r})"
