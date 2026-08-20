from __future__ import annotations

from llm_search.crawl import (
    CrawlState,
    crawl_site,
    discover_sitemap,
    extract_links,
    same_domain,
)
from llm_search.ingest.fetch import Document


def _doc(url: str, html: str) -> Document:
    return Document(url=url, title=url, text=html)


def test_extract_links_same_domain_only():
    html = """
    <a href="/about">a</a>
    <a href="https://example.com/x">x</a>
    <a href="https://other.com/y">y</a>
    <a href="/#frag">frag</a>
    """
    links = extract_links(html, "https://example.com/home")
    assert "https://example.com/about" in links
    assert "https://example.com/x" in links
    assert "https://other.com/y" not in links
    assert all(not link.endswith("#frag") for link in links)


def test_crawl_bfs_respects_max_pages_and_dedupes():
    # link graph: home -> p1, p2 ; p1 -> p2 (cycle); p2 -> p1 (cycle)
    pages = {
        "https://ex.com/": '<a href="https://ex.com/p1"></a><a href="https://ex.com/p2"></a>',
        "https://ex.com/p1": '<a href="https://ex.com/p2"></a>',
        "https://ex.com/p2": '<a href="https://ex.com/p1"></a>',
    }
    ingested: list[str] = []

    def fake_fetch(url: str) -> Document:
        return _doc(url, pages.get(url, "<html></html>"))

    state, stats = crawl_site(
        "https://ex.com/",
        ingest_fn=lambda d: ingested.append(d.url) or 0,
        max_pages=2,
        fetch_fn=fake_fetch,
        robots_fn=lambda url: True,
    )
    assert stats["pages"] == 2
    assert len(ingested) == 2
    assert stats["links"] >= 2  # discovered links counted


def test_crawl_dedupes_within_run():
    pages = {"https://ex.com/a": "<a href='https://ex.com/a'>self</a>"}

    def fake_fetch(url: str) -> Document:
        return _doc(url, pages.get(url, "<html></html>"))

    ingested: list[str] = []
    _, stats = crawl_site(
        "https://ex.com/a",
        ingest_fn=lambda d: ingested.append(d.url) or 0,
        max_pages=5,
        fetch_fn=fake_fetch,
        robots_fn=lambda url: True,
    )
    assert stats["pages"] == 1
    assert ingested == ["https://ex.com/a"]


def test_crawl_incremental_skips_unchanged_etag():
    # Page was crawled before (etag "v1"); server returns 304 -> not re-ingested.
    def fake_fetch(url: str, etag=None, last_modified=None) -> Document | None:
        if etag == "v1":
            return None  # 304 Not Modified
        return _doc(url, "<html>changed</html>")

    state = CrawlState(visited={"https://ex.com/home": "v1"})
    ingested: list[str] = []
    _, stats = crawl_site(
        "https://ex.com/home",
        ingest_fn=lambda d: ingested.append(d.url) or 0,
        max_pages=5,
        state=state,
        fetch_fn=fake_fetch,
        robots_fn=lambda url: True,
    )
    assert stats["pages"] == 0
    assert stats["skipped"] >= 1
    assert ingested == []
    assert state.visited.get("https://ex.com/home") == "v1"


def test_crawl_incremental_reingests_changed_etag():
    def fake_fetch(url: str, etag=None, last_modified=None) -> Document | None:
        if etag == "v1":
            return _doc(url, "<html>new content</html>")  # changed -> 200
        return _doc(url, "<html>orig</html>")

    state = CrawlState(visited={"https://ex.com/home": "v1"})
    ingested: list[str] = []
    _, stats = crawl_site(
        "https://ex.com/home",
        ingest_fn=lambda d: ingested.append(d.url) or 0,
        max_pages=5,
        state=state,
        fetch_fn=fake_fetch,
        robots_fn=lambda url: True,
    )
    assert stats["pages"] == 1
    assert ingested == ["https://ex.com/home"]


def test_crawl_concurrency_fetches_all():
    pages = {
        "https://ex.com/": "<a href='https://ex.com/p1'></a><a href='https://ex.com/p2'></a>",
        "https://ex.com/p1": "<html>p1</html>",
        "https://ex.com/p2": "<html>p2</html>",
    }

    def fake_fetch(url: str, etag=None, last_modified=None) -> Document:
        return _doc(url, pages.get(url, "<html></html>"))

    ingested: list[str] = []
    _, stats = crawl_site(
        "https://ex.com/",
        ingest_fn=lambda d: ingested.append(d.url) or 0,
        max_pages=5,
        fetch_fn=fake_fetch,
        robots_fn=lambda url: True,
        concurrency=4,
    )
    assert stats["pages"] == 3
    assert len(ingested) == 3


def test_discover_sitemap_via_robots():
    robots = "User-agent: *\nSitemap: https://ex.com/sitemap.xml\n"

    def fake_fetch(url: str) -> Document:
        return _doc(url, robots if url.endswith("robots.txt") else "<xml/>")

    assert discover_sitemap("https://ex.com/", fetch_fn=fake_fetch) == "https://ex.com/sitemap.xml"


def test_discover_sitemap_fallback():
    def fake_fetch(url: str) -> Document:
        if url.endswith("robots.txt"):
            raise RuntimeError("404")
        return _doc(url, "<xml/>")

    assert discover_sitemap("https://ex.com/", fetch_fn=fake_fetch) == "https://ex.com/sitemap.xml"


def test_same_domain():
    assert same_domain("https://ex.com/a", "https://ex.com/b")
    assert not same_domain("https://ex.com", "https://other.com")


def test_crawl_state_save_load(tmp_path):
    state_file = tmp_path / "state.json"
    state = CrawlState(visited={"https://ex.com/a": "v1", "https://ex.com/b": None})
    state.save(state_file)
    
    loaded_state = CrawlState.load(state_file)
    assert loaded_state.visited == {"https://ex.com/a": "v1", "https://ex.com/b": None}

def test_crawl_state_load_non_existent(tmp_path):
    state_file = tmp_path / "missing.json"
    loaded_state = CrawlState.load(state_file)
    assert loaded_state.visited == {}

