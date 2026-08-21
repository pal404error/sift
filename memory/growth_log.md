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
