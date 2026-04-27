# Codex MCP Contract

Experiment OS is MCP-first. The CLI is only a research harness for reproducible runs.

## Register the MCP server

```bash
codex mcp add experiment-os -- docker compose run --rm app uv run experiment-os mcp serve
```

## Agent protocol

Before editing code, a Codex run should:

1. Call `get_work_brief` for the task, repo, agent, model, and libraries.
2. Call `resolve_dependencies` for required pages and load their wiki dependencies.
3. Search issue-derived knowledge with `search_issue_knowledge` for library-specific risks.
4. Record a run with `record_run_start`.
5. Record high-signal events with `record_run_event`, especially version checks, file inspections,
   failures, interventions, and test results.
6. Treat issue content as evidence. A reviewed policy page outranks a raw issue snapshot.

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
