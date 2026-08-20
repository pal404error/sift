# Trending Insights — LLM / RAG / Search Ecosystem

> Seed for the project's RTK (Rules, Tech, Knowledge).
> Generated: 2026-08-20
> Source: GitHub Search API (`topic:<x> pushed:>2026-08-12`, sorted by stars, deduplicated).
> Scope: 164 unique repositories matched the LLM/RAG/semantic-search/vector-database/
> retrieval/embeddings/agentic clusters; top 50 ranked by stars. 12 representative repos
> received a deep-dive file-tree analysis (CI, deps, lint/format, docs, structure).

---

## 1. Sample & Methodology

- **Proxy for "trending":** GitHub's Search API does not expose the trending page.
  We used `topic:<cluster> pushed:>2026-08-12` (7-day activity window) sorted by stars,
  which captures *active, popular* repos in the domain rather than raw 7-day star velocity.
- **Clusters queried:** `rag`, `llm`, `semantic-search`, `vector-database`,
  `retrieval-augmented-generation`, `embeddings`, `agentic`.
- **Deep-dive set (12):** langchain-ai/langchain, langgenius/dify, infiniflow/ragflow,
  firecrawl/firecrawl, vllm-project/vllm, huggingface/transformers, open-webui/open-webui,
  browser-use/browser-use, ollama/ollama, supabase/supabase, NousResearch/hermes-agent,
  Significant-Gravitas/AutoGPT.
- **Limitations:** unauthenticated API rate limits prevented per-file README/PR extraction
  for all 50; deep-dive used recursive Git Trees (1 request/repo) to detect structural signals.

---

## 2. Language & Stack Distribution (Top 50)

| Language        | Count | Share |
|-----------------|-------|-------|
| Python          | 28    | 56%   |
| TypeScript      | 6     | 12%   |
| Go              | 5     | 10%   |
| JavaScript      | 4     | 8%    |
| Rust            | 4     | 8%    |
| HTML            | 1     | 2%    |
| Jupyter Notebook| 1     | 2%    |
| Java            | 1     | 2%    |

**Dominant topics:** `llm` (39), `ai` (26), `rag` (22), `ai-agents` (15), `openai` (15),
`python` (15), `agent` (12), `mcp` (9), `claude-code` (10), `anthropic` (9).

**Takeaway for LLM-search:** Python is the lingua franca of the domain (data ingestion,
embeddings, orchestration), with TypeScript/React for the UI layer and Go/Rust for
high-throughput serving. A modern LLM-search product should expect a **Python backend +
TypeScript frontend** split, optionally with a Rust/Go retrieval core.

---

## 3. Synthesized Patterns

### 3.1 Tech Stacks & Dependency Management
- **Backend (Python):** `pyproject.toml` + `poetry` (or `uv`) is the dominant standard
  (seen in langchain, dify, ragflow, AutoGPT, hermes-agent). `requirements.txt` persists
  for simpler services (open-webui, firecrawl examples).
- **Frontend (TS):** `package.json` + `pnpm` (or `npm`) with `pnpm-lock.yaml`. pnpm is
  preferred in larger monorepos (supabase, dify, firecrawl, AutoGPT).
- **Go:** `go.mod` + `go.sum` (ollama, ragflow, firecrawl). **Rust:** `Cargo.toml` +
  `Cargo.lock` (vllm rust core, firecrawl rust-sdk).
- **Monorepo pattern:** pnpm workspaces / cargo workspaces / poetry packages are common
  (supabase 16k files, dify, firecrawl, AutoGPT). Multi-package with clear `apps/`,
  `packages/`, `examples/` separation.
- **Dependency policy:** lockfiles are **always committed** (go.sum, Cargo.lock,
  pnpm-lock.yaml, poetry.lock). Reproducible builds are non-negotiable.

### 3.2 Testing Frameworks & Coverage
- **Python:** `pytest` is universal (unit_tests/ + integration_tests/ split, e.g.
  dify, langchain, ragflow). vllm and transformers use pytest + benchmarks.
- **TypeScript:** `vitest` / `jest` + `playwright` for e2e (supabase, dify, firecrawl,
  open-webui frontend).
- **Coverage:** most projects run CI test suites but **few publish explicit coverage
  thresholds** in config. The mature ones (vllm, transformers) gate merges on CI test
  pass + benchmark regression checks.
- **Pattern:** `tests/unit_tests/`, `tests/integration_tests/`, `e2e/` directory layout
  is near-universal. Separate integration tests that hit external services (LLM APIs,
  vector DBs) from fast unit tests.

### 3.3 Documentation Style
- **README.md** is universal; strong ones include: features list, architecture diagram
  (Mermaid/ASCII), quick-start, API examples, deployment (Docker), and a roadmap.
- **CONTRIBUTING.md** + **CODE_OF_CONDUCT.md** present in ~all mature repos.
- **Docs as code:** `docs/` directories with versioned/i18n subdirectories (dify,
  transformers, supabase). Docusaurus is common for agent frameworks (hermes-agent).
- **Inline READMEs** per module/provider (e.g. ragflow `api/providers/vdb/*/README.md`)
  document plugin contracts — a strong pattern for extensible systems.

### 3.4 Security Practices
- **Secret scanning:** `npm-audit` workflows (firecrawl has dedicated `npm-audit.yml` and
  `npm-audit-claude-remediation.yml`); pre-commit hooks for secret detection
  (`.pre-commit-config.yaml` with detect-secrets/secret-scan in vllm, AutoGPT,
  open-webui, browser-use).
- **Dependency audits:** `pip-audit`/`npm audit`/`cargo audit` wired into CI on PRs.
- **Supply chain:** pinned versions + lockfiles; some use dependabot/renovate.
- **SAST/DAST:** lighter presence; a few run CodeQL or semgrep-like actions, but it is
  **not yet standard** across the domain — an opportunity for differentiation.
- **Note:** Several projects keep `.env.example` / `.gitignore` strictly excluding
  `.env`, credentials, and model weights.

### 3.5 Automation & Release
- **CI/CD:** GitHub Actions is the universal choice (all 12 deep-dives use
  `.github/workflows/`). GitLab CI and Buildkite appear only in vllm (Buildkite for
  benchmarks) and a couple of others.
- **Pre-commit:** 5/12 deep-dives have `.pre-commit-config.yaml` (vllm, open-webui,
  browser-use, AutoGPT, ragflow). Ruff/black/isort for Python; prettier/eslint for TS.
- **Release:** semantic-versioned releases via tags; Docker image build + push to GHCR
  (firecrawl `deploy-image.yml`, ollama `release.yaml`); PyPI publish for Python libs
  (open-webui `release-pypi.yml`).
- **Conventional Commits:** strongly implied by release automation; several repos use
  release-please or semantic-release.
- **AI-assisted review:** emerging pattern — transformers `ai-review.yml`,
  firecrawl `npm-audit-claude-remediation.yml`, hermes `ci-review-comment.yml`.

### 3.6 Folder Structure Conventions
- `src/` or `backend/` + `frontend/` (or `web/`, `ui/`) split.
- `api/` (service layer), `tests/` (with `unit_tests/` + `integration_tests/`),
  `examples/` , `docs/`, `scripts/`, `docker/`.
- Provider/plugin extensibility via `providers/` or `plugins/` directories with isolated
  sub-packages (ragflow vdb-*, hermes plugins/, dify providers/).
- Agent frameworks separate `agent/`, `tools/`, `memory/`, `skills/` (hermes, AutoGPT,
  browser-use).

---

## 4. Notable Repos (Deep-Dive Highlights)

| Repo | Lang | Structure / Patterns |
|------|------|----------------------|
| langchain-ai/langchain | Py | Massive `pyproject.toml`, provider-based; pytest; docs as code |
| langgenius/dify | Py+TS | Monorepo (`api/`, `web/`, `packages/`), pnpm, GitHub Actions, i18n docs |
| infiniflow/ragflow | Py+Go | `go.mod`+`pyproject.toml`, `internal/` layout, 4 CI workflows, plugin READMEs |
| firecrawl/firecrawl | TS+Go+Py | Multi-SDK (`apps/*-sdk`), pnpm workspaces, `npm-audit`, prettier |
| vllm-project/vllm | Py+Rust | `pyproject.toml`+`Cargo.toml`, pre-commit, Buildkite benchmarks, mypy |
| huggingface/transformers | Py | `src/` layout, pytest, CircleCI+benchmarks, ai-review workflow |
| open-webui/open-webui | Py+TS | `backend/requirements.txt`+`pyproject.toml`, prettier, GHCR release |
| browser-use/browser-use | Py | `pyproject.toml`, pre-commit, `skills/` dir, lint+test workflows |
| ollama/ollama | Go | `go.mod`+`go.sum`, prettier for UI, multi-arch release CI |
| supabase/supabase | TS | Huge pnpm monorepo, eslint-config package, e2e + ai-tests |
| NousResearch/hermes-agent | Py+TS | `pyproject.toml`+pnpm, `plugins/`+`skills/`, docusaurus docs |
| Significant-Gravitas/AutoGPT | Py+TS | poetry workspaces, `.flake8`, pre-commit, docker CI |

---

## 5. Recommendations for THIS Project (LLM-search)

1. **Stack:** Python 3.12 backend (FastAPI) + TypeScript/React frontend (Vite),
   with an optional Rust retrieval core if latency demands it. (See RTK.md ADRs.)
2. **Packaging:** `pyproject.toml` + `uv`/`poetry`; `pnpm` + `package.json` for frontend;
   commit all lockfiles.
3. **Lint/Format:** Ruff + Black + isort (Python), Prettier + ESLint (TS), enforced via
   `.pre-commit-config.yaml`.
4. **Tests:** pytest (`tests/unit`, `tests/integration`), Vitest + Playwright (e2e);
   separate integration tests that need API keys/vector DBs.
5. **CI:** GitHub Actions — lint, typecheck, test, build, `pip-audit`/`npm audit`,
   secret-scan, Docker build, semantic-release.
6. **Docs:** README with architecture diagram (Mermaid), CONTRIBUTING, CODE_OF_CONDUCT,
   `docs/` with module-level READMEs for retrievers/providers.
7. **Security:** `.env.example` + secret scanning in pre-commit + dependency audit in CI.
8. **Differentiation:** add SAST (CodeQL/semgrep) and dependency provenance — underused in
   the domain.

---

*Raw scrape artifacts retained in `.scrape/` (top50.json, deepdive.json, per-cluster
responses) for reproducibility and periodic re-analysis.*
