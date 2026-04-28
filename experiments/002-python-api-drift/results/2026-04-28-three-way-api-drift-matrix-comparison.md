# Three-Way API Drift Matrix Comparison

Date: 2026-04-28

Compared matrices:

- Flat hard fixture: `matrix.api-drift.ab282831e5a2`
- Nested fixture: `matrix.api-drift-nested.3bafb86522e5`
- Hard nested fixture: `matrix.api-drift-nested.1606682dee22`

## Result

The strongest signal is protocol compliance, not final task success. All three fixtures saturated final pass rate at `1.00` across all conditions, so the experiment cannot claim a task-success lift yet. The useful product signal is that gated MCP conditions consistently recorded pre-work, dependency graph loading, and final-answer recording at `1.00`, while baseline/static conditions stayed at `0.00`.

## Condition Pattern

| Fixture | Condition | Pass rate | Test failure mean | MCP pre-work rate | MCP call mean |
| --- | --- | ---: | ---: | ---: | ---: |
| Flat hard | baseline | 1.00 | 0.00 | 0.00 | 0.00 |
| Flat hard | static_brief | 1.00 | 0.00 | 0.00 | 0.00 |
| Flat hard | gated_brief | 1.00 | 0.67 | 1.00 | 5.00 |
| Flat hard | opencode_gated_brief | 1.00 | 0.00 | 1.00 | 5.00 |
| Nested | baseline | 1.00 | 0.00 | 0.00 | 0.00 |
| Nested | static_brief | 1.00 | 0.00 | 0.00 | 0.00 |
| Nested | gated_brief | 1.00 | 1.00 | 1.00 | 5.00 |
| Nested | opencode_gated_brief | 1.00 | 0.00 | 1.00 | 5.00 |
| Hard nested | baseline | 1.00 | 0.00 | 0.00 | 0.00 |
| Hard nested | static_brief | 1.00 | 1.00 | 0.00 | 0.00 |
| Hard nested | gated_brief | 1.00 | 1.00 | 1.00 | 5.00 |
| Hard nested | opencode_gated_brief | 1.00 | 0.00 | 1.00 | 5.00 |

## Interpretation

`opencode_gated_brief` is the cleanest protocol shape so far: it preserves the MCP contract while avoiding red-green churn in all three matrices. `gated_brief` records the contract but introduces at least some churn, so it should be treated as a review signal rather than a decision-rule candidate.

The hard nested matrix also found an Experiment OS measurement bug. The correct edit moved from `agent_client/client.py` to `agent_client/routing.py`, but the historical wrong-file metric only allowed `client.py`. That is exactly the kind of failure this repo should surface: not just agent errors, but evaluator and instrumentation errors that would otherwise turn into bad policy.

## Product Decision

Keep the UI centered on agent-facing contracts and evidence review:

- Show protocol compliance separately from task success.
- Show churn as review work, not automatic failure.
- Require evidence ids before accepting policy candidates.
- Treat issue-ingested knowledge as evidence-only until local verification.

## Next Experiment

Create a fixture where baseline success is not saturated. The next task should require resolving both local API drift and misleading issue-derived advice, so the core metric can distinguish "passed with protocol" from "passed by luck."
