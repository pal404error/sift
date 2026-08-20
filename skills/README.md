# Skills Index

Modular capability packs. Invoke a skill only when its task matches; never skip its
discipline. Each pack lives in `skills/<name>.md` with a YAML frontmatter `name`/`description`/`trigger`/`discipline`.

| Skill | Invoke when | File |
|-------|-------------|------|
| brainstorming | Clarifying intent/scope before building | [brainstorming.md](brainstorming.md) |
| planning | Breaking work into verified phases (post-brainstorm) | [planning.md](planning.md) |
| test-driven-development | Implementing core logic (retrieval/ranking/chunking) | [test-driven-development.md](test-driven-development.md) |
| systematic-debugging | Any bug/test failure/unexpected behavior | [systematic-debugging.md](systematic-debugging.md) |
| security-review | Pre-merge, new endpoints/deps, after ingestion | [security-review.md](security-review.md) |
| diagram-generation | Documenting architecture/sequence/ER designs | [diagram-generation.md](diagram-generation.md) |

## Ritual (per feature/fix)
1. **brainstorming** → intent brief
2. **planning** → PLAN with success criteria
3. **test-driven-development** (core) / **systematic-debugging** (if blocked)
4. **security-review** before merge
5. **diagram-generation** to document design
6. Update `memory/knowledge-graph.json`, `decisions.log`, `open-threads.md`, `RTK.md`.
