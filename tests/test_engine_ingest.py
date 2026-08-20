from __future__ import annotations

from llm_search.engine import SearchEngine


def test_ingest_url_chunks_and_stores(engine: SearchEngine, monkeypatch):
    import llm_search.ingest.fetch as fmod

    class _Resp:
        text = "<html><body>" + "<p>alpha beta gamma</p>" * 200 + "</body></html>"
        status_code = 200
        headers: dict[str, str] = {}

        def raise_for_status(self):
            return None

    monkeypatch.setattr(fmod.httpx, "get", lambda *a, **k: _Resp())
    monkeypatch.setattr(fmod, "robots_allowed", lambda url: True)
    n = engine.ingest_url("http://example.com/page")
    assert n > 0
    assert engine.store.count() == n


def test_ask_without_context_returns_empty(engine: SearchEngine):
    out = engine.ask("anything at all")
    assert out["answer"] == "No relevant context found."
    assert out["sources"] == []


def test_search_returns_reranked_top_k(engine: SearchEngine):
    # two chunks; lexical reranker should keep both for top_k=2
    engine.store.upsert(
        [
            {
                "id": "a",
                "vector": engine.embedding.embed(["machine learning"])[0],
                "payload": {"doc_url": "u1", "doc_title": "t", "index": 0, "text": "ml rocks"},
            },
            {
                "id": "b",
                "vector": engine.embedding.embed(["machine learning"])[0],
                "payload": {"doc_url": "u2", "doc_title": "t", "index": 0, "text": "ml also good"},
            },
        ]
    )
    res = engine.search("machine learning", top_k=2)
    assert [r["id"] for r in res] == ["a", "b"]
