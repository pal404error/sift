# PLAN — LLM-search Phase 2 (Enterprise hardening)

Goal: make the MVP enterprise-ready: authenticated + role-gated API with audit logging,
a reranker stage, crawler politeness (robots.txt + rate limits), provider health/validation,
and enforced test coverage.

## Success criteria (verify before claiming done)
- [ ] `ruff check .` → 0 errors, 0 warnings
- [ ] `pytest --cov=llm_search --cov-fail-under=75` → all pass, coverage ≥ 75%
- [ ] API key auth gates `/ingest`,`/search`,`/ask`; `/health` open; bad key → 401
- [ ] Reranker integrates (retrieve 2×k, rerank → k)
- [ ] Crawler honors robots.txt + per-host interval (mocked, no network in tests)
- [ ] `/health/providers` reports provider config without leaking secrets
- [ ] README + RTK + knowledge graph updated

## Phases (atomic, verifiable)
1. **Config** — add auth/robots/rerank settings. verify: import + defaults.
2. **Auth + RBAC** — `auth.py` (key lookup, role dependency, audit log). verify: tests
   (valid key passes, wrong role 403, missing 401).
3. **Reranker** — `rerank.py` (ABC + lexical + fake), wire into engine. verify: tests.
4. **Crawler politeness** — robots.txt (robotparser) + per-host throttle in fetch. verify:
   mocked httpx tests.
5. **Provider health/validation** — `/health/providers`; fail-fast on missing keys when
   provider != fake. verify: endpoint test.
6. **API wiring** — apply auth deps to routes; add provider health. verify: TestClient.
7. **Coverage** — add pytest-cov, threshold; add tests to reach ≥75%. verify gate.
8. **Docs + graph** — README auth/rerank/robots sections; RTK ADR; rebuild graph; logs.
