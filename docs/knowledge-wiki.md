# Knowledge Wiki Model

## Product Idea

The human-facing presentation should feel like a wiki of experimental knowledge, not a log dashboard.

Agents should also consume this wiki structure through MCP. The important design point is that knowledge pages can explicitly depend on other knowledge pages.

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

## Presentation

The UI should present knowledge at three levels:

1. **Wiki page**: readable human explanation.
2. **Machine metadata**: typed front matter for retrieval and MCP.
3. **Dependency graph**: what must be loaded to understand or safely apply the page.

This gives us a product surface that is much stronger than a log table:

- humans curate pages,
- agents consume pages,
- policies are explainable because their dependency chain is visible.

