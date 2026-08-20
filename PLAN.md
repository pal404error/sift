# PLAN — LLM-search Index+Search MVP

Goal: A self-hostable, multi-provider RAG search service over web content. Ingest URLs →
chunk → embed → store in Qdrant → answer natural-language queries via a pluggable LLM.

## Success criteria (verify before claiming done)
- [ ] `ruff check .` → 0 errors, 0 warnings
- [ ] `pytest -q` → all pass (unit + fake-provider integration)
- [ ] `python -c "import llm_search.api"` imports cleanly
- [ ] FastAPI app boots (`uvicorn llm_search.main:app`) and `/health` returns ok
- [ ] `docker-compose up` brings up app + Qdrant (smoke, documented)
- [ ] README documents architecture (Mermaid) + run instructions

## Phases (atomic, verifiable)
1. **Package + config** — `pyproject.toml`, `llm_search/config.py` (pydantic Settings,
   `.env.example`). verify: import + settings load with defaults.
2. **Provider abstractions** — `providers/base.py` (LLM/Embedding ABCs),
   OpenAI/Anthropic/Ollama impls, `fake.py` for tests. verify: unit test fake returns
   deterministic output.
3. **Ingestion** — `ingest/fetch.py` (web fetch→text, sanitize), `ingest/chunk.py`
   (token-aware chunking). verify: chunk size/overlap tests.
4. **Vector store** — `store/base.py` (ABC), `store/memory.py` (InMemory for dev/test),
   `store/qdrant.py` (Qdrant for prod). verify: round-trip upsert+search with InMemory.
5. **Retrieval + RAG** — `retriever.py` (top-k), `rag.py` (retrieve→prompt→LLM answer).
   verify: end-to-end with fake providers returns grounded answer.
6. **API** — `api.py` FastAPI (`/health`, `/ingest`, `/search`, `/ask`), `main.py`.
   verify: TestClient hits `/ask` and `/health` green.
7. **Ops** — `Dockerfile`, `docker-compose.yml` (app + qdrant), `.env.example`. verify:
   compose config valid (`docker compose config`).
8. **Docs + graph** — README w/ Mermaid architecture, refresh knowledge-graph.json.
   verify: rebuild script runs; README renders.

## Risks / open questions
- No live API keys/Qdrant in CI → use fakes + InMemory store for tests (no network).
- HTML sanitization for XSS (security-review discipline) included in fetch.
- Auth/compliance deferred (enterprise phase 2).
