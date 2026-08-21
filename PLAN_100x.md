# 100x Sift RAG Execution Plan

## 1. Goal
Make retrieval relevance measured + semantic, and the product demoable in 60s.

## 2. Collaborators
- **NotebookLM**: Intended for project synthesis, but its auth expired (user to re-run `save_auth_tokens`).
- **AGY**: Does implementation.
- **Subagents**: Do analysis/research.
- **Orchestrator (Human)**: Verifies gates.

## 3. Hour 1 — Establish truth: real semantic eval + semantic baseline
- **T1.1**: Build semantic gold set (>=20 docs, >=15 queries that FAIL lexical: paraphrases/synonyms/multi-hop, no token overlap) at `tests/gold/eval_gold_semantic.json`.
- **T1.2**: Add 'local' embedding provider (sentence-transformers `all-MiniLM-L6-v2`, dim 384) + confirm cross-encoder reranker lazy-loads.
- **T1.3**: Extend `scripts/run_eval.py` with `--embedding {fake,local}` and `--reranker {lexical,cross-encoder}` + side-by-side table.
- **Verifiable exits**: Semantic gold MRR < 0.7 with fake/lexical; cross-encoder MRR >= lexical on the table.

## 4. Hour 2 — Prove the 100x + make it demoable
- **T2.1**: Tune `rerank_multiplier` via sweep, set best default.
- **T2.2**: Add `sift demo` (or `sift serve --seed`) that ingests a bundled corpus on startup so UI returns real results.
- **T2.3**: Polish `static/index.html` (show score, highlight matched terms, citation chips, skeletons, honest copy).

## 5. Hour 3 — Ship + harden
- **T3.1**: Gate semantic eval into CI as network-skippable job (fake eval stays always-on).
- **T3.2**: Crawl robustness (skip non-HTML, dedupe canonical, honor noindex, timeout+retry, tests).
- **T3.3**: Honest README with 'Live demo in 60s', MRR comparison table, fix the false React claim, add demo screenshot.

## 6. Feasibility flags

| Flag | Status |
| :--- | :--- |
| Local MiniLM+cross-encoder | **Feasible** |
| Real OpenAI/Anthropic answers | **NOT feasible** (no keys) |
| React rebuild | **De-prioritized** (vanilla-JS UI polish preferred) |
