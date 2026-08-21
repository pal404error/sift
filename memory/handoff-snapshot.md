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

### Update 2026-08-20 — Professional repo polish (GH Pages + tags + humanized docs)
**Done (collab with AGY + own corrections):** Humanized `README.md` (accurate shields.io badges:
live CI status, 83% coverage, MIT, Python 3.12+, Docker, OIDC; fixed a fabricated 95% coverage
and a "React" UI claim → plain HTML). `docs/index.html` responsive GitHub Pages landing page
+ `docs/.nojekyll`. `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`,
`LICENSE` (MIT). Set repo metadata via API: description, homepage `https://pal404error.github.io/sift/`,
14 discovery topics. Enabled GitHub Pages (source main `/docs`, legacy build). Cut annotated
`v0.1.0` tag + GitHub release.
**Verification:** `git push` OK; `curl https://pal404error.github.io/sift/` → HTTP 200;
`curl https://github.com/pal404error/sift` → HTTP 200; release at `/releases/tag/v0.1.0`.
**Next action:** Phase 11 options — (a) real gold set + cross-encoder eval to truly tune
rerank_multiplier, (b) AGY: /metrics Prometheus scrape config / React UI, (c) DB-backed
CrawlState, (d) future tags v0.1.x as fixes land.

### Update 2026-08-20 — Monitoring stack (Prometheus + Grafana)
**Done:** `prometheus/prometheus.yml` (scrape sift `/metrics`, 15s); `grafana/provisioning/datasources/datasource.yml`
(pre-provisioned Prometheus); `docker-compose.yml` adds `prometheus` + `grafana` under a
`monitoring` profile (`docker compose --profile monitoring up -d`); README "Monitoring" section.
**Verification:** YAML parses (all 3 configs); `ruff check .` clean; `pytest tests/test_api.py`
4 passed (metrics/health). Pushed `920982c`.

### Update 2026-08-20 — Landing page revamp (vibe-coding framework + AGY)
**Done (collab with AGY, verified here):** Applied two reference articles — (1) landing-page
best practices (clear header/main/footer, mobile responsiveness, SEO meta + OG + JSON-LD, strong
top-fold + CTAs) and (2) the 4-part vibe-coding prompt framework (Identity/Audience/Features/
Aesthetic with specific technical constraints). AGY rewrote `docs/index.html`: sticky header +
mobile hamburger, hero with gradient headline + subtle grid bg + copy-to-clipboard install
snippet, 6-card feature grid, 3-step "How it works", quickstart code block, accessible FAQ
accordion (`<details>`), final CTA, multi-column footer. Self-contained vanilla HTML/CSS/JS
(no CDNs/build step). Preserved SEO tags. Fixed hero install to valid PEP 508 (no `all` extra).
**Verification:** python3 HTML parse OK; zero external resource refs (excl. github/schema);
all required sections + SEO present; no fabricated social proof/metrics. Pushed `b9d64da`.

### Update 2026-08-20 — Newspaper theme (Helvetica BOLD)
**Done:** User requested a newspaper theme with Helvetica BOLD font all over. Rewrote
`docs/index.html` styling: Helvetica/Arial base, `font-weight: 700` body (bold throughout),
900-weight headlines; newsprint palette (#f4f1e9 / #111 ink), thick rules + double borders,
masthead with dateline "Vol. 1 — No. 1", kickers/section labels, bordered feature columns,
terminal "wire" code box, uppercase bold CTAs. Kept all sections/FAQ/copy/hamburger + SEO/OG/JSON-LD;
still self-contained (no external resources).
**Verification:** python3 parse OK; Helvetica+bold confirmed; zero external refs; sections/SEO present;
no fabricated claims. Pushed `74acda9`.

### Update 2026-08-20 — 3-Hour "100x" plan + execution (collab: agent + AGY)
**Plan:** Created PLAN_100x.md via AGY (3 hourly blocks). NotebookLM could NOT be used —
auth expired (AUTH_EXPIRED); user must run `save_auth_tokens` with fresh cookies to loop it in.
Agent analysis found the **eval was a tautology** (lexical fake embeddings + lexical reranker
over a 4-doc gold set where queries share tokens with answers -> MRR~1.0 proves nothing) and
the demo started empty. That is the real "100x" lever.
**Hour 1 executed + verified (pushed `a9fd184`):**
- Added `local` embedding provider (`llm_search/providers/local.py`, sentence-transformers MiniLM;
  optional dep). `build_embedding` now supports "local".
- `scripts/run_eval.py` gained `--embedding {fake,local}`, `--reranker {lexical,cross-encoder}`,
  `--compare` (side-by-side table).
- New `tests/gold/eval_gold_semantic.json` (16 docs / 16 queries: paraphrases, synonyms,
  multi-hop, no token overlap) -> CI gate asserts MRR < 0.7 (non-trivial).
- Measured: fake+lexical MRR **0.124** vs local+cross-encoder MRR **0.593** (recall@5 0.81) ->
  a real ~5x relevance lift on hard queries. `rerank_multiplier=2` already optimal.
- Added `sift demo` zero-config command (seeds bundled corpus, local+cross-encoder; verified
  live: OIDC query ranks 'oidc' #1). Added `semantic` pyproject extra; README retrieval-quality
  + live-demo sections. New offline CI test.
**Verification:** ruff clean; mypy clean (42 files); pytest 100% pass (6 skipped, 81.6% cov).
**Remaining (Hour 2/3):** polish in-app static UI (scores/highlights/citations), gate semantic
eval into CI as network-skippable job, crawl robustness (noindex/timeout/retry/tests), honest
README screenshot. NotebookLM synthesis once re-authed.
