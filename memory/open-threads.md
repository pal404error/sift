# Open Threads / Unresolved Issues

Track unresolved questions, known limitations, and parked work. Update after each session.

---

## Open
- **Product scope (RESOLVED 2026-08-20):** web/search engine, enterprise self-host,
  multi-provider. First milestone = Index+search MVP.
- **Auth/compliance (PARTIAL 2026-08-20):** Phase 2 added bearer-token RBAC + audit log.
  Still open: SSO/OIDC, fine-grained permissions, audit log rotation/export. Defer to Phase 3.
- **Crawler scale (PARTIAL 2026-08-20):** BFS crawl + sitemap discovery + CrawlState added.
  Still open: concurrency/parallel fetches, crawl queue/persistence, real incremental
  re-crawl using ETag/Last-Modified (CrawlState records but re-fetch path not wired),
  content hashing to skip unchanged pages.
- **Reranker quality (PARTIAL 2026-08-20):** cross-encoder reranker added (guarded). Still
  open: run an offline eval comparing lexical vs cross-encoder on a gold set; tune
  `rerank_multiplier`; default-deploy decision.
- **Typecheck (RESOLVED 2026-08-20):** mypy is a green quality gate.
- **SSO (RESOLVED 2026-08-20):** OidcVerifier now verifies RS256 signatures via JWKS
  (discovery or injected get_jwks). Still open: OIDC discovery caching/refresh, refresh-token
  session flow, fine-grained (non admin/user) role mapping, token expiry handling polish.

- **CI/CD (RESOLVED 2026-08-20):** GitHub Actions + pre-commit + Makefile + tested workflow
  YAML in place. Still open: actually run CI on a real push (no git remote here), add a
  scheduled `pip-audit`/dependabot, and a release changelog automation.

- **Eval (RESOLVED 2026-08-20):** `scripts/run_eval.py` runs the harness offline with lexical
  fakes; CI gate via `--gate-mrr` wired into `.github/workflows/ci.yml` + `make eval`/`make ci`.
  Rerank-multiplier sweep (`--rerank-multipliers`) added (ADR-018). Still open: a real annotated
  gold set + lexical-vs-cross-encoder comparison; swap `tests/gold/eval_gold.json` for a semantic set.

- **Observability (RESOLVED 2026-08-20):** in-process `Metrics` + `GET /metrics` (Prometheus
  style) + `GET /health/live` + `GET /health/ready` (503 on missing store/provider). Still open:
  expose metrics to Prometheus scraping (no push), add per-provider health detail, dashboard.

- **Crawl (RESOLVED 2026-08-20):** concurrent (`CRAWL_CONCURRENCY`) + ETag-aware incremental
  re-crawl (304 -> skip re-ingest) via seeded `CrawlState`. Persistent `CrawlState` JSON
  save/load + 429/Retry-After backoff added by collaborator **AGY** (see decisions.log).
  Still open: sitemap-driven full re-crawl; DB-backed state; adaptive per-host backoff.
- **Real provider e2e (PARTIAL 2026-08-20):** integration tests added (skip without keys).
  Still open: run them in CI with a sandboxed key / local Ollama for true coverage.
- **Vector store finalization:** Qdrant chosen as default (ADR-003) but pgvector vs
  Qdrant trade-off for ops simplicity still worth a spike if single-binary deploy matters.
- **LLM provider strategy:** Support only OpenAI-compatible, or multi-provider (Anthropic,
  local Ollama)? Affects abstraction layer design.
- **Data sources:** Which corpora will be searchable — web, local docs/PDFs, code, or all?

## Known Limitations
- Trending analysis used `pushed:>date` proxy, not true 7-day velocity. Re-run periodically.
- Unauthenticated API limited deep-dive to 12 repos (no per-file README/PR extraction).

## Parked
- Rust retrieval core (ADR-001 mentions possible future drop to Rust) — defer until latency
  data exists.
