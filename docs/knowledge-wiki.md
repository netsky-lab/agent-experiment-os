# Knowledge Wiki Model

## Product Idea

The primary presentation target is the agent, not the human.

Humans may see dashboards, tables, charts, and review queues. Those are UI projections over the same data. The canonical representation should be an agent-readable wiki graph exposed through MCP: typed pages, compact summaries, applicability metadata, confidence, source provenance, and explicit dependency edges.

The important design point is that knowledge pages can explicitly depend on other knowledge pages, and agents can resolve those dependencies before work.

## Page Types

Initial page types:

- `source`: raw GitHub issue, PR, docs page, run trace, test output
- `claim`: extracted assertion from a source
- `knowledge_card`: curated issue/docs/run learning
- `failure`: failure mode with examples and evidence
- `intervention`: reusable mitigation
- `policy`: reviewed rule that can be inserted into future work briefs
- `experiment`: hypothesis and test design
- `run_report`: one execution and its interpretation

## Page Front Matter

Every wiki page should have machine-readable metadata.

```yaml
id: policy.opencode-gemma-shell-escaping
type: policy
title: Use narrow shell commands for OpenCode + Gemma
status: accepted
confidence: medium
dependsOn:
  - failure.tool-call-syntax-drift
  - failure.shell-escaping
  - intervention.command-normalization
  - run.2026-04-26-gemma-python-cli-001
contradicts: []
supersedes: []
validatedBy:
  - run.2026-04-26-gemma-python-cli-002
appliesTo:
  repo_type: python_cli
  agent: opencode
  model: gemma
  toolchain: shell
review:
  reviewer: human
  reviewed_at: 2026-04-26
```

Body:

```md
# Use narrow shell commands for OpenCode + Gemma

## Rule

When OpenCode + Gemma works in Python CLI repos, prefer single-purpose shell commands and validate tool-call JSON before execution.

## Rationale

Prior runs show invalid shell escaping and JSON drift under compound shell commands.

## Evidence

- run.2026-04-26-gemma-python-cli-001
- failure.tool-call-syntax-drift

## Counterexamples

None yet.
```

## `dependsOn`

`dependsOn` is not just UI decoration. It is part of the retrieval and briefing contract.

Meaning:

```text
This page should not be interpreted alone.
To use it safely, also load or summarize these dependency pages.
```

Examples:

- A policy depends on the failure it mitigates.
- An intervention depends on failure examples and run reports.
- A knowledge card depends on source issues and version notes.
- A run report depends on experiment design and trace evidence.
- A work brief depends on selected policies and knowledge cards.

## Graph Edges

Minimum edge types:

- `dependsOn`
- `contradicts`
- `supersedes`
- `validates`
- `mitigates`
- `observedIn`
- `derivedFrom`
- `appliesTo`

The UI should render this as a navigable graph and as dependency breadcrumbs.

## Agent-First Presentation

The canonical presentation should be optimized for agents:

- compact summary,
- typed metadata,
- applicability conditions,
- confidence,
- source provenance,
- dependency closure,
- counterexamples,
- token budget aware rendering.

The human UI can present the same objects as a dashboard, wiki, graph, table, or review queue. That UI is secondary to the MCP contract.

The core product surface is:

- agents consume pages,
- agents resolve dependencies,
- agents know which policies apply,
- agents can trace recommendations back to evidence,
- humans curate and review the objects that agents will consume.
