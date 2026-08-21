# Growth Log — Sift (living knowledge base)

> Stand-in for the NotebookLM decision log the marathon calls for. Honest, data-backed.
> Updated each execution cycle. All claims traceable to repo files or cited research.

## Cycle 0 — 2026-08-21 (marathon start)

### Self-debate: what actually drives organic GitHub growth for a dev tool?
- **Engineer:** Best lever is genuine capability + a demo that works in 60s. Trending repos
  win on "I can run this and it does something impressive immediately."
- **Marketer:** The hook must be a *provable* data point, not adjectives. We have one:
  recall@5 0.31 → 0.81 on a hard gold set (verified via `scripts/run_eval.py --compare`).
- **Skeptic:** "5× lift" is only impressive if the gold set is credible. Ours is adversarial
  (paraphrases/synonyms/multi-hop) — stronger than toy sets. Keep it honest; publish raw CSV.
- **Decision:** Lead with the verified benchmark, ship transparent data, never fabricate
  engagement. Ecosystem fit: Python+FastAPI matches 56% of top-50 trending RAG repos
  (see `trending-insights.md`).

### Research notes (grounded in `trending-insights.md`)
- Dominant stack: Python backend + TS frontend; pnpm/uv; ruff+black; GitHub Actions.
  Sift already matches this — good.
- Underused in domain: SAST/semgrep, explicit coverage gates. Sift already has both
  (coverage 80% gate, gitleaks in CI). Differentiation is real, lead with it.
- README pattern across winners: features → architecture → quickstart → API → deploy → roadmap.

### Next highest-leverage honest moves
1. HyDE query expansion (retrieval booster, cheap, plugs into engine).
2. Public ROADMAP.md (community infrastructure; honest).
3. README benchmark table (provable social proof).
4. Streaming answers (demo appeal) — later cycle.

## Cycle 1 — 2026-08-21
- **Self-debate resolved:** lead with verified benchmark (recall@5 0.31→0.81), never fabricate.
- **Shipped:** hybrid retrieval (RRF, k=60) — ADR-019; HyDE expansion — ADR-020; ndcg@k in eval.
- **Research:** web-grounded `research/RETRIEVAL_NOTES.md` confirms Sift's architecture matches
  the 2026 production consensus (BM25 + vector + RRF + cross-encoder rerank). Real differentiator.
- **Honesty fix:** corrected README hook from "5×" to exact "2.6× recall@5 / 4.8× MRR".
- **Public infra:** ROADMAP.md (shipped/in-progress/planned), growth_log (this file).
- **Committed:** baseline hybrid work + HyDE, both with clear messages.

## Cycle 2 — 2026-08-21 (streaming)
- **Feature:** Server-Sent-Events streaming answers. `LLMProvider.stream` (default yields full
  text; OpenAI/Anthropic true token streaming) → `SearchEngine.ask_stream` (sources event then
  token events) → `GET /ask/stream`. CLI `ask`/`search` gained `--hybrid`/`--hyde` flags.
- **Self-debate:** streaming is a UX/demo lever, not a relevance lever — pairs with the verified
  benchmark for the "impressive in 60s" hook. Keep it honest (no fake "thinking" tokens).
- **Gates:** ruff ✓ mypy ✓ pytest ✓; coverage 82% (>80%). mypy caught 2 real bugs pre-push
  (`cache_clear` is a function attr; Anthropic `stream()` rejects `temperature`).
- **Committed + pushed:** streaming feature + docs (ADR-021). Loop continues.

## Cycle 3 — 2026-08-21 (content)
- **Asset:** `promo/blog_hybrid_retrieval.md` — a publishable, honest technical deep-dive. Leads
  with the reproducible benchmark, explains hybrid+RRF+HyDE+streaming as a composable substrate,
  and explicitly states honest gaps (BM25-lite, small gold set). No hype rounding.
- **Self-debate:** blog must earn trust by showing the *trivial* set scores ~1.0 too (we did).
  Credibility > virality for organic growth.
- **Committed + pushed.** Ready for the human to post (blog + the Show HN/Reddit/X drafts in
  `promo/LAUNCH.md`). Loop continues.

## Cycle 4 — 2026-08-21 (demo UX)
- **Feature:** wired the static web UI "Ask" to `GET /ask/stream` — answers render
  token-by-token; sources appear on the first event. Added a HyDE checkbox (passes `hyde=1`).
- **Self-debate:** the 60s demo is the single biggest organic-growth lever (marathon Cycle 0
  insight). Streaming makes "it works, and fast" visceral. No fake progress UI.
- **Committed + pushed.** Loop continues — next candidate: weighted/query-style hybrid fusion
  (roadmap) or a multi-model benchmark sweep (needs model downloads).
