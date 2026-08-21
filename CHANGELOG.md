# Changelog

All notable changes to Sift will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Embedding-model sweep**: `scripts/run_eval.py --embedding-models "m1,m2,..."` builds a fresh index per model and prints a recall/precision/ndcg/MRR comparison; skips models that fail to load. Ran on the semantic gold set: `all-MiniLM-L6-v2` (recall@5 0.812) > `paraphrase-MiniLM-L3-v2` (0.750).
- **Larger, multilingual gold set**: `tests/gold/eval_gold_large.json` (24 factual docs, 32 queries, 8 cross-lingual ES/FR/DE/IT) + `data/retrieval_benchmark_large.csv`. Findings: on keyword-heavy queries lexical recall is already high (semantic wins on ndcg/mrr, not recall); model ranking is dataset-dependent. `tests/test_gold_integrity.py` guards gold-set validity.
- **External BEIR benchmark**: `scripts/import_beir.py` converts a BEIR dataset (ground-truth qrels, so relevance is not authored by us) into gold format. On BEIR SciFact (2000 docs, 100 queries), semantic gives ~2.2× recall / ~2.5× MRR over lexical; `all-MiniLM-L6-v2` > `paraphrase-MiniLM-L3-v2`. Results in `data/retrieval_benchmark_beir.csv` (generated gold file is git-ignored).

### Fixed (multi-agent audit)
- **CRITICAL: config env-var prefix** — `Settings` now uses `env_prefix="SIFT_"`, so every documented `SIFT_*` knob (and the `sift` CLI `--hybrid`/`--hyde` flags and `sift demo` hybrid default) actually takes effect. Previously these were silent no-ops. `.env.example` updated to `SIFT_` names.
- **CRITICAL: crawler BFS was dead** — link extraction read plaintext (tags already stripped), so crawls never expanded past page 1. Now uses the raw HTML (`Document.html`). Also fixed `_call_fetch` passing `etag` into the wrong positional arg (which silently disabled `respect_robots` on crawls); it now passes `etag`/`last_modified` by keyword.
- **HIGH: SSRF in fetch** — `fetch_url` now rejects non-http(s) schemes and private/loopback/link-local IPs, re-validates every redirect hop, and caps response size (`SIFT_MAX_FETCH_BYTES`, default 10MB). Throttle now uses a lock.
- **HIGH: unbounded inputs** — `/crawl` `max_pages` clamped to [1,500]; `/search`/`/ask`/`/ask/stream` `top_k` clamped to [1,50]; streaming capped at 4096 tokens.
- **MEDIUM: `/health` readiness** — `emb_ok` no longer keys off the LLM key, and the readiness check requires BOTH providers ready (`and`, not `or`).
- **MEDIUM: cosine_similarity** now uses `zip(..., strict=True)` so a dimension mismatch raises instead of silently truncating and mis-ranking.
- **Docs** — README overstated the lift as "~5×" (now "2.6×"); `SIFT_HYBRID_ROUTE` noted as weighted-mode only; `research/RETRIEVAL_NOTES.md` now records weighted fusion + routing as shipped (not "not implemented").

## [0.2.0] - 2026-08-21

### Added
- **Hybrid retrieval**: lexical + vector fusion via Reciprocal Rank Fusion (`llm_search/lexical_index.py`, `SIFT_HYBRID`). Off by default, dependency-free, fully tested (ADR-019).
- **Research-grade eval**: `ndcg@k` metric added; `scripts/run_eval.py --compare` reports recall/precision/ndcg/MRR. Headline lift (recall@5 0.31→0.81, MRR 0.12→0.59) verified on `tests/gold/eval_gold_semantic.json`.
- **HyDE query expansion**: `SearchEngine.ask(use_hyde=True)` rewrites the query into a hypothetical answer passage for better retrieval (`SIFT_USE_HYDE`). Off by default (ADR-020).
- **Streaming answers (SSE)**: `LLMProvider.stream` + `SearchEngine.ask_stream` + `GET /ask/stream` (sources event, then token events). Real token streaming for OpenAI/Anthropic; safe fallback for all. CLI `ask`/`search` gained `--hybrid`/`--hyde` (ADR-021).
- **Configurable hybrid fusion**: `SIFT_HYBRID_MODE` (`rrf` | `weighted`) + `SIFT_HYBRID_ALPHA`. Weighted path min-max-normalizes each signal before blending (ADR-022). RRF remains the default.
- **Query-style routing**: `SIFT_HYBRID_ROUTE` biases hybrid toward lexical for exact-match queries (codes/IDs/acronyms) when in weighted mode (ADR-023).
- **Transparent benchmark**: `data/retrieval_benchmark.csv` with real, reproducible numbers; web UI streams answers with a HyDE toggle; `examples/quickstart.py` (no API keys).
- **Docs**: `research/RETRIEVAL_NOTES.md` (maps the stack to the 2026 production-RAG consensus), `ROADMAP.md`, and an honest growth log.

### Changed
- README leads with the verified benchmark and an honest star CTA (corrected the overstated "5×" to exact 2.6× recall / 4.8× MRR).

## [0.1.0] - 2026-08-21

### Added
- **Initial professional release!** 🚀
- **Pluggable Architecture**: Core framework supporting interchangeable LLM and embedding providers.
- **Vector Store Integration**: Robust, generic interfaces for vector storage and retrieval.
- **Crawl Orchestrator**: Built-in scheduling and management for data ingestion pipelines.
- **FastAPI Backend**: High-performance API endpoints for search, ingestion, and administration.
- **CLI (`sift`)**: Powerful developer command-line interface for local management.
- **Web UI**: Static, mobile-responsive frontend for immediate, out-of-the-box search.
- **Offline Evaluation**: Tooling to measure and track retrieval accuracy and generation quality.
- **Enterprise Auth**: OIDC/SSO support integrated directly into the core routing layer.
- **Observability**: Health checks and metrics endpoints ready for Prometheus/Grafana.
- Comprehensive setup scripts, Docker Compose configurations, and `.env` templating.
