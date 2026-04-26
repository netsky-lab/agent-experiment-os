# Architecture

## Storage Stance

SQLite is acceptable only for tiny local demos and unit tests. It should not be the primary design target.

The product needs semantic retrieval, full-text retrieval, typed relationships, provenance, and auditable policy promotion. The baseline storage should be:

```text
Postgres
-> canonical entities, relationships, audit log
-> tsvector/BM25-style full-text search
-> pgvector embeddings for semantic candidate recall
-> JSONB for event payloads and source metadata
```

This keeps the first implementation simple while avoiding a dead-end architecture.

## Why Not Vector-Only

The system cannot be "just embeddings" because the important objects are typed and evidence-backed:

- source snapshots,
- issue claims,
- knowledge cards,
- runs,
- failures,
- interventions,
- policies,
- policy dependency edges,
- review decisions,
- counterexamples.

Semantic search should retrieve candidates. It should not decide policy applicability by itself.

## Retrieval Model

Use hybrid retrieval:

```text
1. Structured filters:
   repo_type, language, framework, library, version, agent, model, toolchain, task_family

2. Full-text search:
   issue titles, issue bodies, docs snippets, failure summaries, policy text

3. Semantic search:
   embeddings over claims, knowledge cards, run summaries, policy rationales

4. Graph expansion:
   dependsOn, contradicts, supersedes, validates, mitigates

5. Ranking:
   applicability, confidence, source quality, recency, severity, evidence count, counterexamples
```

The brief compiler receives ranked candidates and emits a compact work brief.

## Core Components

```text
MCP server
  agent-facing tools, prompts, resources

HTTP API
  UI, integrations, webhooks, batch ingestion

Workers
  GitHub issue ingestion, docs ingestion, claim extraction, embedding, clustering, diagnosis

Postgres + pgvector
  canonical source of truth, search, embeddings, graph edges

UI
  wiki, brief preview, knowledge cards, failure atlas, policy review
```

## First Implementation Stack

Recommended first stack:

- Python
- FastMCP or official MCP Python SDK
- FastAPI for HTTP/UI API
- Postgres 16 + pgvector
- SQLAlchemy + Alembic
- Pydantic for schemas
- `uv` for project management
- simple server-rendered UI or Next.js later

Local dev should use Docker Compose for Postgres. SQLite can exist only as an optional test fixture.

