from __future__ import annotations

from llm_search.engine import SearchEngine
from llm_search.providers import FakeEmbedding, FakeLLM
from llm_search.store import InMemoryStore


def _eng() -> SearchEngine:
    return SearchEngine(
        store=InMemoryStore(),
        embedding=FakeEmbedding(dim=32),
        llm=FakeLLM(),
    )


def test_ask_with_hyde_returns_grounded_answer():
    eng = _eng()
    eng.store.upsert(
        [
            {
                "id": "doc1",
                "vector": eng.embedding.embed(["the capital of France is Paris"])[0],
                "payload": {
                    "doc_url": "http://example.com/france",
                    "doc_title": "France",
                    "index": 0,
                    "text": "The capital of France is Paris.",
                },
            }
        ]
    )
    out = eng.ask("What is the capital of France?", use_hyde=True)
    assert "Paris" in out["answer"]
    assert "http://example.com/france" in out["sources"]


def test_hyde_toggle_via_settings():
    eng = _eng()
    eng.settings.use_hyde = True
    # Should not raise and should still produce an answer structure.
    out = eng.ask("anything at all")
    assert "answer" in out and "sources" in out
