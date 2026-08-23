# Retrieval Research Notes — Sift

> Grounded research on production RAG retrieval best practices (2026), mapped to what Sift
> actually implements. Sources are real, dated 2026 industry write-ups (Canonical, InfoQ,
> SurePrompts, Sesame Disk, Redis). No numbers here are fabricated; where a claim is an
> industry observation rather than our own measurement, it is labeled as such.

## 1. The consensus architecture (2026)
Multiple independent 2026 sources converge on the same production pattern:

1. **Hybrid retrieval** — run lexical (BM25/sparse) and dense-vector search in parallel and
   fuse the ranked lists. Vector search captures *meaning* (paraphrases, synonyms); BM25
   captures *exact matches* (product codes, error codes, version strings, rare terms) that
   dense vectors smear. Most real queries need both.
2. **Reciprocal Rank Fusion (RRF)** — fuse on *rank position*, not raw scores. Raw BM25
   (unbounded) and cosine similarity ([-1,1]) are not comparable; summing them silently
   lets BM25 dominate. RRF (`score += 1/(k + rank)`, **k=60** default) needs no score
   normalization and is the safe, robust default. (Canonical; InfoQ; Redis; Sesame Disk.)
3. **Cross-encoder reranking** — after fusion casts a wide net (top ~20–100), a cross-encoder
   re-scores only those candidates for a final precision boost. This is exactly Sift's
   `CrossEncoderReranker`. (InfoQ; SurePrompts.)

> "If you are running a RAG pipeline on embeddings alone, you are leaving retrieval quality on
> the table. Add BM25, fuse with RRF, and consider a cross-encoder re-ranking stage." — InfoQ (2026)

## 2. How Sift maps to the pattern
| Best-practice component | Sift implementation | Status |
| --- | --- | --- |
| Lexical retriever (BM25-lite) | `llm_search/lexical_index.py` (inverted index, IDF + TF saturation) |  shipped (ADR-019) |
| Dense vector retriever | pluggable `EmbeddingProvider` (local MiniLM, OpenAI, Ollama) |  shipped |
| RRF fusion, k=60 | `SearchEngine.search` when `SIFT_HYBRID=true` |  shipped (default off) |
| Cross-encoder reranker | `llm_search/rerank.py::CrossEncoderReranker` |  shipped |
| HyDE query expansion | `SearchEngine.ask(use_hyde=True)` |  shipped (ADR-020) |

This means Sift is architecturally aligned with the documented 2026 production standard,
not a naive single-method retriever.

## 3. Evaluation discipline (what the research insists on)
- **Build a golden set** of 50–500 real queries with labeled relevant docs; version it with
  code. Sift ships `tests/gold/eval_gold_semantic.json` (paraphrases/synonyms/multi-hop).
- **Measure the right metrics.** Recall@k (did a relevant doc make the top-k?), MRR, and
  **nDCG@10** (graded relevance, position-discounted). Sift's `run_eval.py` reports
  recall@k / precision@k / **ndcg@k** / MRR. (Sesame Disk; SurePrompts.)
- **Reproduce, don't claim.** Our headline numbers (recall@5 0.31→0.81, MRR 0.12→0.59 on the
  semantic gold set) are produced by `python scripts/run_eval.py --gold tests/gold/eval_gold_semantic.json --compare` and published raw in `data/retrieval_benchmark.csv`.

## 4. Honest gaps & roadmap (per the research)
The same sources note these as the *next* steps beyond RRF — logged honestly, not claimed:
- **Weighted fusion / query-style routing**: SHIPPED (off by default). `SIFT_HYBRID_MODE=weighted`
  with `SIFT_HYBRID_ALPHA`, plus `SIFT_HYBRID_ROUTE` (biases toward lexical for exact-match queries
  via `SearchEngine._routed_alpha`). See `llm_search/engine.py` and CHANGELOG ADR-022/023.
- **Full BM25** vs our BM25-*lite*: we use IDF + TF saturation without full length-norm tuning.
  Adequate for fusion; could be upgraded.
- **Bigger / out-of-domain gold sets**: our semantic set is small; expanding it strengthens
  the eval (and would let us tune `rrf_k` per corpus, though research says k=60 is robust).

## 5. Sources
- Canonical — "Hybrid search and reranking: a deeper look at RAG" (2026-04)
- InfoQ — "Why Vector Search Alone Isn't Enough: Hybrid Retrieval for RAG" (2026-06)
- SurePrompts — "Hybrid Search: Combining BM25 and Vector Retrieval" (2026-04)
- Sesame Disk — "Hybrid Search Fusion Strategies in 2026" (2026-07)
- Redis — "Reciprocal Rank Fusion" (2026-08)
