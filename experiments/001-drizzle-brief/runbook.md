# Runbook

## 1. Prepare Knowledge

```bash
docker compose up -d postgres
docker compose run --rm app uv run experiment-os db migrate
docker compose run --rm app uv run experiment-os db seed
docker compose run --rm app uv run experiment-os issues ingest \
  --repo drizzle-team/drizzle-orm \
  --query "migration default" \
  --limit 3
```

## 2. Review Drafts

```bash
docker compose run --rm app uv run experiment-os knowledge list --status draft
```

Accept only cards that are useful and source-backed:

```bash
docker compose run --rm app uv run experiment-os knowledge set-status <page_id> accepted
```

## 3. Run MCP Smoke

```bash
docker compose run --rm app uv run experiment-os demo mcp-smoke
```

## 3b. Run Deterministic A/B Fixture

```bash
docker compose run --rm app uv run experiment-os experiments run-drizzle-fixture
```

This does not run a real coding agent yet. It records controlled baseline and
brief-assisted event timelines so the metrics extractor and experiment result
storage can be validated.

## 4. Run Agent Conditions

Baseline:

```text
Give the task directly to the agent.
Do not provide an Experiment OS brief.
```

Brief-assisted:

```text
Require the agent to call get_work_brief and resolve_dependencies before editing.
```

## 5. Record Observations

Use run events:

```bash
docker compose run --rm app uv run experiment-os demo mcp-smoke
```

Manual observations should be converted into run events in the next implementation.
