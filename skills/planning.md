---
name: planning
description: Break work into phases with verification checkpoints and goal-backward success.
trigger: After brainstorming, before executing any multi-step feature or fix.
discipline: Define success criteria FIRST, then plan the path to it.
---

# Planning

Goal: a step-by-step PLAN where each step has a verifiable output.

## Template (write to PLAN.md or TODO.md)
```
## Goal
<one sentence>

## Success criteria (verify before claiming done)
- [ ] lint 0/0
- [ ] typecheck pass
- [ ] tests pass (unit + integration)
- [ ] build (dev + prod)
- [ ] security-review pass
- [ ] docs updated

## Phases (atomic, verifiable)
1. <step> | verify: <command/output>
2. <step> | verify: <command/output>
...

## Risks / open questions
- ...
```

## Rules
- **One in_progress item at a time** (TODO.md discipline).
- Each step ends with a command you actually run and show.
- Phases map to Conventional Commit units.
- If a step can't be verified, it's not done.

## Then
Hand to `test-driven-development` (for core logic) and `systematic-debugging` (if blocked).
Update `memory/knowledge-graph.json` and `memory/decisions.log` as you go.
