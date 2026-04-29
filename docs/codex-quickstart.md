# Codex Quickstart

This repo exposes Experiment OS through MCP so Codex can load agent-facing experiment knowledge
before editing.

## 1. Start Postgres And Seed Knowledge

```bash
make up
make migrate
make seed
```

## 2. Register The MCP Server

```bash
codex mcp add experiment-os -- docker compose -f "$(pwd)/docker-compose.yml" run --rm app uv run experiment-os mcp serve
```

## 3. Expected Agent Protocol

Before editing, Codex should call:

```text
start_pre_work_protocol
```

Then it should inspect:

```text
agent_work_context.required_load_order
agent_work_context.presentation_contract.must_load
agent_work_context.presentation_contract.dependsOn
```

Before risky edits, record a decision:

```text
record_decision(run_id, decision, rationale, evidence_ids)
```

Before final answer:

```text
complete_run(run_id, summary, outcome)
summarize_run(run_id)
```

## 4. Useful MCP Tools

- `start_pre_work_protocol`
- `get_agent_work_context`
- `get_agent_presentation_contract`
- `search_issue_knowledge`
- `page_provenance`
- `check_issue_version_alignment`
- `get_next_required_action`
- `record_decision`
- `complete_run`

## 5. Fallback

If MCP is unavailable, compile a brief and provide it to the agent as static context. This is weaker
than MCP because the agent cannot self-record decisions or ask for the next required action.
