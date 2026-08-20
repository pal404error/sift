---
name: diagram-generation
description: Produce architecture, sequence, or ER diagrams via Mermaid/PlantUML.
trigger: Documenting system design, data flow, API contracts, or DB schema.
discipline: A diagram is a verified artifact — it must match the code, not vibes.
---

# Diagram Generation

Goal: visual artifacts that reflect reality and live in `docs/`.

## Types & when
- **Architecture** (components + data flow): use at project start and after structural
  changes. Mermaid `flowchart` or `graph`.
- **Sequence** (request/retrieval flow): for RAG pipeline (query → retrieve → rerank →
  generate). Mermaid `sequenceDiagram`.
- **ER / schema** (DB + vector collections): Mermaid `erDiagram` or class diagram for
  Pydantic models.
- **State / decision**: Mermaid `stateDiagram` for ingestion jobs.

## Mermaid starter (RAG flow)
```mermaid
sequenceDiagram
  participant U as User
  participant API as FastAPI
  participant R as Retriever
  participant V as Qdrant
  participant LLM as LLM
  U->>API: query
  API->>R: embed+search
  R->>V: top-k vectors
  V-->>R: chunks
  R-->>API: context
  API->>LLM: prompt+context
  LLM-->>U: answer
```

## Discipline
- Generate, then cross-check node names against `memory/knowledge-graph.json`.
- Store diagrams in `docs/` (e.g. `docs/architecture.md`). Keep RTK.md diagrams in sync.
- Prefer Mermaid (GitHub-renderable) unless PlantUML is required by the team.
