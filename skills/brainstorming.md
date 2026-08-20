---
name: brainstorming
description: Clarify intent before building. Ask "why", explore alternatives, surface constraints.
trigger: New feature, ambiguous request, or before any non-trivial build.
discipline: NEVER skip. Build the right thing before building it fast.
---

# Brainstorming

Goal: convert a vague idea into a crisp, scoped, justified plan.

## Process
1. **Restate the problem** in one sentence. Confirm you understood.
2. **Ask "why"** (5-whys lite): what outcome does this enable? What happens if we don't?
3. **Constraints & scope:** users, data sources, latency, cost, compliance, deployment.
4. **Alternatives:** list 2–3 approaches with trade-offs. Recommend one.
5. **Success criteria:** define measurable done (latency p95, recall@k, test pass, etc.).
6. **Risks:** what could go wrong; what's the cheapest way to de-risk (spike)?

## Output
A short brief: Problem / Why / Options / Recommendation / Success / Risks.
Hand off to `planning` to turn the brief into a step-by-step PLAN.

## Guardrails
- Do not write feature code during brainstorming.
- If the user's ask conflicts with RULES (RTK.md), flag it.
- Capture answers in `memory/user-preferences.md` and `memory/open-threads.md`.
