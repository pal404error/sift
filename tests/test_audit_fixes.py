import socket

import pytest
from fastapi.testclient import TestClient

from llm_search.config import Settings
from llm_search.crawl import _call_fetch, crawl_site
from llm_search.ingest.fetch import Document, _host_is_safe
from llm_search.providers.base import cosine_similarity

# --- F1: env-var prefix + back-compat aliases ---
_ENV_KEYS = [
    "SIFT_HYBRID", "HYBRID", "SIFT_LLM_API_KEY", "LLM_API_KEY",
    "SIFT_EMBEDDING_PROVIDER", "EMBEDDING_PROVIDER", "SIFT_RERANKER", "RERANKER",
]


def _clear_env(monkeypatch):
    for k in _ENV_KEYS:
        monkeypatch.delenv(k, raising=False)


def test_sift_prefix_env_var_is_honored(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("SIFT_HYBRID", "true")
    assert Settings().hybrid is True


def test_sift_prefixed_key_works(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("SIFT_LLM_API_KEY", "prefixed")
    assert Settings().llm_api_key == "prefixed"


def test_provider_reranker_sift_names(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("SIFT_EMBEDDING_PROVIDER", "openai")
    monkeypatch.setenv("SIFT_RERANKER", "cross-encoder")
    s = Settings()
    assert s.embedding_provider == "openai"
    assert s.reranker == "cross-encoder"


# --- F4: SSRF guard ---
def test_host_is_safe_rejects_non_http(monkeypatch):
    assert _host_is_safe("ftp://example.com") is False
    assert _host_is_safe("file:///etc/passwd") is False


def test_host_is_safe_rejects_loopback_and_private(monkeypatch):
    def fake_getaddrinfo(host, port, **_):
        ip = "127.0.0.1" if host == "localhost" else "10.0.0.5"
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 0))]

    monkeypatch.setattr("llm_search.ingest.fetch.socket.getaddrinfo", fake_getaddrinfo)
    assert _host_is_safe("http://localhost:8080") is False
    assert _host_is_safe("http://10.0.0.5/") is False


def test_host_is_safe_allows_public(monkeypatch):
    def fake_getaddrinfo(host, port, **_):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))]

    monkeypatch.setattr("llm_search.ingest.fetch.socket.getaddrinfo", fake_getaddrinfo)
    assert _host_is_safe("https://example.com") is True


# --- F2/F3: crawler BFS expands via raw HTML and respects robots arg order ---
def test_crawl_discovers_links_from_raw_html(monkeypatch):
    monkeypatch.setattr("llm_search.ingest.fetch._host_is_safe", lambda u: True)
    pages = {
        "http://example.com/a": '<html><body><a href="/b">b</a></body></html>',
        "http://example.com/b": "<html><body>hi</body></html>",
    }

    def fake_fetch(url, etag=None, last_modified=None):
        return Document(url=url, title=url, text="", html=pages[url])

    state, stats = crawl_site(
        "http://example.com/a",
        ingest_fn=lambda d: 1,
        max_pages=5,
        fetch_fn=fake_fetch,
        robots_fn=lambda u: True,
        concurrency=1,
    )
    assert stats["pages"] == 2  # both a and b ingested -> BFS expanded
    assert stats["links"] >= 1


def test_call_fetch_passes_etag_as_keyword_not_positionally():
    seen = {}

    def fake_fetch(url, etag=None, last_modified=None):
        seen.update(url=url, etag=etag, last_modified=last_modified)
        return Document(url=url, title=url, text="x")

    _call_fetch(fake_fetch, "http://x", "ETAG123")
    assert seen["etag"] == "ETAG123"  # would have landed on `timeout` if positional


# --- F6: cosine strict catches dimension mismatch ---
def test_cosine_similarity_raises_on_dim_mismatch():
    with pytest.raises(ValueError):
        cosine_similarity([1.0, 2.0], [1.0, 2.0, 3.0])


# --- F5/F9 + bounds: API endpoints ---
def test_search_clamps_top_k_and_returns_ok():
    client = TestClient(__import__("llm_search.api", fromlist=["app"]).app)
    resp = client.get("/search", params={"q": "hello", "top_k": 9999})
    assert resp.status_code == 200
    assert isinstance(resp.json()["results"], list)
