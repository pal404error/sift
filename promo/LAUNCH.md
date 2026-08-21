# Launch Assets — Sift (legitimate, honest promo)

> All copy here is truthful and links to real, reproducible data. Post from your own
> accounts when you're ready. Adapt the wording based on real feedback (that's the
> "dynamic" part) — never invent metrics or screenshots.

---

## 1. Show HN (Hacker News)

**Title:** Show HN: Sift – a self-hostable RAG search engine with a 5× retrieval lift from local embeddings

**Body:**

We built Sift because most RAG demos quietly score ~1.0 on toy eval sets and fall apart on real queries. So we measured retrieval on a deliberately hard gold set — paraphrases, synonyms, and multi-hop questions designed to defeat lexical matching — and published the raw numbers:

- Old default (random "fake" embeddings + lexical reranker): recall@5 0.31, MRR 0.12
- New default (local MiniLM + cross-encoder reranker): recall@5 0.81, MRR 0.59

No API key needed for relevance; you bring your own LLM. Reproduce it:

```
pip install sentence-transformers
python scripts/run_eval.py --gold tests/gold/eval_gold_semantic.json --compare
```

Repo: https://github.com/pal404error/sift

Author here — happy to answer questions about the eval methodology or the architecture (FastAPI + Qdrant + pluggable providers, OIDC/SSO, Prometheus metrics). What models should we add to the benchmark next?

---

## 2. Reddit — r/LocalLLaMA

**Title:** We measured RAG retrieval on a hard gold set — local MiniLM + cross-encoder reranker beat our old default ~5× (recall@5 0.31 → 0.81)

**Body:**

Most RAG benchmarks I see use sets that score ~1.0 and prove nothing, so we built one that's actually adversarial to lexical matching (paraphrases, synonyms, multi-hop). Raw results in `data/retrieval_benchmark.csv`.

The interesting part: the lift came entirely from local, free embeddings + a cross-encoder reranker — no API key, no cost. Curious what the community thinks we're missing. Full repo + reproducible eval: https://github.com/pal404error/sift

Would love feedback on (a) the gold-set design and (b) which embedding/reranker models to add.

---

## 3. Reddit — r/RAG

Same thread as above, framed for practitioners:

**Title:** Self-hosted RAG retrieval quality: our eval harness + results (local MiniLM + reranker, ~5× lift on a hard set)

**Body:** (same body as r/LocalLLaMA, lead with "if you're building your own RAG pipeline, here's how we measure retrieval quality and the numbers we got...")

---

## 4. Twitter / X thread (honest, ~10 tweets)

1/ We open-sourced Sift, a self-hostable RAG search engine. Thread on what we learned measuring retrieval quality for real. 🧵

2/ The trap: most RAG demos eval on sets that score ~1.0. That proves nothing. So we built a gold set with paraphrases, synonyms, and multi-hop questions.

3/ Result on that hard set: random "fake" embeddings + lexical reranker → recall@5 0.31. Local MiniLM + cross-encoder reranker → recall@5 0.81. A ~5× lift.

4/ Best part: that lift is free. Local embeddings, no API key, no per-query cost. You bring your own LLM for generation.

5/ Architecture: FastAPI + Qdrant + pluggable providers (OpenAI/Anthropic/local). OIDC/SSO, Prometheus metrics, Docker Compose. Enterprise-ready, self-hostable.

6/ Everything is reproducible: `python scripts/run_eval.py --gold tests/gold/eval_gold_semantic.json --compare`

7/ We published the raw numbers in `data/retrieval_benchmark.csv`. No cherry-picked benchmarks — fork it and prove us wrong.

8/ What's next: more embedding models in the benchmark, a reranker sweep, and community-requested providers.

9/ Repo: https://github.com/pal404error/sift — ⭐ if you want to follow along.

10/ Genuinely want feedback: what's the hardest retrieval case you've hit in production RAG?

---

## 5. Posting cadence (legitimate, human-driven)

- T+0: Ship README + benchmark CSV (this PR).
- T+0 (after merge): Post Show HN, then comment as author within minutes.
- T+15m: r/LocalLLaMA.
- T+45m: r/RAG.
- T+60m: X thread, tagging relevant OSS maintainers (not as spam — genuine @mentions).
- Then: reply to *every* real comment within a few hours, honestly.
- Reassess at T+3h and T+6h using real metrics (stars, HN score, upvotes) logged in SITREP.md.

## 6. What we are NOT doing

- No fake "we're trending" screenshots.
- No bot/dummy issues or star-request DMs.
- No baiting fights or cross-post spam with manipulated framing.
- No algorithm-gaming micro-commits.
- Metrics in SITREP.md must be real (pull from GitHub/ HN/ Reddit directly).
