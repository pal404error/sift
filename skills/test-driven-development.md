---
name: test-driven-development
description: Red-green-refactor for core logic. Write the failing test first.
trigger: Implementing retrieval, ranking, chunking, parsing, or any core algorithm.
discipline: Tests are the spec. No implementation without a failing test for core logic.
---

# Test-Driven Development

Goal: drive correctness via tests, not after-the-fact coverage.

## Loop
1. **RED** — write a failing test for the next small behavior. Run it; see it fail (with a
   clear message, not an error).
2. **GREEN** — write the minimal implementation to pass.
3. **REFACTOR** — clean up, keep tests green. No new behavior here.

## Scope rules (from RTK.md RULES)
- Core logic (retrieval, ranking, chunking, embeddings, rerank): TDD mandatory.
- Integration tests that need API keys / Qdrant / Redis: mark with markers
  (`@pytest.mark.integration`) and skip when env vars absent.
- Unit tests must be fast and hermetic (no network).

## Commands (verify, don't claim)
```
pytest -q                       # unit
pytest -q -m integration        # integration (needs env)
pytest --cov=src --cov-fail-under=80
```
Show the output. A green run is the only proof of "passing".

## After green
Update `memory/knowledge-graph.json` (run rebuild script) and note new modules in
`memory/decisions.log` if design changed.
