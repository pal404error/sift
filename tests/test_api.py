from __future__ import annotations

from fastapi.testclient import TestClient

from llm_search.api import app


def test_health_live():
    with TestClient(app) as c:
        r = c.get("/health/live")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


def test_health_ready(monkeypatch):
    from llm_search.api import get_engine

    # Ensure engine is up (InMemoryStore doesn't fail on count)
    eng = get_engine()

    with TestClient(app) as c:
        r = c.get("/health/ready")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

        # Simulate store missing
        def fake_count():
            raise RuntimeError("Store is down")

        monkeypatch.setattr(eng.store, "count", fake_count)

        r2 = c.get("/health/ready")
        assert r2.status_code == 503
        assert r2.json()["status"] == "error"


def test_metrics():
    with TestClient(app) as c:
        r = c.get("/metrics")
        assert r.status_code == 200
        initial_content = r.text

        c.get("/health/live")

        r2 = c.get("/metrics")
        assert r2.status_code == 200

        def get_total(text):
            for line in text.splitlines():
                if line.startswith("sift_requests_total"):
                    return int(line.split()[1])
            return -1

        assert get_total(r2.text) > get_total(initial_content)


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
