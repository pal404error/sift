from __future__ import annotations

from fastapi.testclient import TestClient

from llm_search.api import app


def test_health():
    with TestClient(app) as c:
        r = c.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


def test_ask_via_api():
    with TestClient(app) as c:
        # seed via internal engine, then query
        from llm_search.api import get_engine

        eng = get_engine()
        eng.store.upsert(
            [
                {
                    "id": "d1",
                    "vector": eng.embedding.embed(["the sky is blue"])[0],
                    "payload": {
                        "doc_url": "http://example.com/sky",
                        "doc_title": "Sky",
                        "index": 0,
                        "text": "The sky is blue.",
                    },
                }
            ]
        )
        r = c.get("/ask", params={"q": "what color is the sky?"})
        assert r.status_code == 200
        assert "blue" in r.json()["answer"]
