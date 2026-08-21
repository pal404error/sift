from __future__ import annotations

import json

from llm_search.engine import SearchEngine
from llm_search.providers import FakeEmbedding, FakeLLM
from llm_search.store import InMemoryStore


def _eng() -> SearchEngine:
    return SearchEngine(
        store=InMemoryStore(),
        embedding=FakeEmbedding(dim=32),
        llm=FakeLLM(),
    )


def test_provider_stream_yields_full_text_by_default():
    chunks = list(FakeLLM().stream(system="s", prompt="p"))
    assert chunks and "".join(chunks)  # default fallback yields the full answer


def test_ask_stream_emits_sources_then_tokens():
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
    events = list(eng.ask_stream("What is the capital of France?"))
    assert events[0]["type"] == "sources"
    assert "http://example.com/france" in events[0]["sources"]
    tokens = "".join(e["text"] for e in events if e["type"] == "token")
    assert "Paris" in tokens


def test_ask_stream_no_context_event():
    eng = _eng()
    events = list(eng.ask_stream("anything"))
    assert events[0]["type"] == "sources"
    assert events[0]["sources"] == []
    assert any(e["type"] == "token" for e in events)


def test_api_ask_stream_returns_sse():
    from fastapi.testclient import TestClient

    from llm_search.api import app, get_engine

    get_engine().store.upsert(
        [
            {
                "id": "doc1",
                "vector": get_engine().embedding.embed(["the capital of France is Paris"])[0],
                "payload": {
                    "doc_url": "http://example.com/france",
                    "doc_title": "France",
                    "index": 0,
                    "text": "The capital of France is Paris.",
                },
            }
        ]
    )
    client = TestClient(app)
    resp = client.get("/ask/stream", params={"q": "What is the capital of France?"})
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    body = resp.text
    assert "data: " in body
    # at least one event parses and carries the source/ token shape
    first = next(line for line in body.splitlines() if line.startswith("data: "))
    evt = json.loads(first.removeprefix("data: "))
    assert evt["type"] in {"sources", "token"}
