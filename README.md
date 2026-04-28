# Agent Experiment OS

MCP-native experiment knowledge system for coding agents.

This is not a generic agent memory product and not another eval dashboard. The project studies how to turn coding-agent work into reusable experimental knowledge:

```text
hypothesis
-> test design
-> agent run
-> observed failures
-> metric movement
-> interpretation
-> intervention
-> next experiment
-> accumulated policy
```

The main agent-facing artifact is a **work brief**: a compact, source-backed packet of known risks, dependency-specific issue knowledge, prior failures, and approved interventions that an agent should read before editing code.

The main research artifact is a **matrix report**: repeated agent runs that separate final task success,
protocol compliance, clean-pass rate, red-green churn, forbidden edits, and policy candidates.

## Current Status

Research prototype. The repo already contains:

- MCP server for agent pre-work protocols;
- Postgres + pgvector-backed knowledge retrieval;
- source-backed wiki pages with `dependsOn` edges;
- agent-facing `agent_work_context.v1`;
- agent-facing `agent_presentation_contract.v1` with `must_load`, `dependsOn`, decision rules, known failures, and evidence boundaries;
- Codex matrix runners for Drizzle version traps and Python API drift;
- run/event metrics, churn drill-downs, reports, and review workflows;
- matrix comparison read models for protocol compliance vs execution quality;
- strict adapter completion gates that require pre-work, dependency loading, verification, and final-answer recording before a gated run can complete;
- issue-ingestion review boundaries that keep GitHub claims as evidence-only until local verification and human review.

## Research Corpus

- [Deep research](./research/deep-research.md)
- [Paper corpus](./research/papers/README.md)

## Design Docs

- [Architecture](./docs/architecture.md)
- [Agent adapter layer](./docs/agent-adapters.md)
- [Agent work context](./docs/agent-work-context.md)
- [Codex MCP contract](./docs/codex-mcp.md)
- [Backend API contract](./docs/backend-api-contract.md)
- [Experiment methodology](./docs/experiment-methodology.md)
- [Issue evidence security](./docs/issue-evidence-security.md)
- [Knowledge wiki model](./docs/knowledge-wiki.md)
- [MCP dependency flow](./docs/mcp-dependency-flow.md)
- [Roadmap](./docs/roadmap.md)

## Quickstart

Start Postgres, migrate, seed, and run tests:

```bash
make up
make migrate
make seed
make test
```

Run the API:

```bash
make api
```

Open the static product UI after the API starts:

```text
http://127.0.0.1:8080/app/
```

Run the MCP server:

```bash
make mcp
```

Run the next matrix:

```bash
make api-drift-matrix
```

## Local Development

Check the database connection from the Docker network:

```bash
docker compose run --rm app uv run experiment-os db check
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

Run the harder version-trap matrix with a stricter oracle:

```bash
docker compose run --rm app uv run experiment-os experiments run-codex-version-trap-hard-matrix \
  --repeat-count 3 \
  --sandbox danger-full-access
```

Progress events are written as JSONL to stderr. The final JSON includes the matrix summary and, by
default, a markdown result artifact under `experiments/001-drizzle-brief/results/`.

Run the Python API-drift matrix:

```bash
docker compose run --rm app uv run experiment-os experiments run-codex-api-drift-matrix \
  --repeat-count 3 \
  --sandbox danger-full-access \
  --approval-policy never
```

Run the nested API-drift matrix:

```bash
docker compose run --rm app uv run experiment-os experiments run-codex-api-drift-nested-matrix \
  --repeat-count 3 \
  --sandbox danger-full-access \
  --approval-policy never
```

Run the non-saturated API-drift matrix where issue evidence is intentionally misleading:

```bash
docker compose run --rm app uv run experiment-os experiments run-codex-api-drift-misleading-matrix \
  --repeat-count 3 \
  --sandbox danger-full-access \
  --approval-policy never
```

Register Experiment OS as a Codex MCP server:

```bash
codex mcp add experiment-os -- docker compose -f "$(pwd)/docker-compose.yml" run --rm app uv run experiment-os mcp serve
```

Smoke-check the MCP presentation contract:

```bash
docker compose run --rm app uv run experiment-os demo mcp-smoke
```

Run a model matrix by repeating `--model`:

```bash
docker compose run --rm app uv run experiment-os experiments run-codex-version-trap-hard-matrix \
  --model gpt-5.4-mini \
  --model gpt-5.4
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

Use a local GitHub-search JSON payload for reproducible issue-ingestion tests:

```bash
docker compose run --rm app uv run experiment-os issues ingest \
  --repo openai/openai-python \
  --query "responses migration" \
  --input-json research/issues/openai-python-responses-search.json
```

Run several issue-ingestion jobs from a config:

```bash
docker compose run --rm app uv run experiment-os issues batch \
  --config research/issues/issue-ingestion-batch.example.json
```

Refresh issue-derived knowledge from GitHub. If `GITHUB_TOKEN` is present it is used for the API call:

```bash
docker compose run --rm app uv run experiment-os issues refresh \
  --repo openai/openai-python \
  --query "responses migration" \
  --limit 5
```

Check whether issue-derived version evidence matches the local project:

```bash
docker compose run --rm app uv run experiment-os issues version-alignment \
  --page-id claim.github-issue.drizzle-team.drizzle-orm.5661.versions \
  --local-version drizzle-orm=0.44.5
```

Prune local test pages from a dev database:

```bash
docker compose run --rm app uv run experiment-os db prune-test-pages
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

Useful UI/read-model endpoints:

- `GET /experiments`
- `GET /experiments/{experiment_id}/matrix`
- `GET /experiments/{experiment_id}/matrix/compare?left_matrix_id=...&right_matrix_id=...`
- `GET /experiments/{experiment_id}/matrix/regression?left_matrix_id=...&right_matrix_id=...`
- `POST /experiments/{experiment_id}/status`
- `GET /experiments/{experiment_id}/protocol-compliance`
- `GET /experiments/{experiment_id}/churn?matrix_id=...`
- `GET /runs/{run_id}`
- `GET /runs/{run_id}/completion-contract`
- `GET /runs/{run_id}/next-required-action`
- `GET /runs/{run_id}/churn`
- `GET /briefs/{brief_id}/agent-work-context`
- `GET /briefs/{brief_id}/presentation-preview`
- `GET /wiki/graph`
- `GET /knowledge/stale`
- `GET /knowledge/duplicates`
- `GET /pages/{page_id}/provenance`
- `POST /issue-knowledge/{page_id}/version-alignment`
- `GET /policy-candidates`
- `GET /ui/contract`
- `GET /ui/bootstrap`

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
- `src/experiment_os/services/` - application use cases, split into contracts, matrix comparison, regression, provenance, issue ingestion, review, and dashboard read models.
- `src/experiment_os/mcp_server/` - MCP transport adapter.
- `src/experiment_os/cli.py` - developer CLI only.

The MCP tools and CLI commands share the same service layer.

## Experimental Fixtures

- `fixtures/drizzle-version-trap-repo` - easy version trap, now mostly solved by current Codex.
- `fixtures/drizzle-version-trap-hard-repo` - stricter Drizzle oracle with one correct schema edit.
- `fixtures/python-api-drift-repo` - second-domain scaffold for Python SDK/API drift.
- `fixtures/python-api-drift-nested-repo` - API-drift fixture where the correct adapter is behind a nested module.
- `fixtures/python-api-drift-hard-nested-repo` - harder router fixture with dependency-upgrade bait.

## Current R&D Signal

The first flat-vs-nested API-drift comparison saturated final pass rate, so the useful signal moved
to execution quality:

- gated Codex reached full protocol compliance but produced red-green churn;
- gated OpenCode reached full protocol compliance with clean passes;
- final pass rate, protocol compliance, and clean pass rate must be tracked separately.

See:

- `experiments/002-python-api-drift/results/2026-04-28-matrix-api-drift-ab282831e5a2.md`
- `experiments/002-python-api-drift/results/2026-04-28-matrix-api-drift-nested-3bafb86522e5.md`
- `experiments/002-python-api-drift/results/2026-04-28-flat-vs-nested-matrix-comparison.md`
