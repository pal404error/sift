from __future__ import annotations

from fastapi.testclient import TestClient

from llm_search.api import app
from llm_search.config import get_settings as _gs


def test_provider_health_redacts_secrets(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "supersecret")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    _gs.cache_clear()
    with TestClient(app) as c:
        r = c.get("/health/providers")
        assert r.status_code == 200
        body = r.json()
        assert body["llm_key"] == "<set>"
        assert body["anthropic_key"] == "<unset>"
        assert body["llm_ready"] is True


def test_auth_required_blocks_without_key(monkeypatch):
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    monkeypatch.setenv("API_KEYS", "user:GOODKEY")
    _gs.cache_clear()
    with TestClient(app) as c:
        assert c.get("/ask", params={"q": "hi"}).status_code == 401
        r = c.get("/ask", params={"q": "hi"}, headers={"Authorization": "Bearer GOODKEY"})
        assert r.status_code == 200


def test_auth_wrong_key_401(monkeypatch):
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    monkeypatch.setenv("API_KEYS", "user:GOODKEY")
    _gs.cache_clear()
    with TestClient(app) as c:
        r = c.get("/ask", params={"q": "hi"}, headers={"Authorization": "Bearer WRONGKEY"})
        assert r.status_code == 401


def test_health_open_without_auth(monkeypatch):
    monkeypatch.setenv("REQUIRE_AUTH", "true")
    _gs.cache_clear()
    with TestClient(app) as c:
        assert c.get("/health").status_code == 200
