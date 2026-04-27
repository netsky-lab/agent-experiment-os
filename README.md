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
- [Codex MCP contract](./docs/codex-mcp.md)
- [Backend API contract](./docs/backend-api-contract.md)
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

Run a Codex CLI condition through `codex exec`:

```bash
docker compose run --rm app uv run experiment-os experiments run-codex \
  --condition-id condition.001-drizzle-brief-assisted \
  --prompt "Fix the Drizzle migration default-value issue with minimal changes." \
  --workdir /workspace \
  --sandbox workspace-write \
  --approval-policy never
```

Run Codex against the disposable Drizzle toy fixture:

```bash
docker compose run --rm app uv run experiment-os experiments run-codex-toy \
  --condition-id condition.001-drizzle-brief-assisted \
  --sandbox workspace-write \
  --approval-policy never
```

The fixture is copied from `fixtures/drizzle-toy-repo` into ignored `artifacts/workdirs/...`
before execution, and the run writes transcript/report artifacts under `artifacts/<run-id>/`.

Run baseline vs brief-assisted Codex conditions:

```bash
docker compose run --rm app uv run experiment-os experiments run-codex-toy-comparison
```

Run the version-trap fixture where issue evidence conflicts with local package versions:

```bash
docker compose run --rm app uv run experiment-os experiments run-codex-version-trap
```

Run baseline vs brief-assisted Codex conditions on the version-trap fixture:

```bash
docker compose run --rm app uv run experiment-os experiments run-codex-version-trap-comparison
```

Run Codex with Experiment OS mounted as an MCP server for the task:

```bash
docker compose run --rm app uv run experiment-os experiments run-codex-mcp-version-trap
```

Run a repeated baseline/static-brief/MCP-brief matrix:

```bash
docker compose run --rm app uv run experiment-os experiments run-codex-version-trap-matrix \
  --repeat-count 3 \
  --sandbox danger-full-access
```

Register Experiment OS as a Codex MCP server:

```bash
codex mcp add experiment-os -- docker compose run --rm app uv run experiment-os mcp serve
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

Run the dashboard/backend HTTP API:

```bash
docker compose run --rm --service-ports app uv run experiment-os api serve --host 0.0.0.0 --port 8080
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
