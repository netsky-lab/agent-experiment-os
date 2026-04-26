# Roadmap

## Phase 0: Research Repo

Status: in progress.

Artifacts:

- paper corpus,
- deep research,
- architecture docs,
- wiki/dependency model,
- MCP dependency flow.

## Phase 1: Protocol Prototype

Goal: prove the MCP work-brief loop.

Build:

- Postgres + pgvector schema,
- MCP server,
- seeded wiki pages,
- `get_work_brief`,
- `resolve_dependencies`,
- run event recording,
- markdown/JSON run reports.

Success criterion:

An agent can call MCP, receive required wiki pages, resolve dependencies, do work, and write back a run report.

## Phase 2: Issue Knowledge Ingestion

Goal: turn GitHub issues into source-backed knowledge cards.

Build:

- GitHub issue fetcher,
- source snapshot storage,
- claim extraction,
- issue clustering,
- version/status extraction,
- reviewable knowledge cards.

Success criterion:

A brief for a library-related task includes relevant issue-derived claims with source links and confidence.

## Phase 3: Failure and Intervention Loop

Goal: turn agent runs into reusable policies.

Build:

- failure taxonomy,
- failure annotation UI,
- intervention records,
- policy proposal flow,
- policy review queue.

Success criterion:

A repeated task family shows fewer repeated failures after approved policies enter briefs.

## Phase 4: Product UI

Goal: present the knowledge system clearly.

Build:

- wiki page browser,
- dependency graph,
- agent brief preview,
- knowledge cards,
- failure atlas,
- intervention library,
- policy review queue.

Success criterion:

A human can inspect why a brief contains a recommendation and trace it back to sources, runs, failures, and interventions.

