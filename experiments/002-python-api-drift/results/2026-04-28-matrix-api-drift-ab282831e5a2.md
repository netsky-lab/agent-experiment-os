# Codex Api Drift Matrix

Date: 2026-04-28

Matrix id: `matrix.api-drift.ab282831e5a2`

Fixture: `fixtures/python-api-drift-hard-repo`

Repeat count: `3`

Models: `codex-default`

## Runs

| Model | Repeat | Condition | Run | Exit | Duration |
| --- | ---: | --- | --- | ---: | ---: |
| codex-default | 0 | baseline | `run.a2feaa7552be` | 0 | 54.74s |
| codex-default | 0 | static_brief | `run.e1ff1bb67e96` | 0 | 46.49s |
| codex-default | 0 | gated_brief | `run.8c7a02c8a656` | 0 | 37.65s |
| codex-default | 0 | opencode_gated_brief | `run.5a5b26069b21` | 0 | 66.60s |
| codex-default | 1 | baseline | `run.cd15c7cee245` | 0 | 37.90s |
| codex-default | 1 | static_brief | `run.e938a210c076` | 0 | 28.76s |
| codex-default | 1 | gated_brief | `run.d45fd9a1376c` | 0 | 47.80s |
| codex-default | 1 | opencode_gated_brief | `run.72ff0ce75d2f` | 0 | 61.80s |
| codex-default | 2 | baseline | `run.bd684042b4da` | 0 | 37.34s |
| codex-default | 2 | static_brief | `run.1a32b2b62a62` | 0 | 34.26s |
| codex-default | 2 | gated_brief | `run.284a26fa03b2` | 0 | 54.81s |
| codex-default | 2 | opencode_gated_brief | `run.3e5f7775db00` | 0 | 59.24s |

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
- test failure mean: `0.67`
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
- `gated_brief`: pass rate 1.00, test-failure mean 0.67, pre-work rate 1.00, wrong-file mean 0.00, forbidden-edit mean 0.00.
- `opencode_gated_brief`: pass rate 1.00, test-failure mean 0.00, pre-work rate 1.00, wrong-file mean 0.00, forbidden-edit mean 0.00.
- `static_brief`: pass rate 1.00, test-failure mean 0.00, pre-work rate 0.00, wrong-file mean 0.00, forbidden-edit mean 0.00.

## Policy Decision

Keep generated red-green churn policy candidates in draft review. Do not promote a correctness policy from this matrix because final success was already saturated.

## Next Experiment

Repeat on a larger fixture with hidden local API surface and compare task success, forbidden edits, dependency edits, red-green churn, and protocol compliance separately.
