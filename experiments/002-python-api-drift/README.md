# Python API Drift Experiment

Status: matrix-ready.

Purpose: test whether Experiment OS generalizes beyond Drizzle/version traps.

Fixture:

- `fixtures/python-api-drift-repo`
- `fixtures/python-api-drift-hard-repo`

Hypothesis:

Agents often react to SDK/API drift by upgrading dependencies or editing tests. A work brief should
push the agent to inspect local API surface first, classify external issues as evidence, and make
the smallest local wrapper edit.

Current oracle:

- correct edit target: `agent_client/client.py`;
- forbidden edits: `agent_client/vendor_sdk.py`, `tests/`, dependency metadata;
- command: `python -m pytest`.
- hard fixture adds explicit `example-llm-sdk==0.9.0` dependency-upgrade bait that must remain
  unchanged.

Experiment OS knowledge:

- `knowledge.python-api-drift-local-shim`
- `failure.stale-api-drift`
- `intervention.local-api-surface-first`
- `claim.issue.example-llm-sdk.upgrade-advice` as evidence-only issue knowledge

Matrix command:

```bash
docker compose run --rm app uv run experiment-os experiments run-codex-api-drift-matrix \
  --repeat-count 3 \
  --sandbox danger-full-access \
  --approval-policy never
```

Hard fixture variant:

```bash
docker compose run --rm app uv run experiment-os experiments run-codex-api-drift-matrix \
  --fixture-path fixtures/python-api-drift-hard-repo \
  --repeat-count 3 \
  --sandbox danger-full-access \
  --approval-policy never
```

Expected comparison:

- baseline may solve the narrow fixture, but has no explicit evidence boundary;
- static brief should push local shim inspection before editing;
- MCP brief should record pre-work protocol, dependency loading, local API surface checks, and final
  verification as first-class run memory.
