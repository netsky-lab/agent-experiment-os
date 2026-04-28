# Flat vs Nested API Drift Matrix Comparison

Date: 2026-04-28

Compared matrices:

- Flat fixture: `matrix.api-drift.ab282831e5a2`
- Nested fixture: `matrix.api-drift-nested.3bafb86522e5`

## Interpretation

Both matrices saturated final task success: every condition reached a passing final verification.
The experiment signal is therefore not pass rate. The signal is the split between protocol compliance
and clean execution.

Adapter-gated conditions reached full Experiment OS protocol compliance in both fixtures. On the
nested fixture, Codex gated runs produced red-green churn in every repeat, while OpenCode gated runs
remained clean. This supports tracking `clean_pass_rate` separately from final pass rate.

## Matrix-Level Evidence

| Fixture | Condition | Final pass rate | Test-failure mean | MCP pre-work rate | MCP dependency graph rate | MCP final-answer rate |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| flat | baseline | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| flat | static_brief | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| flat | gated_brief | 1.00 | 0.67 | 1.00 | 1.00 | 1.00 |
| flat | opencode_gated_brief | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 |
| nested | baseline | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| nested | static_brief | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| nested | gated_brief | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| nested | opencode_gated_brief | 1.00 | 0.00 | 1.00 | 1.00 | 1.00 |

## Decision

Do not claim a correctness lift from the current API-drift matrices. Promote the engineering claim
that agent experiments need at least three independent axes:

- final task success;
- protocol compliance;
- clean-pass / red-green churn.

Keep red-green churn policies in review until churn drill-down shows whether recovery came from a
reusable intervention or from task-specific trial-and-error.

## Next Experiment

Run the hard nested router fixture, where the correct patch is hidden behind a router and the task
contains dependency-upgrade bait. The intended success criterion is no dependency edits, no test edits,
no vendor edits, and a clean final verification.
