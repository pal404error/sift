# Handoff Snapshot

Compact context for pause/resume across sessions or agents. Refresh via
`scripts/make_handoff.py` or manually on pause.

---

## Session: 2026-08-20 — Framework Establishment

**Current task:** Build the Index+Search MVP (Step 4 ritual: brainstorm → plan → build → verify).
**Done steps:**
1. Scraped GitHub trending (7 clusters, 164 unique repos, top-50 ranked). → `trending-insights.md`, `.scrape/`.
2. Synthesized patterns → `trending-insights.md` §3. Created `RTK.md`.
3. Built memory layer + `skills/` packs + `.pre-commit-config.yaml` / `.gitignore`.
4. Brainstormed (user): web search engine, enterprise self-host, multi-provider, MVP first.
5. Planned → `PLAN.md`. Built MVP: config, providers (OpenAI/Anthropic/Ollama/fake),
   ingest (fetch+sanitize+chunk), vector store (memory+qdrant), engine (RAG), FastAPI,
   Dockerfile + docker-compose, README (Mermaid).
6. Wrote 11 tests; ran ruff (0 errors) and pytest (11 passed); refreshed knowledge graph
   (108 nodes, 177 edges).

**Blockers:** None. Typecheck (mypy) not yet wired; docker build not executed in this env.

**Next action:** User review of MVP; then Phase 2 (enterprise auth/RBAC, real provider
integration, crawler scale/robots.txt, reranker, eval/coverage thresholds).

**Recent changes & verification:**
- `ruff check .` → 0 errors, 0 warnings (PASS).
- `pytest -q` → 11 passed (PASS).
- `import llm_search.api` + `/health` via TestClient (PASS).
- Knowledge graph rebuilt via `scripts/rebuild_knowledge_graph.py` (PASS).
- Docker image build not run here (no docker daemon); compose config authored.

---

## Update 2026-08-20 — Phase 2 COMPLETE
**Done:** auth+RBAC+audit (`auth.py`), reranker (`rerank.py` wired into engine), crawler
robots.txt + per-host throttle (`ingest/fetch.py`), `/health/providers`, 75% coverage gate.
**Verification:**
- `ruff check .` → All checks passed! (PASS)
- `pytest --cov=llm_search --cov-fail-under=75` → 31 passed, 76.5% coverage (PASS)
- Knowledge graph rebuilt → 108→ (re-run) nodes/edges updated.
**Next action:** Phase 4 options — (a) real JWKS/OIDC signature verification + discovery,
(b) cross-encoder reranker (ms-marco) for relevance, (c) crawl queue/sitemap/incremental
re-crawl, (d) UI (React) + SSO login. Awaiting user direction.

### Update 2026-08-20 — Phase 4 COMPLETE
**Done:** cross-encoder reranker (`reranker=cross-encoder`, guarded sentence-transformers,
injectable scorer) + eval harness (`llm_search.eval`: recall@k, precision@k, MRR).
**Verification:**
- `ruff check .` → All checks passed! (PASS)
- `mypy .` → Success: no issues found in 35 files (PASS)
- `pytest --cov=llm_search --cov-fail-under=80` → 48 passed, 4 skipped, 83.8% coverage (PASS)
- Knowledge graph rebuilt → 185 → updated nodes/edges.
**Next action:** Phase 5 options — (a) run offline eval lexical-vs-cross-encoder on a gold
set + tune rerank_multiplier, (b) real JWKS/OIDC signature verification, (c) crawl
queue/sitemap/incremental re-crawl, (d) React UI + SSO login. Awaiting user direction.

### Update 2026-08-20 — Phase 5 COMPLETE
**Done:** `llm_search/crawl` orchestrator (BFS, same-domain filter, dedupe, sitemap
discovery, incremental `CrawlState`) + `engine.crawl_site` + `POST /crawl` endpoint.
**Verification:**
- `ruff check .` → All checks passed! (PASS)
- `mypy .` → Success: no issues found in 37 files (PASS)
- `pytest --cov=llm_search --cov-fail-under=80` → 54 passed, 4 skipped, 82.9% coverage (PASS)
- Knowledge graph rebuilt → 203 → updated nodes/edges.
**Next action:** Phase 6 options — (a) offline eval lexical-vs-cross-encoder + tune,
(b) real JWKS/OIDC signature verification, (c) crawl concurrency/queue + true incremental
re-crawl via ETag, (d) React UI + SSO login. Awaiting user direction.

### Update 2026-08-20 — Phase 6 COMPLETE
**Done:** `OidcVerifier` now performs real RS256 signature verification via JWKS (discovery
or injected `get_jwks`); `pyjwt` added as runtime dep, `cryptography` for tests; unit tests
sign with a generated RSA key and assert verify/tamper/issuer/role behavior.
**Verification:**
- `ruff check .` → All checks passed! (PASS)
- `mypy .` → Success: no issues found in 37 files (PASS)
- `pytest --cov=llm_search --cov-fail-under=80` → 55 passed, 4 skipped, 83.2% coverage (PASS)
- Knowledge graph rebuilt → updated nodes/edges.
**Next action:** Phase 7 options — (a) offline eval lexical-vs-cross-encoder + tune
rerank_multiplier, (b) crawl concurrency/queue + true incremental re-crawl via ETag,
(c) React UI + SSO login, (d) CI pipeline (GitHub Actions: lint+type+test+audit+image).

### Update 2026-08-20 — Phase 7 (CI/CD) COMPLETE
**Done:** GitHub Actions `ci.yml` (ruff + mypy + pytest-cov@80% + pip-audit + gitleaks +
docker build) and `release.yml` (GHCR push on tags); `pre-commit` gained mypy; `Makefile`
mirrors all targets; `.dockerignore`; `tests/test_ci.py` parses the workflow YAML (YAML 1.1
`True` key handled). `pyyaml` added to dev deps.
**Verification:**
- `ruff check .` → All checks passed! (PASS)
- `mypy .` → Success: no issues found in 38 files (PASS)
- `pytest --cov=llm_search --cov-fail-under=80` → 58 passed, 4 skipped, 83% coverage (PASS)
- `make ci` (lint/type/cov) → ruff+mypy+pytest all green (PASS)
- Knowledge graph rebuilt → 226 → updated nodes/edges.
**Next action:** Phase 8 options — (a) offline eval lexical-vs-cross-encoder + tune
rerank_multiplier, (b) crawl concurrency/queue + true incremental re-crawl via ETag,
(c) React UI + SSO login, (d) actually wire a git remote + push to trigger CI.

### Update 2026-08-20 — Phase 8 (offline eval) COMPLETE
**Done:** `FakeEmbedding` is now lexical (bag-of-words, deterministic) so offline RAG +
retrieval are sensible; added `scripts/run_eval.py` (recall@k/precision@k/MRR + `--gate-mrr`)
over a gold corpus through the real `SearchEngine`, plus tests. Fixed a flaky network-dependent
crawl test by injecting `robots_fn` (default does a real robots.txt fetch).
**Verification:**
- `ruff check .` → All checks passed! (PASS)
- `mypy .` → Success: no issues found in 39 files (PASS)
- `pytest --cov=llm_search --cov-fail-under=80` → 59 passed, 4 skipped, 82.6% coverage (PASS)
- `python scripts/run_eval.py` → recall@k=1.0, precision@k=0.25, mrr=1.0 (lexical demo) (PASS)
- Knowledge graph rebuilt → 231 → updated nodes/edges.
**Next action:** Phase 9 options — (a) lexical-vs-cross-encoder comparison on a real gold set
+ tune `rerank_multiplier`, (b) crawl concurrency/queue + true incremental re-crawl via ETag,
(c) React UI + SSO login, (d) wire a git remote + push to trigger CI.

### Update 2026-08-20 — Phase 9 (concurrent + incremental crawl) COMPLETE
**Done:** `crawl_site` fetches up to `CRAWL_CONCURRENCY` (default 4) pages via ThreadPoolExecutor;
`Document` carries `etag`/`last_modified`; `fetch_url` does conditional GETs (returns None on 304);
re-crawls pass a seeded `CrawlState` to skip unchanged pages (not re-ingested). `config.crawl_concurrency`
added + wired into `engine.crawl_site`. Tests cover dedupe, 304-skip, changed-reingest, concurrency.
**Verification:**
- `ruff check .` → All checks passed! (PASS)
- `mypy .` → Success: no issues found in 39 files (PASS)
- `pytest --cov=llm_search --cov-fail-under=80` → 62 passed, 4 skipped, 83% coverage (PASS)
- Knowledge graph rebuilt → 236 → updated nodes/edges.
**Next action:** Phase 10 options — (a) lexical-vs-cross-encoder eval on a real gold set + tune
`rerank_multiplier`, (b) persistent CrawlState storage across runs + 429 backoff, (c) React UI +
SSO login, (d) wire a git remote + push to trigger CI.

### Update 2026-08-20 — eval wired into CI (quality gate)
**Done:** `.github/workflows/ci.yml` now runs `python scripts/run_eval.py --gate-mrr 0.5` as a
gate; `Makefile` gained `eval` and `ci` depends on it; added reproducible `tests/gold/eval_gold.json`
+ a `--gold` test. **Verification:** ruff/mypy clean; pytest 64 passed/4 skipped/83% cov;
`python scripts/run_eval.py --gate-mrr 0.5` → MRR 1.0 (PASS); knowledge graph rebuilt.

### Update 2026-08-20 — AGY collaboration: persistent CrawlState + 429 backoff
**Done (by AGY agent via `agy` CLI, verified here):** `CrawlState.save(path)`/`load(path)`
(JSON, empty on missing) for durable incremental re-crawl; `fetch_url` 429/Retry-After
exponential backoff (3 retries, injectable sleep). New tests: `test_crawl_state_save_load`,
`test_crawl_state_load_non_existent`, `test_fetch_handles_429_*`.
**Verification (independent re-run):** ruff clean; mypy clean; `pytest --cov-fail-under=80`
→ 67 passed, 4 skipped, 83% coverage.

### Update 2026-08-20 — repo wired + CLI/UI + observability + rerank sweep
**Done:** Git repo created at github.com/pal404error/sift and `main` pushed (initial commit +
iterative pushes). Collaborated with AGY (via `agy` CLI, `--dangerously-skip-permissions`):
 - `sift` CLI (serve/ingest/crawl/search/ask) + console script in pyproject; static web UI at
   `GET /`; tests in `tests/test_cli.py`.
 - Observability: thread-safe `Metrics` + `GET /metrics` (Prometheus-style) + `GET /health/live`
   + `GET /health/ready` (503 generic detail). Tests in `test_api.py`.
 - Fixed latent mypy errors in optional providers (openai/anthropic/qdrant) that only appeared
   once SDK deps installed via `pip install -e .` (would have broken CI).
 - Added `scripts/run_eval.py --rerank-multipliers` sweep (comparison table).
**Verification (each step, independent re-runs):** ruff clean; mypy clean (41 files); pytest
74 passed/6 skipped/83% cov. CI workflow now exercises real SDK stubs.
**Next action:** Phase 11 options — (a) real gold set + lexical-vs-cross-encoder eval to truly
tune rerank_multiplier, (b) more AGY collab (e.g. /metrics Prometheus scrape config, React UI),
(c) DB-backed CrawlState, (d) cut a v0.1.0 release tag + CHANGELOG.

**Key references:** `RTK.md` (truth), `trending-insights.md` (seed), `memory/*`, `skills/`.
