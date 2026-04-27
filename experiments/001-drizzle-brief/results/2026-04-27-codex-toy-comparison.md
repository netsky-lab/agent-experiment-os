# Codex Toy Baseline vs Brief-Assisted Comparison

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
   uv run experiment-os experiments run-codex-toy-comparison
   --sandbox danger-full-access
   --approval-policy never
   --timeout-seconds 900'
```

## Behavioral Run

Baseline run: `run.946a3b716e64`

Brief-assisted run: `run.749a4c186de6`

| Metric | Baseline | Brief-assisted |
| --- | ---: | ---: |
| `inspected_package_versions_before_edit` | `true` | `true` |
| `inspected_migration_conventions_before_edit` | `true` | `true` |
| `tests_run` | `2` | `2` |
| `tests_passing` | `true` | `true` |
| `failure_count` | `3` | `3` |
| `file_edit_count` | parser missed structured `file_change` | `0` |

Interpretation:

The toy fixture is too easy. Baseline discovered the relevant version/migration checks without the
brief and even attempted to align `drizzle-kit` with `drizzle-orm`. Brief-assisted avoided editing
and still passed the fixture. This does not produce a strong product signal because the task lacks a
real trap where issue knowledge can help.

Follow-up:

- Add a fixture where the issue-derived beta signal conflicts with the local `drizzle-kit` version.
- Make the fixture fail if the agent changes `package.json` instead of preserving the local version
  constraint and verifying migration conventions.
- Improve Codex JSONL parsing for structured `file_change.changes`; this run exposed that the parser
  missed baseline's `package.json` edit.

## Infra Run

Before the behavioral run, the same comparison was attempted with `--sandbox workspace-write` inside
the app container:

- Baseline: `run.6b7c541ed9de`
- Brief-assisted: `run.949d82872e78`

Both conditions were blocked by Codex's `bwrap` sandbox wrapper:

```text
bwrap: No permissions to create a new namespace
```

Interpretation:

This is a harness/environment failure, not an agent behavior result. Containerized Codex comparisons
need either a sandbox mode that works inside the app container or a container profile that permits
the namespace behavior required by the Codex sandbox.
