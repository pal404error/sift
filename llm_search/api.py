from __future__ import annotations

import json
import time
from collections import defaultdict
from pathlib import Path
from threading import Lock

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from llm_search.auth import require_role
from llm_search.config import get_settings
from llm_search.engine import SearchEngine
from llm_search.ingest import sanitize_query
from llm_search.providers import build_embedding, build_llm
from llm_search.store import build_store


class Metrics:
    def __init__(self) -> None:
        self.lock = Lock()
        self.total_requests = 0
        self.route_counts: dict[str, int] = defaultdict(int)
        self.error_counts = 0
        self.latencies: list[float] = []
        self.max_latencies = 1000

    def record(self, route: str, is_error: bool, duration: float) -> None:
        with self.lock:
            self.total_requests += 1
            self.route_counts[route] += 1
            if is_error:
                self.error_counts += 1
            self.latencies.append(duration)
            if len(self.latencies) > self.max_latencies:
                self.latencies.pop(0)


metrics_store = Metrics()

app = FastAPI(title=get_settings().app_name, version="0.1.0")


@app.middleware("http")
async def metrics_middleware(request: Request, call_next) -> Response:
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time

    route = request.url.path
    is_error = response.status_code >= 500
    metrics_store.record(route, is_error, duration)
    return response


@app.get("/metrics")
def get_metrics() -> Response:
    with metrics_store.lock:
        req_total = metrics_store.total_requests
        err_total = metrics_store.error_counts
        route_counts = dict(metrics_store.route_counts)
        lats = metrics_store.latencies
        avg_lat = sum(lats) / len(lats) if lats else 0.0

    lines = [
        f"sift_requests_total {req_total}",
        f"sift_errors_total {err_total}",
        f"sift_latency_seconds_avg {avg_lat:.4f}",
    ]
    for r, c in route_counts.items():
        lines.append(f'sift_route_requests_total{{route="{r}"}} {c}')
    return Response("\n".join(lines) + "\n", media_type="text/plain")


# Serve the built React + ThreeUI frontend. Precedence:
#   1. ui/dist        -> dev build produced by `cd ui && npm run build` (picked up live)
#   2. llm_search/_uidist -> the same build bundled into the wheel so an installed
#      `sift` package also serves the ThreeUI UI, not just a checkout.
#   3. static/index.html -> last-resort zero-build fallback.
_UI_DIR = Path(__file__).parent.parent / "ui" / "dist"
_PKG_UI_DIR = Path(__file__).parent / "_uidist"
_STATIC_DIR = Path(__file__).parent.parent / "static"


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    for cand in (_UI_DIR, _PKG_UI_DIR, _STATIC_DIR):
        p = cand / "index.html"
        if p.exists():
            return p.read_text(encoding="utf-8")
    raise HTTPException(status_code=404, detail="UI not found")


_ui_assets = (
    _UI_DIR
    if (_UI_DIR / "assets").is_dir()
    else (_PKG_UI_DIR if (_PKG_UI_DIR / "assets").is_dir() else None)
)
if _ui_assets is not None:
    app.mount("/assets", StaticFiles(directory=str(_ui_assets / "assets")), name="ui-assets")


_engine: SearchEngine | None = None


def get_engine() -> SearchEngine:
    global _engine
    if _engine is None:
        s = get_settings()
        _engine = SearchEngine(
            store=build_store(s), embedding=build_embedding(s), llm=build_llm(s), settings=s
        )
    return _engine


def _redact(value: str | None) -> str:
    return "<set>" if value else "<unset>"


@app.get("/health/live")
def health_live() -> dict:
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready(response: Response) -> dict:
    try:
        engine = get_engine()
        engine.store.count()
        s = get_settings()
        llm_ok = s.llm_provider == "fake" or bool(s.llm_api_key or s.anthropic_api_key)
        emb_ok = s.embedding_provider == "fake" or bool(s.llm_api_key)
        if not (llm_ok and emb_ok):
            response.status_code = 503
            return {"status": "error", "detail": "No provider ready"}
        return {"status": "ok"}
    except Exception:
        response.status_code = 503
        return {"status": "error", "detail": "dependency unavailable"}


@app.get("/health/providers")
def provider_health() -> dict:
    s = get_settings()
    llm_ok = s.llm_provider == "fake" or bool(s.llm_api_key or s.anthropic_api_key)
    emb_ok = s.embedding_provider == "fake" or bool(s.llm_api_key)
    return {
        "llm_provider": s.llm_provider,
        "llm_model": s.llm_model,
        "llm_key": _redact(s.llm_api_key),
        "anthropic_key": _redact(s.anthropic_api_key),
        "llm_ready": llm_ok,
        "embedding_provider": s.embedding_provider,
        "embedding_model": s.embedding_model,
        "embedding_ready": emb_ok,
        "vector_store": s.vector_store,
        "reranker": s.reranker,
        "auth_required": s.require_auth,
        "auth_method": s.auth_method,
    }


@app.post("/ingest", dependencies=[Depends(require_role("user"))])
def ingest(url: str) -> dict:
    try:
        n = get_engine().ingest_url(url)
    except Exception as e:  # surface ingestion errors clearly
        raise HTTPException(status_code=502, detail=f"ingest failed: {e}") from e
    return {"ingested_chunks": n}


@app.post("/crawl", dependencies=[Depends(require_role("user"))])
def crawl(url: str, max_pages: int = 20) -> dict:
    # Bound the crawl to prevent resource exhaustion / amplified SSRF.
    max_pages = max(1, min(max_pages, 500))
    try:
        stats = get_engine().crawl_site(url, max_pages=max_pages)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"crawl failed: {e}") from e
    return {"stats": stats}


@app.get("/search", dependencies=[Depends(require_role("user"))])
def search(q: str, top_k: int = 5) -> dict:
    top_k = max(1, min(top_k, 50))
    results = get_engine().search(sanitize_query(q), top_k=top_k)
    return {"query": q, "results": results}


@app.get("/ask", dependencies=[Depends(require_role("user"))])
def ask(q: str, top_k: int = 5) -> dict:
    top_k = max(1, min(top_k, 50))
    return get_engine().ask(sanitize_query(q), top_k=top_k)


@app.get("/ask/stream", dependencies=[Depends(require_role("user"))])
def ask_stream(q: str, top_k: int = 5, hyde: bool = False) -> StreamingResponse:
    """Stream the answer as Server-Sent Events (one ``data: {json}`` line per event).

    Events: ``{"type": "sources", "sources": [...]}`` then ``{"type": "token", "text": "..."}``.
    Output is capped at ``max_tokens`` to bound generation / connection lifetime.
    """
    top_k = max(1, min(top_k, 50))
    max_tokens = 4096

    def event_gen():
        emitted = 0
        for ev in get_engine().ask_stream(sanitize_query(q), top_k=top_k, use_hyde=hyde):
            yield f"data: {json.dumps(ev)}\n\n"
            if ev.get("type") == "token":
                emitted += max(1, len(ev.get("text", "")))
                if emitted >= max_tokens:
                    break

    return StreamingResponse(event_gen(), media_type="text/event-stream")
