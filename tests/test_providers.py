from __future__ import annotations

from llm_search.providers import FakeEmbedding, FakeLLM


def test_fake_embedding_deterministic_and_normalized():
    e = FakeEmbedding(dim=16)
    v1 = e.embed(["hello world"])[0]
    v2 = e.embed(["hello world"])[0]
    assert v1 == v2
    assert abs(sum(x * x for x in v1) - 1.0) < 1e-6


def test_fake_llm_grounds_on_prompt():
    llm = FakeLLM()
    out = llm.generate(system="sys", prompt="Context: cats are animals\nQuestion:?")
    assert "cats are animals" in out
