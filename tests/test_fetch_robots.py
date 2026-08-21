from __future__ import annotations

import pytest

from llm_search.ingest import fetch
from llm_search.ingest.fetch import RobotDisallowed, fetch_url, throttle

_HTML = (
    "<html><head><title>Hi</title></head><body>"
    "<script>bad()</script><p>Hello world</p></body></html>"
)


class _Resp:
    text = _HTML
    status_code = 200
    headers: dict[str, str] = {}

    def raise_for_status(self):
        return None


def test_fetch_strips_scripts_and_extracts_text(monkeypatch):
    monkeypatch.setattr(fetch.httpx, "get", lambda *a, **k: _Resp())
    monkeypatch.setattr(fetch, "robots_allowed", lambda url: True)
    monkeypatch.setattr(fetch, "_host_is_safe", lambda url: True)
    doc = fetch_url("http://example.com/p", respect_robots=True)
    assert "Hello world" in doc.text
    assert "bad()" not in doc.text
    assert doc.title == "Hi"


def test_fetch_respects_robots(monkeypatch):
    monkeypatch.setattr(fetch.httpx, "get", lambda *a, **k: _Resp())
    monkeypatch.setattr(fetch, "robots_allowed", lambda url: False)
    monkeypatch.setattr(fetch, "_host_is_safe", lambda url: True)
    with pytest.raises(RobotDisallowed):
        fetch_url("http://example.com/p", respect_robots=True)


def test_throttle_sleeps_when_too_soon():
    sleeps: list[float] = []
    # last seen at t=0, now=0.5, interval=1 -> should sleep 0.5
    fetch._HOST_LAST_SEEN["h"] = 0.0
    throttle("h", 1.0, sleep=lambda s: sleeps.append(s), now=lambda: 0.5)
    assert sleeps == [0.5]


def test_robots_allowed_real_path(monkeypatch):
    import llm_search.ingest.fetch as fmod

    class _RP:
        def set_url(self, url):
            pass

        def read(self):
            pass

        def can_fetch(self, ua, url):
            return True

    monkeypatch.setattr(fmod.urllib.robotparser, "RobotFileParser", lambda: _RP())
    fmod._ROBOTS_CACHE.clear()
    assert fmod.robots_allowed("http://example.com/x") is True

    class _RPDeny:
        def set_url(self, url):
            pass

        def read(self):
            pass

        def can_fetch(self, ua, url):
            return False

    monkeypatch.setattr(fmod.urllib.robotparser, "RobotFileParser", lambda: _RPDeny())
    fmod._ROBOTS_CACHE.clear()
    assert fmod.robots_allowed("http://example.com/x") is False


def test_throttle_no_sleep_when_enough_time():
    sleeps: list[float] = []
    fetch._HOST_LAST_SEEN["h2"] = 0.0
    throttle("h2", 1.0, sleep=lambda s: sleeps.append(s), now=lambda: 5.0)
    assert sleeps == []

def test_fetch_handles_429_backoff(monkeypatch):
    class _Resp429:
        text = "Too Many Requests"
        status_code = 429
        headers = {"Retry-After": "1.5"}
        def raise_for_status(self):
            raise Exception("429")

    responses = [_Resp429(), _Resp()]

    def fake_get(*args, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(fetch.httpx, "get", fake_get)
    monkeypatch.setattr(fetch, "robots_allowed", lambda url: True)
    monkeypatch.setattr(fetch, "_host_is_safe", lambda url: True)

    sleeps: list[float] = []
    doc = fetch_url("http://example.com/p", respect_robots=False, sleep=lambda s: sleeps.append(s))
    assert doc is not None
    assert doc.title == "Hi"
    assert sleeps == [1.5]


def test_fetch_handles_429_exponential_backoff(monkeypatch):
    class _Resp429:
        text = "Too Many Requests"
        status_code = 429
        headers = {}
        def raise_for_status(self):
            raise Exception("429")

    responses = [_Resp429(), _Resp429(), _Resp()]

    def fake_get(*args, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr(fetch.httpx, "get", fake_get)
    monkeypatch.setattr(fetch, "robots_allowed", lambda url: True)
    monkeypatch.setattr(fetch, "_host_is_safe", lambda url: True)

    sleeps: list[float] = []
    doc = fetch_url("http://example.com/p", respect_robots=False, sleep=lambda s: sleeps.append(s))
    assert doc is not None
    assert doc.title == "Hi"
    assert sleeps == [2.0, 4.0]

