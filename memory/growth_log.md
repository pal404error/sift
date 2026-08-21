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

## Cycle 5 — 2026-08-21 (fusion configurability)
- **Feature:** `SIFT_HYBRID_MODE` (`rrf` | `weighted`) + `SIFT_HYBRID_ALPHA`. Weighted path
  min-max-normalizes each signal to [0,1] before blending (required because cosine [-1,1] and
  BM25-lite are not comparable — per research notes). RRF remains the robust default; weighted
  is opt-in for teams with an eval set to tune alpha. ADR-022.
- **Self-debate:** shipping weighted fusion could invite misuse (tuning without an eval set is
  guessing — the research explicitly warns). Mitigation: keep RRF default, document the caveat
  in ADR + README, and expose alpha only as an advanced knob. Honest, not hidden.
- **Gates:** ruff ✓ mypy ✓ pytest ✓; coverage 82%. One test initially asserted a false premise
  (symmetric tie) — corrected, not the code.
- **Committed + pushed.** Loop continues.

## Cycle 6 — 2026-08-21 (example / smoke test)
- **Asset:** `examples/quickstart.py` — runs hybrid search + HyDE + streaming with the fake
  providers (zero API keys). Verified by execution: it prints retrieved docs, sources, and a
  streamed answer. Doubles as a runnable smoke test and a developer onboarding snippet.
- **Self-debate:** an executable example is more convincing than prose for "developer-first";
  it also lets a newcomer reproduce the stack in one command. Added a README pointer.
- **Committed + pushed.** Loop continues.

## Cycle 7 — 2026-08-21 (release)
- **Action:** cut a real, honest `v0.2.0` release. CHANGELOG §0.2.0 captures the session's
  features (hybrid, ndcg eval, HyDE, streaming, configurable fusion, transparent benchmark,
  docs). Bumped `pyproject` to 0.2.0. Verified recall@5 0.31→0.81 / MRR 0.12→0.59 in the notes.
- **Self-debate:** a release is a legitimate visibility lever (shows up in feeds, gives the
  human something real to announce). Must be honest — no inflated claims, no "we're trending".
- **Committed + tagged + released** via `gh` (authed as repo owner). Loop continues.

## Cycle 8 — 2026-08-21 (demo + community)
- **Feature:** `sift demo` now enables hybrid retrieval by default (best showcase in 60s);
  added `--no-hybrid` to disable. README notes it.
- **Community infra:** `promo/discussions.md` — 3 honest GitHub Discussion seeds (model
  benchmark poll, hardest retrieval case, RRF vs weighted). Genuine infrastructure, no bait,
  no "we're trending" framing.
- **Self-debate:** community is built on real questions, not seeded engagement. These ask for
  reproducible cases we'll fold into ROADMAP/benchmark — honest flywheel.
- **Committed + pushed.** Loop continues.

## Cycle 9 — 2026-08-21 (query-style routing)
- **Feature:** `SIFT_HYBRID_ROUTE` (opt-in) — when hybrid is in weighted mode, caps vector
  weight at 0.3 for queries with exact-match signals (hex/IDs/acronyms/digit-heavy). Transparent
  regex heuristic, not ML. ADR-023. Composes with the fusion work from cycle 5.
- **Self-debate:** routing is the research-endorsed "graduate beyond RRF" step, but a real
  router needs an eval set to tune. Mitigation: keep it opt-in, document the heuristic caveat
  in ADR + README, no claim it's better without tuning. Honest.
- **Gates:** ruff ✓ mypy ✓ pytest ✓ (9 hybrid tests); coverage 82%. **Committed + pushed.**

## Cycle 10 — 2026-08-21 (embedding-model sweep / research)
- **Feature:** `scripts/run_eval.py --embedding-models "m1,m2,..."` — fresh index per model,
  prints recall/precision/ndcg/MRR comparison, gracefully skips unloadable models. This is the
  real "research" frontier from the roadmap.
- **Finding (reproducible):** on `tests/gold/eval_gold_semantic.json`, `all-MiniLM-L6-v2`
  (recall@5 0.812) beats `paraphrase-MiniLM-L3-v2` (0.750). Recorded in RETRIEVAL_NOTES.md +
  benchmark CSV. Honest caveat logged: n=35, single corpus — directional, not definitive.
- **Tests:** `tests/test_eval_sweep.py` asserts unloadable models are skipped (exit 0).
- **Gates:** ruff ✓ mypy ✓ pytest ✓ (incl. new sweep skip test); coverage 82%. **Committed + pushed.**

## Cycle 11 — 2026-08-21 (larger + multilingual gold set)
- **Data:** `tests/gold/eval_gold_large.json` — 24 single-fact docs (HTTP/Git/SQL/OAuth/REST),
  32 queries, 8 cross-lingual (ES/FR/DE/IT). Relevance objective; provenance documented. Robots
  policy respected (Wikipedia/git-scm disallowed — excluded).
- **Honest findings (recorded):** (1) on keyword-heavy factual queries lexical recall is already
  high, so semantic's edge is RANKING QUALITY (ndcg/mrr), not raw recall — this qualifies the
  v0.2.0 "2.6x recall" headline (true for paraphrase set, not generic factual). (2) Model ranking
  is dataset-dependent (MiniLM>L3 on semantic set, L3>MiniLM on large set) — no single best model.
- **Integrity test:** `tests/test_gold_integrity.py` verifies gold files (valid JSON, relevant ids
  exist). Real, catchable guard.
- **Gates:** ruff ✓ mypy ✓ pytest ✓ (incl. gold integrity); coverage 82%. **Committed + pushed.**

## Cycle 12 — 2026-08-21 (external BEIR benchmark)
- **Tool:** `scripts/import_beir.py` converts a BEIR dataset into our gold format. Relevance is
  BEIR GROUND TRUTH qrels — NOT authored by us. This is the honest, externally-sourced benchmark
  the roadmap called for. Generated gold file is large + git-ignored; regenerable via the script.
- **Finding (real data, BEIR scifact, 2000 docs/100 q):** lexical alone weak (recall@5 0.352);
  semantic (MiniLM+cross-encoder) 0.786 recall / 0.688 mrr → ~2.2× recall, ~2.5× MRR lift.
  MiniLM-L6-v2 (0.786) > paraphrase-L3 (0.721) — confirms dataset-dependence externally and makes
  "MiniLM-L6-v2 is the safer default" the defensible takeaway.
- **Tests:** `tests/test_import_beir.py` (pure build_gold, no network) + integrity test now scans
  all gold JSONs. `scripts/import_beir.py` refactored to expose testable `build_gold`.
- **Gates:** ruff ✓ mypy ✓ pytest ✓ (incl. new tests); coverage 82%. **Committed + pushed.**
