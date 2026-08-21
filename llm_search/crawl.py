from __future__ import annotations

import json
from collections import deque
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from llm_search.ingest.fetch import (
    Document,
    RobotDisallowed,
    _host_key,
    fetch_url,
    robots_allowed,
)


@dataclass
class CrawlState:
    """Tracks visited URLs + ETag/Last-Modified for incremental re-crawl."""

    visited: dict[str, str | None] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path) -> CrawlState:
        """Load state from JSON for persistent incremental crawls."""
        p = Path(path)
        if p.exists():
            with open(p, encoding="utf-8") as f:
                return cls(visited=json.load(f))
        return cls()

    def save(self, path: str | Path) -> None:
        """Save state to JSON."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.visited, f)

    def is_fresh(self, url: str, etag: str | None) -> bool:
        return self.visited.get(url) == etag

    def record(self, url: str, etag: str | None = None) -> None:
        self.visited[url] = etag

    def pending(self, urls: list[str]) -> list[str]:
        return [u for u in urls if u not in self.visited]


def same_domain(url: str, base: str) -> bool:
    return urlparse(url).netloc == urlparse(base).netloc


def extract_links(html: str, base_url: str) -> list[str]:
    """Same-domain, de-fragmented, sorted unique links from an HTML page."""
    soup = BeautifulSoup(html, "html.parser")
    out: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = cast(str, a.get("href", ""))
        abs_url = urljoin(base_url, href)
        if abs_url.startswith("http") and same_domain(abs_url, base_url):
            out.add(abs_url.split("#")[0])
    return sorted(out)


def discover_sitemap(start_url: str, fetch_fn=None) -> str | None:
    """Find a sitemap via robots.txt `Sitemap:` or fallback `/sitemap.xml`."""
    fetch_fn = fetch_fn or fetch_url
    host = _host_key(start_url)
    try:
        text = fetch_fn(f"{host}/robots.txt").text
        for line in text.splitlines():
            if line.lower().startswith("sitemap:"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    try:
        fetch_fn(f"{host}/sitemap.xml")
        return f"{host}/sitemap.xml"
    except Exception:
        return None


def _call_fetch(
    fetch_fn: Callable[..., Document | None],
    url: str,
    etag: str | None,
    last_modified: str | None = None,
) -> Document | None:
    """Invoke `fetch_fn` with conditional GET args by keyword.

    Keyword args are used so they map to the correct parameters (the previous
    positional call mapped `etag` onto `timeout` and `None` onto `respect_robots`,
    silently bypassing robots.txt). Falls back to a bare call for minimal fakes.
    """
    try:
        return fetch_fn(url, etag=etag, last_modified=last_modified)
    except TypeError:
        return fetch_fn(url)


def crawl_site(
    start_url: str,
    ingest_fn: Callable[[Document], int],
    max_pages: int = 20,
    state: CrawlState | None = None,
    fetch_fn: Callable[..., Document | None] | None = None,
    robots_fn: Callable[[str], bool] = robots_allowed,
    concurrency: int = 1,
) -> tuple[CrawlState, dict]:
    """BFS crawl from `start_url`, ingesting each page via `ingest_fn(doc)`.

    `fetch_fn` is injectable (returns a Document, or `None` on a 304 Not Modified).
    Honors robots.txt + dedupe + `max_pages`. Up to `concurrency` pages are fetched in
    parallel. Passing a `state` pre-populated with ETags enables incremental re-crawl:
    unchanged pages (304) are skipped and not re-ingested.
    """
    fetch_fn = fetch_fn or fetch_url
    state = state or CrawlState()
    queue: deque[str] = deque([start_url])
    discovered: set[str] = {start_url}
    stats = {"pages": 0, "skipped": 0, "failed": 0, "links": 0}
    workers = max(1, concurrency)

    def process(url: str) -> None:
        if not robots_fn(url):
            state.record(url)
            stats["skipped"] += 1
            return
        try:
            doc = _call_fetch(fetch_fn, url, state.visited.get(url))  # type: ignore[arg-type]
        except RobotDisallowed:
            state.record(url)
            stats["skipped"] += 1
            return
        except Exception:
            stats["failed"] += 1
            return
        if doc is None:  # 304 Not Modified -> unchanged, skip re-ingest
            stats["skipped"] += 1
            return
        ingest_fn(doc)
        state.record(url, doc.etag)
        stats["pages"] += 1
        # Link extraction needs the raw HTML; doc.text has tags stripped.
        for link in extract_links(doc.html or doc.text, url):
            if link not in discovered:
                discovered.add(link)
                queue.append(link)
                stats["links"] += 1

    with ThreadPoolExecutor(max_workers=workers) as pool:
        while queue and stats["pages"] < max_pages:
            batch: list[str] = []
            while queue and len(batch) < workers:
                batch.append(queue.popleft())
            if not batch:
                break
            futures = {pool.submit(process, u): u for u in batch}
            for _ in as_completed(futures):
                pass
    return state, stats
