# Codex Toy Dry-Run Result

Date: 2026-04-27

Command:

```bash
DATABASE_URL=postgresql://experiment_os:experiment_os@localhost:5432/experiment_os \
  uv run experiment-os experiments run-codex-toy \
  --condition-id condition.001-drizzle-brief-assisted \
  --sandbox workspace-write \
  --approval-policy never \
  --timeout-seconds 900
```

Run: `run.9ae058734c10`

Condition: `brief-assisted`

Observed metrics:

- `exit_code`: `0`
- `duration_seconds`: `61.71`
- `inspected_package_versions_before_edit`: `true`
- `inspected_migration_conventions_before_edit`: `true`
- `tests_run`: `2`
- `tests_passing`: `true`
- `failure_count`: `0`
- `file_edit_count`: `0`
- `wrong_file_edits`: `0`

Observed behavior:

- Codex loaded the Experiment OS brief from `EXPERIMENT_OS_BRIEF_PATH` before editing.
- Codex inspected `package.json`, `drizzle/migrations/0001_initial.sql`, `drizzle.config.ts`,
  and `src/db/schema.ts` before running verification.
- Codex ran `npm run db:generate` and `npm test`; both passed.
- Codex correctly concluded that no code change was needed.

Harness learnings:

- `codex exec` expects `--ask-for-approval` as a global Codex flag before `exec`.
- `--cd` should be absolute when the subprocess also runs with `cwd=workdir`.
- Brief paths passed through `EXPERIMENT_OS_BRIEF_PATH` should be absolute because the agent's
  process root is the copied fixture workspace, not the Experiment OS repo root.
- Codex JSONL should be parsed structurally from `command_execution` items; raw transcript regex
  parsing over JSON creates false failures from fixture source code and transport log lines.
