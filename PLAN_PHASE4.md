# PLAN — LLM-search Phase 4 (reranker quality + evaluation)

Goal: improve retrieval precision with a cross-encoder reranker (optional/guarded) and add
an evaluation harness (recall@k, MRR) so quality is measurable, not assumed.

## Success criteria (verify before claiming done)
- [ ] `ruff check .` → 0 errors
- [ ] `mypy .` → 0 errors
- [ ] `pytest --cov=llm_search --cov-fail-under=80` → pass
- [ ] `reranker=cross-encoder` supported (guarded sentence-transformers; injectable scorer)
- [ ] `eval.py` exposes recall_at_k / precision_at_k / mrr with unit tests
- [ ] README + RTK + knowledge graph updated

## Phases
1. **Cross-encoder reranker** — `CrossEncoderReranker` in `rerank.py` (injectable scorer +
   guarded `sentence_transformers.CrossEncoder`); wire into `build_reranker`. verify: test
   with fake scorer ranks correctly.
2. **Eval harness** — `llm_search/eval.py` (recall@k, precision@k, MRR). verify: unit tests.
3. **Coverage** — add tests; keep ≥80%. verify gate.
4. **Docs + graph** — README eval/reranker section; RTK ADR-010; rebuild graph; logs.
