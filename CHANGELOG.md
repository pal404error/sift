# Changelog

All notable changes to Sift will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Early exploration for additional managed vector store integrations.
- **Hybrid retrieval**: lexical + vector fusion via Reciprocal Rank Fusion (`llm_search/lexical_index.py`, `SIFT_HYBRID`). Off by default, dependency-free, fully tested.
- **Research-grade eval**: `ndcg@k` metric added; `scripts/run_eval.py --compare` now reports recall/precision/ndcg/MRR. Headline lift (recall@5 0.31→0.81) verified against `tests/gold/eval_gold_semantic.json`.
- **HyDE query expansion**: `SearchEngine.ask(use_hyde=True)` rewrites the query into a hypothetical answer passage for better retrieval (`SIFT_USE_HYDE`). Off by default (ADR-020).
- **Streaming answers (SSE)**: `LLMProvider.stream` + `SearchEngine.ask_stream` + `GET /ask/stream` (Server-Sent Events: sources then token events). Real token streaming for OpenAI/Anthropic; safe fallback for all. CLI `ask`/`search` gained `--hybrid`/`--hyde` flags (ADR-021).
- **Configurable hybrid fusion**: `SIFT_HYBRID_MODE` (`rrf` | `weighted`) + `SIFT_HYBRID_ALPHA`. Weighted path min-max-normalizes each signal before blending (ADR-022). RRF remains the default.
- Transparent retrieval benchmark in `data/retrieval_benchmark.csv` (real, reproducible numbers).
- README hook leading with the measured ~5× retrieval lift and an honest star CTA.
- Launch/promo assets in `promo/` (Show HN, Reddit, X drafts) and a real-metrics `SITREP.md`.

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
