# RTK.md — Rules, Tech & Knowledge

> Project: **LLM-search** — a retrieval-augmented search system over LLMs.
> Living document. Updated after every meaningful change (see §7 self-improvement).
> Companion files: `trending-insights.md`, `memory/`, `skills/`.

---

## 1. RULES (non-negotiable conventions)

- **Formatting:** Enforce via pre-commit.
  - Python: **Ruff** (lint+format) + **Black** + **isort**. One canonical import order.
  - TypeScript: **Prettier** + **ESLint** (flat config). No unformatted commits.
- **No secrets in commits:** Use `.env.example` with placeholders and a secrets manager
  (GitHub Secrets / Vault). `.env`, credentials, and model weights are git-ignored.
- **TDD where applicable:** Write tests before implementation for core logic
  (retrieval, ranking, chunking, embeddings). Tests are the spec.
- **Destructive operations require confirmation:** DB migrations, file/collection
  deletions, and force-pushes must be confirmed by a human before execution.
- **Atomic changes:** One focus per change. Conventional Commits
  (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`). Clear, imperative messages.
- **Verification before claims:** Never say "done/fixed/passing" without running the
  verification command and showing its output (lint, typecheck, test, build).
- **Coverage threshold:** `pytest --cov=llm_search --cov-fail-under=80` must pass on every
  change; new core logic ships with tests.
- **Typecheck:** `mypy .` must be clean on every change (quality gate, alongside ruff).
- **Integration tests:** real OpenAI/Anthropic/Ollama paths live in
  `tests/test_integration_providers.py` under `@pytest.mark.integration`; they skip cleanly
  without API keys (CI stays air-gapped).
- **Security by default:** Treat all untrusted input (user queries, fetched web content,
  uploaded docs) as hostile. Sanitize/validate. Pin dependencies + audit on every PR.

---

## 2. TECH (stack & ADRs)

### 2.1 Chosen Stack (exact versions)

| Layer        | Choice | Version | Notes |
|--------------|--------|---------|-------|
| Language (backend) | Python | 3.12.x | Mature LLM/RAG ecosystem |
| Web framework | FastAPI | 0.115.x | Async, OpenAPI auto-docs |
| Data validation | Pydantic | v2.x | Request/response models |
| Embeddings | sentence-transformers | 3.x | Local + HF Hub models |
| Vector store | Qdrant | 1.11.x | gRPC/REST, filters, fast |
| Orchestration | LangChain | 0.3.x | Optional; used for chains |
| LLM client | openai / anthropic SDK | latest | Pluggable providers |
| Task queue | Celery + Redis | 5.4 / 7.x | Async ingestion jobs |
| Frontend | TypeScript + React | 5.x / 18.x | Vite build |
| UI state | TanStack Query | 5.x | Server-state caching |
| Tests (py) | pytest | 8.x | unit + integration |
| Tests (ts) | Vitest + Playwright | 2.x / 1.x | unit + e2e |
| Lint/Format (py) | Ruff + Black + isort | 0.6 / 24.x / 5.x | pre-commit |
| Lint/Format (ts) | ESLint + Prettier | 9.x / 3.x | pre-commit |
| CI/CD | GitHub Actions | — | lint/type/test/build/audit |
| Container | Docker + docker-compose | — | dev + prod profiles |

### 2.2 Architecture Decision Records (ADRs)

- **ADR-001 — Python 3.12 backend.**
  *Context:* Domain is LLM/RAG; 56% of top-50 trending repos are Python.
  *Decision:* Python 3.12.
  *Rationale:* Largest ecosystem (transformers, langchain, vllm), async support, mature
  tooling (pytest, ruff). Performance-critical paths can drop to Rust later.

- **ADR-002 — FastAPI over Django/Flask.**
  *Context:* Need async I/O for concurrent LLM/embedding calls and streaming.
  *Decision:* FastAPI.
  *Rationale:* Native async, automatic OpenAPI docs (good API contract), Pydantic v2
  integration, lower boilerplate than Django for an API-first service.

- **ADR-003 — Qdrant as vector store.**
  *Context:* Need filtered vector search with low latency.
  *Decision:* Qdrant.
  *Rationale:* Purpose-built vector DB, strong filtering, REST+gRPC, easy local docker
  dev. (Alternatives: pgvector — simpler ops but slower at scale; Milvus — powerful but
  heavier.)

- **ADR-004 — sentence-transformers for embeddings.**
  *Context:* Need reproducible, local-first embeddings with HF model swap.
  *Decision:* sentence-transformers on top of HF `transformers`.
  *Rationale:* Standard in the ecosystem (22/50 trending repos touch RAG/embeddings),
  model portability, no vendor lock-in.

- **ADR-005 — pnpm (frontend) + uv/poetry (backend), commit lockfiles.**
  *Context:* Reproducible builds across environments.
  *Decision:* Lockfiles mandatory (`pnpm-lock.yaml`, `uv.lock`/`poetry.lock`).
  *Rationale:* 100% of analyzed mature repos commit lockfiles; prevents supply-chain drift.

- **ADR-006 — GitHub Actions + pre-commit.**
  *Context:* Enforce quality gates automatically.
  *Decision:* pre-commit for local hooks; Actions for CI (lint, typecheck, test, build,
  `pip-audit`/`npm audit`, secret scan).
  *Rationale:* Universal in the domain (12/12 deep-dives use GitHub Actions).

- **ADR-007 — Bearer-token auth + RBAC + audit log (enterprise).**
  *Context:* Self-hosted deployment needs access control and compliance trail.
  *Decision:* Env-driven API keys (`role:key`), FastAPI `Security` dependency gating
  `/ingest`/`/search`/`/ask`; `admin` > `user`; JSONL audit log; `/health` open.
  *Rationale:* Minimal dependency surface, no external IdP required for v1; SSO/RBAC
  extension point noted. Fail-open when `REQUIRE_AUTH=false` (dev-friendly).

- **ADR-008 — Rerank stage + crawler politeness + coverage gate.**
  *Context:* Raw vector top-k is noisy; crawlers must be polite; quality must be enforced.
  *Decision:* retrieve `rerank_multiplier × k` then rerank (lexical default); honor
  `robots.txt` + per-host `MIN_CRAFT_INTERVAL`; enforce `pytest --cov-fail-under=80`.
  *Rationale:* Cheap precision win; legal/ethical crawling; trending repos underuse
  explicit coverage thresholds—this differentiates.

  *Rationale:* Typed code catches whole classes of bugs; the verifier abstraction lets
  SSO drop in without touching route code. OIDC signature verification left extensible
  (JWKS) to avoid heavy deps in core.

  *Rationale:* cross-encoders materially improve precision over bi-encoders; the eval
  module gives an objective gate and aligns with the "quality by default" posture. Model
  load is lazy/optional so core stays dependency-light.

- **ADR-011 — Crawl orchestrator (BFS + incremental state).**
  *Context:* A "web search engine" must ingest more than one URL; naive recursion is
  unbounded and impolite.
  *Decision:* `llm_search.crawl` does BFS with same-domain filtering, dedupe via `CrawlState`,
  robots.txt + per-host throttle (reuses `ingest.fetch`), sitemap discovery, and
  `MAX_PAGES_PER_INGEST` bound. `fetch_fn`/`robots_fn` are injectable for tests.
  *Rationale:* bounded, polite, deterministic, and fully testable without network; the
  incremental `CrawlState` (ETag/Last-Modified) enables cheap re-crawls later.

- **ADR-012 — OIDC signature verification via JWKS.**
  *Context:* Phase 3's `OidcVerifier` only decoded claims without verifying the signature
  (untrusted tokens could be forged).
  *Decision:* `OidcVerifier` now fetches JWKS (`{issuer}/.well-known/openid-configuration`
  → `jwks_uri`, or an injected `get_jwks`), selects the key by `kid`, and verifies the
  RS256 signature via PyJWT before trusting `iss`/`aud`/roles. `pyjwt` is a runtime dep.
  *Rationale:* real SSO security requires signature verification; the injectable `get_jwks`
  keeps it fully testable offline (unit test signs with a generated RSA key).

- **ADR-013 — CI/CD pipeline codifies the quality gates.**
  *Context:* an enterprise self-host project needs the lint/type/test/audit gates to run
  automatically on every change, not just locally.
  *Decision:* `.github/workflows/ci.yml` runs `ruff`, `mypy`, `pytest` (cov 80% floor),
  `pip-audit` + `gitleaks`, then a Docker build; `release.yml` pushes to GHCR on tags.
  `pre-commit` mirrors ruff+prettier+gitleaks+mypy locally; `Makefile` exposes the same
  targets. CI YAML is itself unit-tested (`tests/test_ci.py`).
  *Rationale:* gates that don't run in CI drift; config-as-code tested in-repo prevents
  breakage and documents the contract.

- **ADR-014 — Lexical fake embeddings + runnable offline eval.**
  *Context:* the fake `EmbeddingProvider` returned random vectors, so offline RAG + the
  eval harness (ADR-010) produced meaningless, near-random retrieval.
  *Decision:* `FakeEmbedding` now hashes tokens into a bag-of-words vector (deterministic,
  cosine tracks token overlap). `scripts/run_eval.py` ingests a gold corpus through the real
  `SearchEngine` and reports recall@k/precision@k/MRR; `--gate-mrr` can fail CI. The crawl
  test injects `robots_fn` to stay offline (default `robots_fn` hits the network).
  *Rationale:* fakes should be useful for local dev/demo, and eval must be runnable without
  keys/network; tests must never depend on the network (flaky/hangs).

- **ADR-015 — Concurrent, ETag-aware incremental crawl.**
  *Context:* a real search engine must crawl many pages quickly and re-crawl cheaply
  (don't re-embed unchanged pages).
  *Decision:* `crawl_site` fetches up to `CRAWL_CONCURRENCY` (default 4) pages via a
  `ThreadPoolExecutor`; `Document` now carries `etag`/`last_modified`; `fetch_url` does
  conditional GETs and returns `None` on 304. Re-crawls pass a `CrawlState` seeded with
  prior ETags; unchanged pages are skipped (not re-ingested). A `discovered` set dedupes
  within a run. `crawl_fn` is arity-probed so 1-arg fakes stay compatible.
  *Rationale:* bounded, polite, fast, and cheap re-crawls; fully testable offline (injectable
  fetch returns `None` to simulate 304).

- **ADR-016 — Persistent CrawlState + 429 backoff (collab w/ AGY).**
  *Context:* incremental re-crawl (ADR-015) was in-memory only, so it couldn't survive a
  restart, and the fetcher had no backoff for `429 Too Many Requests`.
  *Decision:* `CrawlState` gained `save(path)`/`load(path)` (plain JSON of the visited/ETag
  map, empty on missing file). `fetch_url` retries up to 3 times on 429, honoring
  `Retry-After` (else `2**retries` exponential), via the injectable `sleep`. Added tests.
  *Rationale:* incremental crawls become durable across restarts; polite backoff avoids
  hammering rate-limited servers. Implemented by the AGY collaborator agent.

- **ADR-017 — Observability: metrics + liveness/readiness probes.**
  *Context:* an enterprise deployment needs health checks for orchestrators (k8s/Docker)
  and basic request metrics, with zero new runtime dependencies.
  *Decision:* `llm_search/api.py` has a thread-safe in-process `Metrics` (total/per-route/
  5xx counts + rolling latency window capped at 1000) recorded by middleware, exposed at
  `GET /metrics` (Prometheus-style text). `GET /health/live` always 200; `GET /health/ready`
  checks store + provider config and returns 503 with a **generic** detail (no exception
  leakage) otherwise. AGY implemented; we hardened the 503 detail.
  *Rationale:* operability + secure-by-default health endpoints.

- **ADR-018 — Offline rerank-multiplier sweep.**
  *Context:* the reranker's `rerank_multiplier` (candidate pool size) needs tuning, but
  doing so meaningfully requires a real corpus. Offline, the lexical-fake eval still lets
  us demonstrate the sweep harness.
  *Decision:* `scripts/run_eval.py --rerank-multipliers 1,3,5,10` builds an engine per value
  and prints a recall@k/precision@k/MRR comparison + the best. `rerank_multiplier` stays `int`
  (used as a count). Closes the open "tune rerank_multiplier" item (sweep harness; real tuning
  needs a semantic gold set + real providers).
  *Rationale:* makes the eval tool actionable and reproducible.

- **ADR-019 — Hybrid retrieval via Reciprocal Rank Fusion (RRF).**
  *Context:* pure dense-vector retrieval misses exact-match / rare-term queries that
  lexical matching catches, and vice-versa. Competitors (e.g. langchain, dify) ship hybrid
  search as a quality differentiator.
  *Decision:* added `llm_search/lexical_index.py` (dependency-free BM25-lite inverted index)
  and wired it into `SearchEngine.search`: when a `LexicalIndex` is present (auto-created when
  `Settings.hybrid=True`, or injected), vector top-k and lexical top-k are fused by RRF
  (`score += 1/(rrf_k + rank)`) before reranking. New settings: `hybrid: bool = False`,
  `rrf_k: int = 60`. Off by default; fully testable offline (no new runtime deps).
  *Rationale:* directly multiplies the headline "retrieval quality" metric at zero dependency
  cost; lexical payloads are mirrored in the index so lexical-only hits surface in results.

- **ADR-020 — HyDE query expansion.**
  *Context:* short natural-language questions are often a poor match for the dense vectors
  of the passages they seek (query/document vocabulary mismatch). Hypothetical Document
  Embeddings (HyDE) mitigates this by having the LLM draft a plausible answer passage, then
  embedding *that* for retrieval.
  *Decision:* `SearchEngine.ask` gains `use_hyde` (defaults to `Settings.use_hyde`). When on,
  it asks the LLM for a short passage, concatenates it to the query, and retrieves on the
  combined text; the final answer is still generated strictly from retrieved context. New
  setting `use_hyde: bool = False`. Fully testable offline (FakeLLM path exercised in
  `tests/test_hyde.py`).
  *Rationale:* a cheap, well-known retrieval booster that composes with hybrid+RRF; off by
  default so behavior is unchanged unless opted in.

- **ADR-021 — Streaming answers (SSE).**
  *Context:* a 60s demo and interactive UIs feel far more alive when the answer streams in
  token-by-token rather than appearing all at once after a long generation delay.
  *Decision:* added `LLMProvider.stream(system, prompt)` (default yields the full `generate`
  output in one chunk, so every provider streams safely; OpenAI/Anthropic override with native
  token streaming). `SearchEngine.ask_stream` emits SSE-friendly events — first
  `{"type":"sources",...}` then `{"type":"token","text":...}` — and `GET /ask/stream` serves
  them as `text/event-stream`. CLI `ask`/`search` gained `--hybrid`/`--hyde` flags that set the
  corresponding env vars before the engine is built. Covered by `tests/test_stream.py`.
  *Rationale:* genuine demo/UX lift, fully testable offline (FakeLLM fallback), and consistent
  with the "developer-first, batteries-included" posture.

- **ADR-022 — Configurable hybrid fusion (RRF vs weighted).**
  *Context:* research (`research/RETRIEVAL_NOTES.md`) notes RRF is the robust default but
  weighted fusion with a tuned `alpha` can help once you have an eval set. We should support
  both without forcing a choice at code level.
  *Decision:* added `Settings.hybrid_mode` (`"rrf"` | `"weighted"`, default `"rrf"`) and
  `hybrid_alpha` (default `0.5`). `SearchEngine.search` dispatches: RRF (rank positions) or
  weighted (min-max normalize each signal to [0,1], blend `alpha*vector + (1-alpha)*lexical`).
  Normalization is mandatory because cosine ([-1,1]) and BM25-lite (unbounded) are not
  comparable. RRF stays default; weighted is opt-in. Covered by `tests/test_hybrid.py`.
  *Rationale:* gives advanced users a tunable lever (and a path to query-style routing later)
  while keeping the safe default. Honest: weighted is only better *with* an eval set to tune.

### 2.3 Dependency Policy
- Prefer libraries already in the repo. Add new deps only after review + security scan
  (`pip-audit` / `npm audit` / `cargo audit`).
- Pin versions; use ranges only for dev tooling. No unpinned `latest`.
- New dependency proposal → issue + ADR note; record in `memory/decisions.log`.

---

## 3. KNOWLEDGE (domain & gotchas)

### 3.1 Domain Glossary
- **RAG (Retrieval-Augmented Generation):** Augment LLM answers with retrieved context.
- **Embedding:** Dense vector representation of text for similarity search.
- **Chunk:** A segmented unit of a document fed to embedding/retrieval.
- **Retriever:** Component that fetches top-k relevant chunks for a query.
- **Re-ranker:** Model that reorders retrieved chunks by relevance.
- **Vector store / ANN index:** Database optimized for nearest-neighbor search.
- **Token:** Unit of text processed by the LLM; affects cost and context limits.
- **Context window:** Max tokens an LLM can consider in one call.
- **Hallucination:** LLM output not grounded in retrieved context.

### 3.2 Known Gotchas
- **Chunk size vs. recall:** Too large → low granularity; too small → lost context.
  Typical 256–512 tokens with 10–20% overlap.
- **Embedding model drift:** Swapping models invalidates existing vectors — requires
  re-indexing. Pin the model version.
- **Dimension mismatch:** Query and document embeddings must use the same model/dim.
- **Rate limits:** LLM + embedding APIs throttle; implement backoff + retry.
- **Cold-start latency:** First retrieval after restart can be slow (model load) — warm up.
- **Context stuffing:** Stuffing too many chunks blows the context window and costs tokens.
- **Non-determinism:** `temperature>0` makes answers vary; use `0` for eval/repro.
- **Web content sanitization:** Scraped HTML may contain scripts/markup — sanitize before
  embedding or display (XSS risk).

### 3.3 External API Contracts
- **LLM Provider (OpenAI-compatible):**
  - Endpoint: `POST /v1/chat/completions`
  - Auth: `Authorization: Bearer $LLM_API_KEY`
  - Rate limit: provider-dependent (handle 429 with exponential backoff).
  - Error codes: 401 (auth), 429 (rate), 500 (server).
- **Embedding endpoint:** `POST /v1/embeddings` (same auth).
- **Qdrant:** `POST /collections/{name}/points/search` (REST) or gRPC `:6334`.
  - Auth: API key header `api-key: $QDRANT_API_KEY`.
- **Web fetch (optional, for indexing):** honor `robots.txt`, set User-Agent, timeout.

### 3.4 Environment Variables (placeholders)
```
DATABASE_URL=<set-me>            # primary metadata DB (Postgres)
QDRANT_URL=<set-me>              # e.g. http://localhost:6333
QDRANT_API_KEY=<set-me>
LLM_PROVIDER=<set-me>            # openai | anthropic | ...
LLM_API_KEY=<set-me>
LLM_MODEL=<set-me>               # e.g. gpt-4o-mini
EMBEDDING_MODEL=<set-me>         # e.g. sentence-transformers/all-MiniLM-L6-v2
REDIS_URL=<set-me>               # Celery broker/result
SECRET_KEY=<set-me>              # app signing secret
LOG_LEVEL=<set-me>               # INFO
```
(Provide a `.env.example`; never commit real values.)

---

*RTK is the seed of truth. When a gotcha is learned or a stack decision changes, edit this
file, log it in `memory/decisions.log`, and refresh `memory/knowledge-graph.json`.*
