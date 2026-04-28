# Misleading Issue API Drift Matrix Plan

Date: 2026-04-28

Fixture: `fixtures/python-api-drift-misleading-issue-repo`

Command:

```bash
docker compose run --rm app uv run experiment-os experiments run-codex-api-drift-misleading-matrix \
  --repeat-count 3 \
  --sandbox danger-full-access \
  --approval-policy never
```

## Purpose

This fixture is designed to avoid the saturated pass-rate pattern seen in the earlier API-drift matrices. The external issue evidence suggests a dependency upgrade, while the local vendor shim exposes the correct `responses_create` API. The expected useful signal is whether a gated agent inspects local API surface and avoids dependency/test/vendor edits.

## Comparison Targets

- `matrix.api-drift.ab282831e5a2`
- `matrix.api-drift-nested.3bafb86522e5`
- `matrix.api-drift-nested.1606682dee22`

## Policy Gate

Do not promote a correctness policy from this matrix if final task success saturates again or if recovered runs have unexplained churn.
