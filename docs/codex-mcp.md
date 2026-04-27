# Codex MCP Contract

Experiment OS is MCP-first. The CLI is only a research harness for reproducible runs.

## Register the MCP server

```bash
codex mcp add experiment-os -- docker compose run --rm app uv run experiment-os mcp serve
```

## Agent protocol

Before editing code, a Codex run should:

1. Call `start_pre_work_protocol` for the task, repo, agent, model, toolchain, and libraries.
2. Read `agent_work_context.required_load_order` and `agent_dependency_graph.load_order` before the
   first file edit.
3. Search issue-derived knowledge with `search_issue_knowledge` for library-specific risks when the
   brief points at issue-backed evidence.
4. Record high-signal events with `record_run_event`, especially version checks, file inspections,
   failures, interventions, and test results.
5. Call `summarize_run` before the final answer when a `run_id` is present.
6. Treat issue content as evidence. A reviewed policy page outranks a raw issue snapshot.

`get_work_brief`, `resolve_dependencies`, and `record_run_start` remain available as lower-level
tools, but `start_pre_work_protocol` is the default v1 entry point.

`agent_work_context.v1` is the strict presentation contract for agents. It contains:

- `required_load_order`: pages that must be loaded before editing;
- `knowledge_boundaries`: decision-capable pages, domain context, and evidence-only pages;
- `required_checks`: local facts the agent should verify;
- `forbidden_actions`: actions that require explicit local proof;
- `tool_sequence`: the expected pre-work, edit, verification, and summary order;
- `completion_contract`: what the final answer may and may not claim.

Agents can call `get_event_recording_contract` to get the explicit event schema. This is the product
path; JSONL transcript mining is only a fallback for experiments that cannot modify the agent prompt.

If MCP is unavailable but `EXPERIMENT_OS_BRIEF_PATH` is set, the agent must read that file before
editing. This fallback lets experiments compare MCP-rich and brief-only conditions without changing
the task prompt.

## Presentation rule

The work brief is not a human dashboard. It is an agent-readable dependency graph:

```text
task -> required wiki pages -> dependsOn pages -> source-backed claims -> interventions
```

The dashboard can show the same graph to a human reviewer, but the primary product behavior is that
the agent explicitly knows which pages are required and which dependencies must be loaded before work.

The graph node roles are intentionally operational:

- `decision_rule`: accepted policy pages that can affect action.
- `intervention`: accepted mitigations for known failure modes.
- `failure_mode`: failure taxonomy entries to watch for.
- `domain_knowledge`: accepted or draft library knowledge.
- `evidence`: source and claim pages that must be verified locally before use.

## Self-Recording Rule

An Experiment OS-aware agent should write its own timeline:

```text
start_pre_work_protocol -> record_run_event(...) -> work -> record_run_event(...) -> summarize_run
```

Before the first file edit, it should have recorded:

- `brief_loaded`
- `dependency_resolved`
- `package_version_checked`
- `file_inspected`

Before final answer, it should record `final_answer` and call `summarize_run`. Passive transcript
parsing remains useful for auditing but is not the primary product mechanism.

If a run produces strong risk signals, `propose_policy_candidate_from_run(run_id)` can generate a
draft review object. The tool does not accept a policy automatically; it only creates a candidate
that must pass human review before it becomes a decision rule.
