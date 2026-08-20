from __future__ import annotations

import os

from llm_search.providers.base import EmbeddingProvider, LLMProvider

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - import guard
    OpenAI = None


class OpenAIEmbedding(EmbeddingProvider):
    def __init__(self, model: str, api_key: str | None = None, dim: int = 1536) -> None:
        if OpenAI is None:
            raise RuntimeError("openai package not installed")
        self.model = model
        self.dim = dim
        self._client = OpenAI(api_key=api_key or os.getenv("LLM_API_KEY"))

    def embed(self, texts: list[str]) -> list[list[float]]:
        resp = self._client.embeddings.create(model=self.model, input=texts)
        return [d.embedding for d in resp.data]


class OpenAILLM(LLMProvider):
    def __init__(self, model: str, api_key: str | None = None, temperature: float = 0.0) -> None:
        if OpenAI is None:
            raise RuntimeError("openai package not installed")
        self.model = model
        self.temperature = temperature
        self._client = OpenAI(api_key=api_key or os.getenv("LLM_API_KEY"))

    def generate(self, system: str, prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
        return resp.choices[0].message.content or ""
