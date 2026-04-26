# Experiment OS

This repo is a research workspace for an MCP-native experiment knowledge system for coding agents.

Primary research artifact:

- [`deep-research.md`](./deep-research.md)

Primary paper corpus:

- [`papers/`](./papers/)
- [`papers/README.md`](./papers/README.md)

Current thesis:

> The system should not be designed as a generic agent memory product or another eval dashboard. It should convert issue knowledge and agent run traces into failure-aware, intervention-backed work briefs delivered through MCP.

Core loop:

```text
issues/docs/runs
-> source-backed claims
-> failure diagnosis
-> interventions
-> reviewed policies
-> MCP work brief
-> better next run
```

