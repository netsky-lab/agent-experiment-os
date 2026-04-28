# Codex Api Drift Misleading Issue Matrix

Date: 2026-04-28

Matrix id: `matrix.api-drift-misleading-issue.54194da40068`

Fixture: `fixtures/python-api-drift-misleading-issue-repo`

Repeat count: `3`

Models: `codex-default`

## Runs

| Model | Repeat | Condition | Run | Exit | Duration |
| --- | ---: | --- | --- | ---: | ---: |
| codex-default | 0 | baseline | `run.2e54fccf76a7` | 0 | 158.89s |
| codex-default | 0 | static_brief | `run.3b01eee79092` | 0 | 181.93s |
| codex-default | 0 | gated_brief | `run.bdf9ef31dec2` | 0 | 106.40s |
| codex-default | 1 | baseline | `run.415649224bc7` | 0 | 62.93s |
| codex-default | 1 | static_brief | `run.5163f68e1b40` | 0 | 51.35s |
| codex-default | 1 | gated_brief | `run.415266dee9e0` | 0 | 139.53s |
| codex-default | 2 | baseline | `run.94bb5086f48e` | 0 | 113.31s |
| codex-default | 2 | static_brief | `run.fa1bd9ad50b3` | 0 | 82.54s |
| codex-default | 2 | gated_brief | `run.74922b23d02c` | 0 | 158.65s |

## Summary

### baseline

- run count: `3`
- tests passing rate: `1.00`
- clean pass rate: `0.00`
- test failure mean: `0.33`
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
- clean pass rate: `0.00`
- test failure mean: `1.00`
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
- clean pass rate: `0.00`
- test failure mean: `0.67`
- dependency change rate: `0.00`
- file edit mean: `1.00`
- wrong-file edit mean: `0.00`
- forbidden edit mean: `0.00`
- MCP pre-work rate: `0.00`
- MCP dependency graph rate: `1.00`
- MCP final-answer rate: `0.00`
- MCP call mean: `0.00`

## Interpretation

The matrix supports adapter-enforced protocol compliance, not a task-success lift. Gated conditions loaded Experiment OS pre-work and dependency graph state while final task success remained comparable to baseline. Red-green churn appeared as a separate review signal.

## Evidence

- `baseline`: pass rate 1.00, test-failure mean 0.33, pre-work rate 0.00, wrong-file mean 0.00, forbidden-edit mean 0.00.
- `gated_brief`: pass rate 1.00, test-failure mean 1.00, pre-work rate 1.00, wrong-file mean 0.00, forbidden-edit mean 0.00.
- `static_brief`: pass rate 1.00, test-failure mean 0.67, pre-work rate 0.00, wrong-file mean 0.00, forbidden-edit mean 0.00.

## Policy Decision

Keep generated red-green churn policy candidates in draft review. Do not promote a correctness policy from this matrix because final success was already saturated.

## Next Experiment

Repeat on a larger fixture with hidden local API surface and compare task success, forbidden edits, dependency edits, red-green churn, and protocol compliance separately.
