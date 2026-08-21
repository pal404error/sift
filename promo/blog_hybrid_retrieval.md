# Hybrid retrieval is the architecturally correct choice for RAG — and we measured it

*Technical deep-dive for `promo/` — ready to post as a blog post or long-form Show HN comment.
Every number here is reproducible from the repo; nothing is rounded up for effect.*

## The trap most RAG demos fall into

A lot of RAG "looks amazing" because it's evaluated on a gold set that scores ~1.0 — queries
that share vocabulary with the documents they should retrieve. That proves the plumbing works,
not that retrieval is good. The moment a real user asks a question that *paraphrases* the source
or contains a *rare exact token* (an error code, a version string, a product ID), single-method
retrieval falls apart.

We built [Sift](https://github.com/pal404error/sift) to not have that problem, and we measured
it on a deliberately adversarial gold set (`tests/gold/eval_gold_semantic.json`): paraphrases,
synonyms, and multi-hop questions designed to defeat lexical token matching.

## What "hybrid" actually means

Two retrievers with complementary strengths:

- **Dense vector search** captures *meaning*. "sunny weather" can match "clear blue skies"
  with zero word overlap.
- **Lexical (BM25-style) search** captures *exact matches* — the rare tokens dense vectors
  smear. For "Outlook 2019 sync error 0x80004005", you need both the semantic intent and the
  literal `0x80004005`.

We fuse the two ranked lists with **Reciprocal Rank Fusion** (`score += 1/(k + rank)`, `k=60`):
it operates on *rank position*, not raw scores, so it needs no score normalization and is
robust by default. This matches the 2026 production-RAG consensus documented by Canonical,
InfoQ, Redis, and others (see `research/RETRIEVAL_NOTES.md`).

## The numbers (reproducible)

```
pip install -e ".[semantic]"
python scripts/run_eval.py --gold tests/gold/eval_gold_semantic.json --compare
```

| Pipeline | recall@5 | precision@5 | ndcg@5 | MRR |
| --- | --- | --- | --- | --- |
| fake embeddings + lexical reranker (old default) | 0.31 | 0.06 | 0.17 | 0.12 |
| local MiniLM + cross-encoder reranker | 0.81 | 0.16 | 0.65 | 0.59 |

That's a **2.6× lift in recall@5** and a **4.8× lift in MRR** — on the *hard* set. (On the
trivial embedded demo set, both score ~1.0, which is why we don't brag about that one.) All
numbers are in `data/retrieval_benchmark.csv`; fork the repo and prove us wrong.

## It composes

Hybrid retrieval isn't the end — it's the substrate:

- **HyDE** (`ask(use_hyde=True)`): rewrite the query into a hypothetical answer passage, then
  embed *that*, improving the semantic match for short questions.
- **Cross-encoder reranker**: re-scores the fused candidate set for final precision.
- **Streaming** (`GET /ask/stream`, SSE): answers arrive token-by-token for a live demo feel.

None of these require an API key for *relevance* — embeddings and the reranker run locally.
You bring your own LLM for generation.

## Honest gaps

We use a BM25-*lite* (IDF + TF saturation, no full length-norm tuning) and our semantic gold
set is small. Both are roadmap items, not hidden flaws. The architecture is the point: hybrid +
RRF + rerank is the right shape, and it's all measurable.

If you care about retrieval quality, clone it, run the eval, and tell us where our gold set is
too easy. That's the kind of contribution that actually moves the number.
