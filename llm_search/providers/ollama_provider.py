from __future__ import annotations

import httpx

from llm_search.providers.base import EmbeddingProvider, LLMProvider


class OllamaEmbedding(EmbeddingProvider):
    def __init__(self, base_url: str, model: str, dim: int = 384) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for text in texts:
            r = httpx.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=30,
            )
            r.raise_for_status()
            out.append(r.json()["embedding"])
        return out


class OllamaLLM(LLMProvider):
    def __init__(self, base_url: str, model: str, temperature: float = 0.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature

    def generate(self, system: str, prompt: str) -> str:
        r = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "system": system,
                "prompt": prompt,
                "temperature": self.temperature,
                "stream": False,
            },
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["response"]
