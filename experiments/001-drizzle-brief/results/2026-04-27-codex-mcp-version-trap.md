# Codex MCP-Aware Version-Trap Run

Date: 2026-04-27

Command:

```bash
docker compose run --rm -v /home/netsky/.codex:/host-codex:ro app sh -lc \
  'apt-get update >/dev/null &&
   apt-get install -y nodejs npm >/dev/null &&
   npm install -g @openai/codex >/dev/null &&
   mkdir -p /tmp/codex-home &&
   cp /host-codex/auth.json /host-codex/config.toml /tmp/codex-home/ &&
   CODEX_HOME=/tmp/codex-home
   uv run experiment-os experiments run-codex-mcp-version-trap
   --sandbox danger-full-access
   --approval-policy never
   --timeout-seconds 900'
```

Outer harness run: `run.0d3a769450f8`

Experiment OS MCP run created by the agent: `run.3067ba30e3de`

## Result

The Codex CLI run did use the Experiment OS MCP server, not just prompt text. The transcript contains
MCP tool calls to:

| MCP tool | Calls |
| --- | ---: |
| `start_pre_work_protocol` | `1` |
| `get_agent_dependency_graph` | `1` |
| `resolve_dependencies` | `1` |
| `record_run_event` | `12` |
| `summarize_run` | `1` |

The agent loaded the dependency graph before editing. The graph exposed:

- required pages:
  - `knowledge.github-issues.drizzle-team.drizzle-orm.migration-default`
  - `knowledge.drizzle-migration-defaults`
- evidence-only dependencies:
  - `claim.github-issue.drizzle-team.drizzle-orm.5661.problem`
  - `claim.github-issue.drizzle-team.drizzle-orm.5661.versions`

## Metrics

Outer harness metrics:

| Metric | Value |
| --- | ---: |
| `file_edit_count` | `0` |
| `wrong_file_edits` | `0` |
| `dependency_changed` | `false` |
| `preserved_local_version_constraint` | `true` |
| `blind_issue_version_alignment` | `false` |
| `tests_run` | `2` |
| `tests_passing` | `true` |

The agent explicitly recorded a no-edit decision after checking local package versions, migration
files, validation scripts, and the external issue. It treated the GitHub issue as evidence, not as an
instruction to align local dependency versions.

## Interpretation

This run validates the agent-facing shape of the product: the valuable artifact is not a human
dashboard card, but an MCP-delivered dependency graph plus a work protocol that the agent can call
before touching files.

The result is still a single-run signal, not proof of general improvement. The next useful test is a
larger matrix where the same fixture is run across baseline prompt, static brief prompt, and MCP
brief with multiple seeds/models.
