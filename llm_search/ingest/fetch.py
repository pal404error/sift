from __future__ import annotations

import ipaddress
import socket
import threading
import time
import urllib.robotparser
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

_HOST_LOCK = threading.Lock()
_ROBOTS_CACHE: dict[str, urllib.robotparser.RobotFileParser | None] = {}
_HOST_LAST_SEEN: dict[str, float] = {}
_USER_AGENT = "llm-search/0.1"

# Hosts/addresses we refuse to fetch (SSRF defense).
_BLOCKED_NETS = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # link-local / cloud metadata
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),  # ULA
    ipaddress.ip_network("fe80::/10"),  # link-local
)


class RobotDisallowed(Exception):
    """Raised when robots.txt forbids crawling the URL."""


class UnsafeURL(Exception):
    """Raised when a URL targets a non-public scheme or address (SSRF defense)."""


class ResponseTooLarge(Exception):
    """Raised when a fetched response exceeds the configured byte cap."""


def _host_key(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def _host_is_safe(url: str) -> bool:
    """Allow only http/https to public, non-reserved IP addresses."""
    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        return False
    host = p.hostname or ""
    if not host:
        return False
    try:
        infos = socket.getaddrinfo(host, None)
    except (socket.gaierror, UnicodeError):
        return False
    for info in infos:
        addr_str = info[4][0]
        try:
            addr = ipaddress.ip_address(addr_str)
        except ValueError:
            continue
        if addr.is_loopback or addr.is_private or addr.is_link_local or addr.is_reserved:
            return False
        if any(addr in net for net in _BLOCKED_NETS):
            return False
    return True


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
    with _HOST_LOCK:
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
    max_bytes: int = 10 * 1024 * 1024,
) -> Document | None:
    """Fetch a URL and return a sanitized Document.

    Honors robots.txt (when respect_robots) and per-host rate limiting. When `etag`
    /`last_modified` are supplied it sends a conditional GET and returns `None` on a
    304 Not Modified (used for cheap incremental re-crawls).

    Security: only http/https to public, non-reserved addresses are allowed; redirects are
    re-validated against the same policy; responses are capped at `max_bytes`.
    """
    if not _host_is_safe(url):
        raise UnsafeURL(f"refusing to fetch unsafe URL: {url}")
    if respect_robots and not robots_allowed(url):
        raise RobotDisallowed(f"robots.txt disallows: {url}")
    if min_interval > 0:
        throttle(_host_key(url), min_interval, sleep=sleep, now=now)

    headers = {"User-Agent": _USER_AGENT}
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified

    target = url
    retries = 0
    max_retries = 3
    for _ in range(6):  # follow redirects, re-validating each hop
        if not _host_is_safe(target):
            raise UnsafeURL(f"redirect to unsafe URL: {target}")
        r = httpx.get(target, timeout=timeout, follow_redirects=False, headers=headers)
        if r.status_code == 429 and retries < max_retries:
            retries += 1
            wait = 2.0**retries
            retry_after = r.headers.get("Retry-After")
            if retry_after:
                try:
                    wait = float(retry_after)
                except ValueError:
                    pass
            sleep(wait)
            continue
        if r.status_code in (301, 302, 303, 307, 308):
            loc = r.headers.get("location")
            if not loc:
                raise RobotDisallowed("redirect with no Location")
            target = urljoin(target, loc)
            continue
        if r.status_code == 304:
            return None
        r.raise_for_status()
        if len(r.text) > max_bytes:
            raise ResponseTooLarge(
                f"response exceeded {max_bytes} bytes for {target}"
            )
        return _build_document(target, r.text, r)
    raise RobotDisallowed("too many redirects")


def _build_document(url: str, raw: str, response: httpx.Response) -> Document:
    title = ""
    try:
        soup = BeautifulSoup(raw, "html.parser")
        title = (soup.title.string or "").strip() if soup.title else ""
    except Exception:
        pass
    return Document(
        url=url,
        title=title or url,
        text=html_to_text(raw),
        html=raw,
        etag=response.headers.get("etag"),
        last_modified=response.headers.get("last-modified"),
    )


@dataclass
class Document:
    url: str
    title: str
    text: str
    html: str | None = None
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
