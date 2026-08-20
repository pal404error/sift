from __future__ import annotations

import importlib.util
import os

import pytest

from llm_search.config import Settings
from llm_search.providers import (
    AnthropicLLM,
    OpenAIEmbedding,
    OpenAILLM,
    build_embedding,
    build_llm,
)

_HAS_OPENAI = bool(os.getenv("LLM_API_KEY"))
_HAS_ANTHROPIC = bool(os.getenv("ANTHROPIC_API_KEY"))
_HAS_OPENAI_PKG = importlib.util.find_spec("openai") is not None
_HAS_ANTH_PKG = importlib.util.find_spec("anthropic") is not None


@pytest.mark.integration
@pytest.mark.skipif(not _HAS_OPENAI, reason="LLM_API_KEY not set")
def test_openai_embedding_real():
    emb = OpenAIEmbedding(
        model="text-embedding-3-small", api_key=os.environ["LLM_API_KEY"], dim=1536
    )
    vec = emb.embed(["hello world"])[0]
    assert len(vec) == 1536


@pytest.mark.integration
@pytest.mark.skipif(not _HAS_OPENAI, reason="LLM_API_KEY not set")
def test_openai_llm_real():
    llm = OpenAILLM(model="gpt-4o-mini", api_key=os.environ["LLM_API_KEY"], temperature=0.0)
    out = llm.generate(system="Reply with the single word: PONG", prompt="Ping?")
    assert "PONG" in out.upper()


@pytest.mark.integration
@pytest.mark.skipif(not _HAS_ANTHROPIC, reason="ANTHROPIC_API_KEY not set")
def test_anthropic_llm_real():
    llm = AnthropicLLM(model="claude-3-5-haiku-20241022", api_key=os.environ["ANTHROPIC_API_KEY"])
    out = llm.generate(system="Reply with the single word: PONG", prompt="Ping?")
    assert "PONG" in out.upper()


@pytest.mark.integration
@pytest.mark.skipif(
    not (_HAS_OPENAI_PKG and _HAS_ANTH_PKG),
    reason="openai/anthropic packages not installed",
)
def test_factory_builds_real_providers_when_configured():
    s = Settings(embedding_provider="openai", llm_provider="anthropic")
    assert build_embedding(s) is not None
    assert build_llm(s) is not None


def test_build_embedding_fails_fast_without_openai():
    if _HAS_OPENAI_PKG:
        pytest.skip("openai installed")
    with pytest.raises(RuntimeError):
        build_embedding(Settings(embedding_provider="openai"))


def test_build_llm_fails_fast_without_anthropic():
    if _HAS_ANTH_PKG:
        pytest.skip("anthropic installed")
    with pytest.raises(RuntimeError):
        build_llm(Settings(llm_provider="anthropic"))
