from __future__ import annotations

import time
import urllib.robotparser
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

_ROBOTS_CACHE: dict[str, urllib.robotparser.RobotFileParser | None] = {}
_HOST_LAST_SEEN: dict[str, float] = {}
_USER_AGENT = "llm-search/0.1"


class RobotDisallowed(Exception):
    """Raised when robots.txt forbids crawling the URL."""


def _host_key(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def robots_allowed(url: str, user_agent: str = _USER_AGENT) -> bool:
    """Check robots.txt for the URL. Caches parsed rules per host."""
    key = _host_key(url)
    rp = _ROBOTS_CACHE.get(key)
    if rp is None:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{key}/robots.txt")
        try:
            rp.read()
        except Exception:
            # If we cannot read robots.txt, default to permissive (fail open).
            rp = None
        _ROBOTS_CACHE[key] = rp
    if rp is None:
        return True
    return rp.can_fetch(user_agent, url)


def throttle(
    host: str,
    interval: float,
    sleep: Callable[[float], None] = time.sleep,
    now: Callable[[], float] = time.time,
) -> None:
    """Ensure at least `interval` seconds since last crawl of `host`."""
    if interval <= 0:
        return
    last = _HOST_LAST_SEEN.get(host)
    if last is not None:
        wait = interval - (now() - last)
        if wait > 0:
            sleep(wait)
    _HOST_LAST_SEEN[host] = now()


def fetch_url(
    url: str,
    timeout: float = 20,
    respect_robots: bool = True,
    min_interval: float = 0.0,
    sleep: Callable[[float], None] = time.sleep,
    now: Callable[[], float] = time.time,
    etag: str | None = None,
    last_modified: str | None = None,
) -> Document | None:
    """Fetch a URL and return a sanitized Document.

    Honors robots.txt (when respect_robots) and per-host rate limiting. When `etag`
    /`last_modified` are supplied it sends a conditional GET and returns `None` on a
    304 Not Modified (used for cheap incremental re-crawls).
    """
    if respect_robots and not robots_allowed(url):
        raise RobotDisallowed(f"robots.txt disallows: {url}")
    if min_interval > 0:
        throttle(_host_key(url), min_interval, sleep=sleep, now=now)
    headers = {"User-Agent": _USER_AGENT}
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified
    retries = 0
    max_retries = 3
    while True:
        r = httpx.get(
            url,
            timeout=timeout,
            follow_redirects=True,
            headers=headers,
        )
        if r.status_code == 429 and retries < max_retries:
            retries += 1
            wait_time = 2.0**retries
            retry_after = r.headers.get("Retry-After")
            if retry_after:
                try:
                    wait_time = float(retry_after)
                except ValueError:
                    pass
            sleep(wait_time)
            continue
        break
    if r.status_code == 304:
        return None
    r.raise_for_status()
    title = ""
    try:
        soup = BeautifulSoup(r.text, "html.parser")
        title = (soup.title.string or "").strip() if soup.title else ""
    except Exception:
        pass
    return Document(
        url=url,
        title=title or url,
        text=html_to_text(r.text),
        etag=r.headers.get("etag"),
        last_modified=r.headers.get("last-modified"),
    )


@dataclass
class Document:
    url: str
    title: str
    text: str
    etag: str | None = None
    last_modified: str | None = None


def html_to_text(html: str) -> str:
    """Extract readable text from HTML, stripping scripts/styles (XSS defense)."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "iframe", "object", "embed"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)


def sanitize_query(text: str) -> str:
    """Defense: strip control chars and limit length of untrusted input."""
    cleaned = "".join(ch for ch in text if ch.isprintable() or ch in "\n\t")
    return cleaned[:2000].strip()
