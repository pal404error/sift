# Roadmap — Sift

> Public, honest roadmap. Items ship when they're real — no vapor. Last updated: 2026-08-21.

## Shipped
- Self-hostable RAG search over web content (FastAPI + Qdrant or in-memory).
- Pluggable LLM & embedding providers (OpenAI, Anthropic, Ollama, local, fake).
- Crawl orchestrator (polite BFS, robots.txt, concurrency, ETag re-crawl).
- Lexical + cross-encoder reranking; **hybrid retrieval** (lexical+vector RRF).
- Offline eval harness with recall/precision/**ndcg**/MRR; verified ~2.6× recall lift
  on a hard semantic gold set (see `data/retrieval_benchmark.csv`).
- Enterprise auth (API key + OIDC/JWKS), Prometheus metrics, health probes.
- CI quality gates (ruff, mypy, pytest 80% cov, pip-audit, gitleaks).

## In progress
- **HyDE query expansion** — rewrite the query into a hypothetical answer to improve retrieval.
- **Benchmark report** — reproducible comparison of embedding models on the gold set.

## Planned (community-driven)
- Streaming answers (SSE) in API + CLI.
- More vector-store backends (local lightweight option).
- Docs site + module-level READMEs for providers/retrievers.
- Community Discussions: "which embedding model should we benchmark next?", polls.

## How to influence this
- Open an issue or Discussion with a use case. The roadmap is shaped by real feedback,
  not by hype. Everything is reproducible from the repo — fork it and prove us wrong.
