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

Run migrations and seed the first agent-readable knowledge pages:

```bash
docker compose run --rm app uv run experiment-os db migrate
docker compose run --rm app uv run experiment-os db seed
```

Run the v0 protocol smoke demo:

```bash
docker compose run --rm app uv run experiment-os demo smoke
```

Run a deterministic experiment fixture:

```bash
docker compose run --rm app uv run experiment-os experiments run-drizzle-fixture
```

Run a shell-command agent condition and capture transcript artifacts:

```bash
docker compose run --rm app uv run experiment-os experiments run-shell \
  --condition-id condition.001-drizzle-brief-assisted \
  --command "echo drizzle-orm@1.0.0-beta.22 && echo 'rg migration drizzle/migrations' && echo 'npm run db:generate passed'" \
  --workdir /workspace
```

Search local knowledge with full-text + pgvector retrieval:

```bash
docker compose run --rm app uv run experiment-os knowledge search "drizzle migration default"
```

Ingest GitHub issues as source snapshots and agent-readable source pages:

```bash
docker compose run --rm app uv run experiment-os issues ingest \
  --repo drizzle-team/drizzle-orm \
  --query "migration default" \
  --limit 3
```

Run the MCP server over stdio:

```bash
docker compose run --rm app uv run experiment-os mcp serve
```

Run the MCP server over streamable HTTP:

```bash
docker compose run --rm app uv run experiment-os mcp serve --transport streamable-http
```

On machines where Docker port publishing works normally, the same check can also run from the host:

```bash
uv run experiment-os db check
```

## Code Layout

The v0 backend is split by responsibility:

- `src/experiment_os/db/` - SQLAlchemy ORM models.
- `src/experiment_os/domain/` - Pydantic input/output schemas.
- `src/experiment_os/repositories/` - database access.
- `src/experiment_os/retrieval/` - full-text + pgvector retrieval.
- `src/experiment_os/services/` - application use cases.
- `src/experiment_os/mcp_server/` - MCP transport adapter.
- `src/experiment_os/cli.py` - developer CLI only.

The MCP tools and CLI commands share the same service layer.
