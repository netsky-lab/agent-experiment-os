# Experiment OS

MCP-native experiment knowledge system for coding agents.

This is not a generic agent memory product and not another eval dashboard. The project studies how to turn coding-agent work into reusable experimental knowledge:

```text
issues/docs/runs
-> source-backed claims
-> failure diagnosis
-> interventions
-> reviewed policies
-> MCP work brief
-> better next run
```

The main agent-facing artifact is a **work brief**: a compact, source-backed packet of known risks, dependency-specific issue knowledge, prior failures, and approved interventions that an agent should read before editing code.

## Research Corpus

- [Deep research](./research/deep-research.md)
- [Paper corpus](./research/papers/README.md)

## Design Docs

- [Architecture](./docs/architecture.md)
- [Knowledge wiki model](./docs/knowledge-wiki.md)
- [MCP dependency flow](./docs/mcp-dependency-flow.md)
- [Roadmap](./docs/roadmap.md)

## Local Development

Start Postgres with pgvector:

```bash
docker compose up -d postgres
```

Check the database connection from the Docker network:

```bash
docker compose run --rm app uv run experiment-os db check
```

On machines where Docker port publishing works normally, the same check can also run from the host:

```bash
uv run experiment-os db check
```
