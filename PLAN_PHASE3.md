# PLAN — LLM-search Phase 3 (type safety + SSO-ready auth + real-provider tests)

Goal: enforce static typing, make auth SSO-ready (pluggable verifiers: API-key + OIDC),
and prove real provider paths work via env-gated integration tests.

## Success criteria (verify before claiming done)
- [ ] `ruff check .` → 0 errors
- [ ] `mypy .` → 0 errors (config: ignore_missing_imports, lenient)
- [ ] `pytest --cov=llm_search --cov-fail-under=80` → pass (≥80%)
- [ ] Auth supports `AUTH_METHOD=oidc` verifier (PyJWT-guarded) + `apikey` (default)
- [ ] Integration tests for OpenAI/Anthropic/Ollama skip cleanly without keys
- [ ] README + RTK + knowledge graph updated

## Phases (atomic, verifiable)
1. **mypy config + install** — add `[tool.mypy]`; run; fix type errors. verify: `mypy .`
2. **SSO-ready auth** — `TokenVerifier` protocol; `ApiKeyVerifier` (current),
   `OidcVerifier` (PyJWT, iss/aud, JWKS cache, optional dep); `AUTH_METHOD` setting;
   wire into `require_role`. verify: unit tests (apikey + oidc w/ mocked decode).
3. **Provider integration tests** — `tests/test_integration_providers.py` marked
   `integration`, build real providers only if env keys present, else skip. verify: runs
   green (skips here), documents real path.
4. **Coverage to 80%** — add tests (auth verifiers, provider factory branches). verify gate.
5. **Docs + graph** — README SSO section; RTK ADR-009; rebuild graph; logs.
