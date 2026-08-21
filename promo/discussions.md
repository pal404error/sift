# Community Discussion Seeds (honest, ready to post)

> GitHub Discussions are genuine community infrastructure — not engagement bait. Post these
> from the repo's Discussions tab. Each is a real question we actually want answered. No
> vote-manipulation, no "we're trending" framing. Adapt wording to your voice.

---

## 1. Poll — Which embedding model should we benchmark next?

We verify retrieval on `tests/gold/eval_gold_semantic.json` (recall@5 0.31→0.81 vs the old
default). The next lever is comparing embedding models head-to-head on that set.

Which model should we add to the benchmark first?
- sentence-transformers/all-MiniLM-L6-v2 (current default)
- sentence-transformers/multi-qa-mpnet-base-dot-v1
- BGE / E5 / GTE family
- A local-only small model you rely on in production

Vote, and drop a link if you have a gold set we should steal.

## 2. Open question — What's the hardest retrieval case you've hit in production RAG?

We built hybrid (lexical + vector via RRF) + HyDE because single-method retrieval misses
either paraphrases or exact tokens. But real queries are weirder.

What retrieval failure has cost you the most? (Multi-hop? code/IDs? multilingual? near-duplicate
docs?) Concrete examples beat opinions — they tell us where to point the next eval.

## 3. Debate — RRF vs weighted fusion: when have you needed weighted?

Our default is Reciprocal Rank Fusion (rank-only, no tuning). `SIFT_HYBRID_MODE=weighted` exists
for teams that have an eval set to tune `alpha` against. The research says RRF-first, graduate
later — but we'd like field data.

If you switched from RRF to a weighted/learned fusion, what forced your hand? If RRF has been
enough, say so — that's useful too.

---

*Guideline for replies: cite a reproducible case where you can. We'll fold good answers into
`ROADMAP.md` and the benchmark. No fabricated examples.*
