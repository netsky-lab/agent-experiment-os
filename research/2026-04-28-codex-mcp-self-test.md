# Codex MCP Self-Test

Date: 2026-04-28

## Setup

Codex was restarted with the `experiment_os` MCP server available. This run used the MCP tools directly from the agent session, not only the local CLI.

MCP pre-work call:

- `start_pre_work_protocol`
- `brief_id`: `brief.40e6fb76e9d6`
- `run_id`: `run.899bed6609cc`
- task: implement the eight-step Experiment OS scope

Initial recorded event:

- `dependency_resolved`
- event id: `137d009f-88d3-41fc-988e-c3ad76cb022d`

## Observations

The MCP contract is usable as an agent-facing work gate. The agent can obtain:

- `must_load` knowledge
- `dependsOn` graph
- known failure modes
- decision rules
- explicit event-recording schema
- a run id for dogfooding the work itself

The current weak point is not tool availability; it is disciplined event recording. If the agent does not record `file_inspected`, `file_edited`, `test_run`, and `final_answer` as the work happens, the run degrades into a post-hoc log. The new regression test keeps `final_answer` and dependency graph loading visible in metrics.

## Design Implication

MCP should remain the primary agent integration surface. REST remains useful for the human dashboard, but the agent-facing product needs presentation contracts, not generic CRUD.

## Follow-Up

Add a stricter MCP compliance mode that refuses to mark a run complete unless:

- pre-work was started
- dependencies were loaded before edit
- tests were recorded after execution
- final answer was recorded before responding
