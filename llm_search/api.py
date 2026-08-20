from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException

from llm_search.auth import require_role
from llm_search.config import get_settings
from llm_search.engine import SearchEngine
from llm_search.ingest import sanitize_query
from llm_search.providers import build_embedding, build_llm
from llm_search.store import build_store

app = FastAPI(title=get_settings().app_name, version="0.1.0")

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


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "engine": get_settings().app_name}


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
    try:
        stats = get_engine().crawl_site(url, max_pages=max_pages)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"crawl failed: {e}") from e
    return {"stats": stats}


@app.get("/search", dependencies=[Depends(require_role("user"))])
def search(q: str, top_k: int = 5) -> dict:
    results = get_engine().search(sanitize_query(q), top_k=top_k)
    return {"query": q, "results": results}


@app.get("/ask", dependencies=[Depends(require_role("user"))])
def ask(q: str, top_k: int = 5) -> dict:
    return get_engine().ask(sanitize_query(q), top_k=top_k)
