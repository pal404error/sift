# User Preferences

Captured from interactions; tune the agent's behavior. Update when the user expresses a
preference (verbosity, testing depth, risk tolerance, tooling).

---

- **Verbosity:** User issued a very detailed meta-prompt → prefers thorough, structured,
  auditable output. Default to detailed but skimmable.
- **Testing level:** Prompt mandates TDD + quality gates → prefer high test coverage and
  red-green-refactor for core logic.
- **Risk tolerance:** Conservative — confirmation required before destructive ops; security
  by default; pin deps; audit on PRs.
- **Tooling preference:** Convention-following, deterministic tooling over black-box calls
  (per prompt §7). Prefer graphs, lint, typecheck, tests as evidence.
- **Communication:** Concise in chat; comprehensive in docs. Conventional Commits expected.
- **Unknown (ask):** Preferred LLM provider, deployment target, primary data sources.
- **RESOLVED (2026-08-20):** Enterprise self-host (docker-compose) with auth/compliance
  expected; multi-provider LLM (OpenAI/Anthropic/Ollama). Product = web search engine.
