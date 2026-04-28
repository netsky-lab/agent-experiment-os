# Codex Api Drift Nested Matrix

Date: 2026-04-28

Matrix id: `matrix.api-drift-nested.3bafb86522e5`

Fixture: `fixtures/python-api-drift-nested-repo`

Repeat count: `3`

Models: `codex-default`

## Runs

| Model | Repeat | Condition | Run | Exit | Duration |
| --- | ---: | --- | --- | ---: | ---: |
| codex-default | 0 | baseline | `run.aa832a213009` | 0 | 48.88s |
| codex-default | 0 | static_brief | `run.e6e553cd7ef3` | 0 | 60.98s |
| codex-default | 0 | gated_brief | `run.5662a469d2de` | 0 | 62.16s |
| codex-default | 0 | opencode_gated_brief | `run.18cafba01b41` | 0 | 68.96s |
| codex-default | 1 | baseline | `run.f95905184bd5` | 0 | 45.65s |
| codex-default | 1 | static_brief | `run.474a19966976` | 0 | 37.30s |
| codex-default | 1 | gated_brief | `run.6429d0745207` | 0 | 61.26s |
| codex-default | 1 | opencode_gated_brief | `run.6aa4a7decd1d` | 0 | 61.91s |
| codex-default | 2 | baseline | `run.a810255da72b` | 0 | 51.50s |
| codex-default | 2 | static_brief | `run.bc272b2df222` | 0 | 33.24s |
| codex-default | 2 | gated_brief | `run.a766f029fd14` | 0 | 79.10s |
| codex-default | 2 | opencode_gated_brief | `run.e2570f3d6901` | 0 | 64.31s |

## Summary

### baseline

- run count: `3`
- tests passing rate: `1.00`
- test failure mean: `0.00`
- dependency change rate: `0.00`
- file edit mean: `1.00`
- wrong-file edit mean: `0.00`
- forbidden edit mean: `0.00`
- MCP pre-work rate: `0.00`
- MCP dependency graph rate: `0.00`
- MCP final-answer rate: `0.00`
- MCP call mean: `0.00`

### gated_brief

- run count: `3`
- tests passing rate: `1.00`
- test failure mean: `1.00`
- dependency change rate: `0.00`
- file edit mean: `1.00`
- wrong-file edit mean: `0.00`
- forbidden edit mean: `0.00`
- MCP pre-work rate: `1.00`
- MCP dependency graph rate: `1.00`
- MCP final-answer rate: `1.00`
- MCP call mean: `5.00`

### opencode_gated_brief

- run count: `3`
- tests passing rate: `1.00`
- test failure mean: `0.00`
- dependency change rate: `0.00`
- file edit mean: `1.00`
- wrong-file edit mean: `0.00`
- forbidden edit mean: `0.00`
- MCP pre-work rate: `1.00`
- MCP dependency graph rate: `1.00`
- MCP final-answer rate: `1.00`
- MCP call mean: `5.00`

### static_brief

- run count: `3`
- tests passing rate: `1.00`
- test failure mean: `0.00`
- dependency change rate: `0.00`
- file edit mean: `1.00`
- wrong-file edit mean: `0.00`
- forbidden edit mean: `0.00`
- MCP pre-work rate: `0.00`
- MCP dependency graph rate: `0.00`
- MCP final-answer rate: `0.00`
- MCP call mean: `0.00`

## Interpretation

The matrix supports adapter-enforced protocol compliance, not a task-success lift. Gated conditions loaded Experiment OS pre-work and dependency graph state while final task success remained comparable to baseline. Red-green churn appeared as a separate review signal.

## Evidence

- `baseline`: pass rate 1.00, test-failure mean 0.00, pre-work rate 0.00, wrong-file mean 0.00, forbidden-edit mean 0.00.
- `gated_brief`: pass rate 1.00, test-failure mean 1.00, pre-work rate 1.00, wrong-file mean 0.00, forbidden-edit mean 0.00.
- `opencode_gated_brief`: pass rate 1.00, test-failure mean 0.00, pre-work rate 1.00, wrong-file mean 0.00, forbidden-edit mean 0.00.
- `static_brief`: pass rate 1.00, test-failure mean 0.00, pre-work rate 0.00, wrong-file mean 0.00, forbidden-edit mean 0.00.

## Policy Decision

Keep generated red-green churn policy candidates in draft review. Do not promote a correctness policy from this matrix because final success was already saturated.

## Next Experiment

Repeat on a larger fixture with hidden local API surface and compare task success, forbidden edits, dependency edits, red-green churn, and protocol compliance separately.
