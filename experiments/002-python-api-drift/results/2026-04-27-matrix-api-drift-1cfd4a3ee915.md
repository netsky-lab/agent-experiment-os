# Codex Api Drift Matrix

Date: 2026-04-27

Matrix id: `matrix.api-drift.1cfd4a3ee915`

Fixture: `fixtures/python-api-drift-hard-repo`

Repeat count: `1`

Models: `codex-default`

## Runs

| Model | Repeat | Condition | Run | Exit | Duration |
| --- | ---: | --- | --- | ---: | ---: |
| codex-default | 0 | baseline | `run.a9f7aab5e453` | 0 | 68.59s |
| codex-default | 0 | static_brief | `run.191c1753d629` | 0 | 36.76s |
| codex-default | 0 | gated_brief | `run.b83a018ae49b` | 0 | 74.05s |
| codex-default | 0 | opencode_gated_brief | `run.1e0e56a39ca3` | 0 | 63.35s |

## Summary

### baseline

- run count: `1`
- tests passing rate: `1.00`
- test failure mean: `0.00`
- dependency change rate: `0.00`
- file edit mean: `1.00`
- wrong-file edit mean: `0.00`
- MCP pre-work rate: `0.00`
- MCP call mean: `0.00`

### gated_brief

- run count: `1`
- tests passing rate: `1.00`
- test failure mean: `1.00`
- dependency change rate: `0.00`
- file edit mean: `1.00`
- wrong-file edit mean: `0.00`
- MCP pre-work rate: `1.00`
- MCP call mean: `5.00`

### opencode_gated_brief

- run count: `1`
- tests passing rate: `1.00`
- test failure mean: `0.00`
- dependency change rate: `0.00`
- file edit mean: `1.00`
- wrong-file edit mean: `0.00`
- MCP pre-work rate: `1.00`
- MCP call mean: `5.00`

### static_brief

- run count: `1`
- tests passing rate: `1.00`
- test failure mean: `0.00`
- dependency change rate: `0.00`
- file edit mean: `1.00`
- wrong-file edit mean: `0.00`
- MCP pre-work rate: `0.00`
- MCP call mean: `0.00`

## Interpretation

This matrix validates the adapter-level gate as a protocol mechanism, not as a task-success
improvement. All four conditions completed the hard API-drift task, preserved dependency metadata,
edited one file, and avoided wrong-file edits.

The difference is protocol compliance:

- baseline and static brief solved the task with `0.00` MCP pre-work rate;
- Codex `gated_brief` solved the task with `1.00` MCP pre-work rate and full post-run recording;
- OpenCode `opencode_gated_brief` also solved the task with `1.00` MCP pre-work rate.

This confirms the earlier negative finding: asking the agent to use MCP is weaker than enforcing
pre-work outside the agent. The gate makes Experiment OS memory observable regardless of whether
the agent CLI exposes the expected MCP tools.

## Cross-agent Note

OpenCode initially exposed an extractor bug: the transcript parser treated prompt/context text as
real edits. After switching OpenCode parsing to its JSON event stream, the run shows one correct
edit to `agent_client/client.py`, one passing verification run, and no forbidden edits.

## Decision

Do not promote a correctness policy from this matrix. The fixture remains too easy for current
Codex and OpenCode on final task success.

Promote the engineering direction:

- adapter-enforced pre-work should be the default for Experiment OS controlled runs;
- dashboard views should separate task success from protocol compliance;
- prompt-only MCP conditions should remain a control group, not the production path.

## Next Experiment Design

- Run at least three repeats with `gated_brief` and `opencode_gated_brief`.
- Add a larger fixture where local API surface is not adjacent to the failing wrapper.
- Add a policy candidate only when forbidden edits, dependency edits, or repeated red-green churn
  appear across repeated runs.
