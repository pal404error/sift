from __future__ import annotations

from llm_search.engine import SearchEngine


def test_ingest_then_ask_returns_grounded_answer(engine: SearchEngine):
    # craft a document-like payload via direct store upsert to avoid network
    engine.store.upsert(
        [
            {
                "id": "doc1",
                "vector": engine.embedding.embed(["the capital of France is Paris"])[0],
                "payload": {
                    "doc_url": "http://example.com/france",
                    "doc_title": "France",
                    "index": 0,
                    "text": "The capital of France is Paris.",
                },
            }
        ]
    )
    out = engine.ask("What is the capital of France?")
    assert "Paris" in out["answer"]
    assert "http://example.com/france" in out["sources"]


def test_search_returns_ranked_results(engine: SearchEngine):
    engine.store.upsert(
        [
            {
                "id": "x",
                "vector": engine.embedding.embed(["machine learning models"])[0],
                "payload": {"doc_url": "u", "doc_title": "t", "index": 0, "text": "ml"},
            }
        ]
    )
    res = engine.search("machine learning models", top_k=3)
    assert res and res[0]["id"] == "x"
