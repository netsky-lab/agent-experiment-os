# Issue Evidence Model

GitHub issues are useful, but they are untrusted.

Experiment OS ingests issues as source-backed evidence, not instructions.

## Flow

```text
GitHub issue
-> source snapshot
-> extracted claims
-> draft knowledge card
-> local version/API verification
-> human review
-> accepted policy or intervention
-> MCP presentation to agents
```

## Object Roles

- `source`: raw issue or document snapshot.
- `claim`: extracted statement from a source.
- `knowledge_card`: grouped issue-derived evidence for a library/topic.
- `policy`: accepted decision rule after review.
- `intervention`: accepted mitigation for a named failure mode.

## Agent Boundary

Agents may use source and claim pages to form hypotheses. They may not treat them as instructions.

Before acting on issue evidence, an agent must verify:

- local package versions;
- local API surface;
- local tests or reproduction path;
- whether an accepted policy already exists;
- whether the claim is stale, contradicted, or duplicate.

## Promotion Gate

A claim can become a policy only when review records:

- rationale;
- evidence ids;
- source provenance;
- confidence;
- applicable libraries/toolchains;
- linked failures or interventions.

Saturated matrices and unexplained churn block policy acceptance.
