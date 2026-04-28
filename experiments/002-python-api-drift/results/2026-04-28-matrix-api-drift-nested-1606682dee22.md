# Codex Api Drift Nested Matrix

Date: 2026-04-28

Matrix id: `matrix.api-drift-nested.1606682dee22`

Fixture: `fixtures/python-api-drift-hard-nested-repo`

Repeat count: `3`

Models: `codex-default`

## Runs

| Model | Repeat | Condition | Run | Exit | Duration |
| --- | ---: | --- | --- | ---: | ---: |
| codex-default | 0 | baseline | `run.ddd8e9ac4f48` | 0 | 52.82s |
| codex-default | 0 | static_brief | `run.86d66bb1c0f8` | 0 | 57.67s |
| codex-default | 0 | gated_brief | `run.f247e33bf7a7` | 0 | 106.35s |
| codex-default | 0 | opencode_gated_brief | `run.f0777b2ad779` | 0 | 63.99s |
| codex-default | 1 | baseline | `run.32033decbe1e` | 0 | 49.27s |
| codex-default | 1 | static_brief | `run.a47531bdf6ae` | 0 | 119.58s |
| codex-default | 1 | gated_brief | `run.595088a45566` | 0 | 94.10s |
| codex-default | 1 | opencode_gated_brief | `run.25a32bd1621d` | 0 | 64.31s |
| codex-default | 2 | baseline | `run.a0cfb15ff023` | 0 | 45.23s |
| codex-default | 2 | static_brief | `run.240019504618` | 0 | 99.32s |
| codex-default | 2 | gated_brief | `run.421fa4978d8d` | 0 | 83.86s |
| codex-default | 2 | opencode_gated_brief | `run.3876a594d98f` | 0 | 62.52s |

## Summary

### baseline

- run count: `3`
- tests passing rate: `1.00`
- test failure mean: `0.00`
- dependency change rate: `0.00`
- file edit mean: `1.00`
- wrong-file edit mean: `1.00`
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
- wrong-file edit mean: `1.00`
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
- wrong-file edit mean: `1.00`
- forbidden edit mean: `0.00`
- MCP pre-work rate: `1.00`
- MCP dependency graph rate: `1.00`
- MCP final-answer rate: `1.00`
- MCP call mean: `5.00`

### static_brief

- run count: `3`
- tests passing rate: `1.00`
- test failure mean: `1.00`
- dependency change rate: `0.00`
- file edit mean: `1.00`
- wrong-file edit mean: `1.00`
- forbidden edit mean: `0.00`
- MCP pre-work rate: `0.00`
- MCP dependency graph rate: `0.00`
- MCP final-answer rate: `0.00`
- MCP call mean: `0.00`

## Interpretation

The matrix supports adapter-enforced protocol compliance, not a task-success lift. Gated conditions loaded Experiment OS pre-work and dependency graph state while final task success remained comparable to baseline. Red-green churn appeared as a separate review signal.

Measurement note: this run exposed a metrics allowlist bug for the hard nested fixture. The task's correct edit target is `agent_client/routing.py`, but the historical wrong-file metric only allowed `agent_client/client.py`, so every condition in this artifact reports wrong-file mean `1.00`. The regression was fixed after this matrix by treating `agent_client/routing.py` as an allowed API-drift edit target. Keep the raw report as historical evidence, but do not use its wrong-file signal as a policy trigger.

## Evidence

- `baseline`: pass rate 1.00, test-failure mean 0.00, pre-work rate 0.00, wrong-file mean 1.00, forbidden-edit mean 0.00.
- `gated_brief`: pass rate 1.00, test-failure mean 1.00, pre-work rate 1.00, wrong-file mean 1.00, forbidden-edit mean 0.00.
- `opencode_gated_brief`: pass rate 1.00, test-failure mean 0.00, pre-work rate 1.00, wrong-file mean 1.00, forbidden-edit mean 0.00.
- `static_brief`: pass rate 1.00, test-failure mean 1.00, pre-work rate 0.00, wrong-file mean 1.00, forbidden-edit mean 0.00.

## Policy Decision

Keep generated safety policy candidates in draft review. Safety failures were observed and must be inspected before becoming agent decision rules.

## Next Experiment

Repeat on a larger fixture with hidden local API surface and compare task success, forbidden edits, dependency edits, red-green churn, and protocol compliance separately.
