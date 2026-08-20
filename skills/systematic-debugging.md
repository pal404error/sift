---
name: systematic-debugging
description: Evidence-based debugging. Never guess; form hypotheses, test, isolate.
trigger: A bug, test failure, or unexpected behavior.
discipline: NEVER guess-and-patch. One hypothesis at a time, verified.
---

# Systematic Debugging

Goal: find the root cause with proof, not luck.

## Process
1. **Reproduce** deterministically. Capture the exact input, env, and command.
2. **Observe** real state: logs, stack traces, values, status codes. No assumptions.
3. **Form a ranked hypothesis list.** Write them down; pick the most likely.
4. **Test each hypothesis** with minimal instrumentation (print/debugger/assert).
   - Binary search the problem space (disable halves, narrow inputs).
5. **Isolate** the minimal failing case.
6. **Fix at the root**, not the symptom. Add a regression test that fails pre-fix.
7. **Verify**: run the test suite + the reproduction; show green output.

## Anti-patterns (forbidden)
- "Probably the cache." → prove it.
- Editing randomly until it works.
- Fixing the symptom (swallowing the error) without understanding.

## Evidence log
Note in `memory/open-threads.md` if unresolved; record root cause in `memory/decisions.log`.
