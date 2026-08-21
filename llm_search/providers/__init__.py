from __future__ import annotations

from llm_search.config import Settings, get_settings
from llm_search.providers.anthropic_provider import AnthropicLLM
from llm_search.providers.base import EmbeddingProvider, LLMProvider
from llm_search.providers.fake import FakeEmbedding, FakeLLM
from llm_search.providers.local import LocalEmbedding
from llm_search.providers.ollama_provider import OllamaEmbedding, OllamaLLM
from llm_search.providers.openai_provider import OpenAIEmbedding, OpenAILLM

__all__ = [
    "EmbeddingProvider",
    "LLMProvider",
    "FakeEmbedding",
    "FakeLLM",
    "LocalEmbedding",
    "OpenAIEmbedding",
    "OpenAILLM",
    "AnthropicLLM",
    "OllamaEmbedding",
    "OllamaLLM",
    "build_embedding",
    "build_llm",
]


def build_embedding(settings: Settings | None = None) -> EmbeddingProvider:
    s = settings or get_settings()
    name = s.embedding_provider
    if name == "fake":
        return FakeEmbedding(dim=s.embedding_dim)
    if name == "local":
        return LocalEmbedding(settings=s)
    if name == "openai":
        return OpenAIEmbedding(model=s.embedding_model, api_key=s.llm_api_key, dim=s.embedding_dim)
    if name == "ollama":
        return OllamaEmbedding(
            base_url=s.ollama_embed_url, model=s.embedding_model, dim=s.embedding_dim
        )
    raise ValueError(f"Unknown embedding_provider: {name}")


def build_llm(settings: Settings | None = None) -> LLMProvider:
    s = settings or get_settings()
    name = s.llm_provider
    if name == "fake":
        return FakeLLM()
    if name == "openai":
        return OpenAILLM(model=s.llm_model, api_key=s.llm_api_key, temperature=s.llm_temperature)
    if name == "anthropic":
        return AnthropicLLM(
            model=s.llm_model, api_key=s.anthropic_api_key, temperature=s.llm_temperature
        )
    if name == "ollama":
        return OllamaLLM(base_url=s.ollama_url, model=s.llm_model, temperature=s.llm_temperature)
    raise ValueError(f"Unknown llm_provider: {name}")
