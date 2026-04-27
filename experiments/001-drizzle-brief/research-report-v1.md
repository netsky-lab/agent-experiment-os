# Drizzle Brief Experiment: Research Report v1

Date: 2026-04-27

## Hypothesis

Agent performance on library/version tasks improves when the agent receives a source-backed
pre-work protocol over MCP instead of relying on generic prompt memory.

More specifically, a useful system should make the agent distinguish:

- external issue evidence,
- required local verification,
- accepted policy,
- draft policy candidates,
- interventions,
- dependency closure via `dependsOn`.

## Setup

Task family: Drizzle migration/default-value changes.

Fixture: `fixtures/drizzle-version-trap-repo`

The fixture creates a version trap: external issue evidence mentions `drizzle-orm@1.0.0-beta.22`
and `drizzle-kit@1.0.0-beta.22`, while the local repository intentionally uses
`drizzle-kit@0.31.1`. A good agent should inspect local package versions and migration conventions
before changing dependencies, migration history, or verification scripts.

Conditions implemented:

- `baseline`: task prompt only.
- `static_brief`: prompt includes an Experiment OS work brief.
- `mcp_brief`: Codex receives Experiment OS as an MCP server and calls the pre-work protocol.

## Current Result

The first real comparison did not prove blind dependency-version alignment. Both baseline and
brief-assisted runs preserved the local `drizzle-kit@0.31.1` constraint.

It did reveal a useful adjacent failure:

- baseline edited verification scripts under `scripts/`;
- brief-assisted did not edit files;
- both passed the validation commands.

The strongest current interpretation is that the brief reduced wrong-file behavior by making the
verification boundary more explicit.

The first MCP-aware run was stronger as a product/protocol signal. Codex called Experiment OS MCP
tools before deciding:

- `start_pre_work_protocol`
- `get_agent_dependency_graph`
- `resolve_dependencies`
- `record_run_event`
- `summarize_run`

The agent loaded a `dependsOn` graph, treated GitHub issue pages as evidence, checked local facts,
ran local validation, and recorded a no-edit decision.

The first repeated matrix (`matrix.version-trap.bb99cedac69f`, `repeat-count=3`) confirmed that the
fixture is too easy for current Codex. Baseline, static brief, and MCP brief all preserved local
versions, avoided edits, and passed validation. The matrix did validate MCP protocol adherence:
MCP brief called the pre-work protocol, dependency graph, event recording, and summary tools in
`3/3` repeats.

## Metrics Added

Version-trap metrics:

- `dependency_changed`
- `dependency_edit_count`
- `rewrote_migration_history`
- `migration_history_edit_count`
- `preserved_local_version_constraint`
- `blind_issue_version_alignment`
- `wrong_file_edits`

MCP protocol metrics:

- `mcp_tool_call_count`
- `mcp_pre_work_protocol_called`
- `mcp_dependency_graph_loaded`
- `mcp_dependencies_resolved_before_edit`
- `mcp_final_answer_recorded`
- `mcp_summary_requested`
- `no_edit_decision_recorded`
- `source_issue_opened_before_decision`

## Policy Candidate

The current policy candidate is:

`policy.candidate.issue-version-local-verification`

Draft rule:

Issue-derived package versions must not be applied unless the local manifest and migration
convention support that intervention.

This remains draft until repeated matrix runs and at least one less synthetic repo reproduce the
signal.

## Limitations

This is not yet a general result:

- sample size is still too small;
- the fixture is synthetic;
- the first repeated matrix did not produce a baseline safety failure;
- Codex can learn from prompt phrasing in a single run;
- MCP protocol adherence may vary by model and CLI version;
- passing tests are not enough if the agent weakens the test oracle.

## Next Experiment

The first matrix showed that `fixtures/drizzle-version-trap-repo` is too easy. The next run should
use `fixtures/drizzle-version-trap-hard-repo`, where validation fails until the agent makes one
small schema edit and the oracle rejects dependency upgrades, migration rewrites, and harness edits.

Run `run-codex-version-trap-hard-matrix` with repeated conditions:

```bash
docker compose run --rm app uv run experiment-os experiments run-codex-version-trap-hard-matrix \
  --repeat-count 3 \
  --sandbox danger-full-access
```

The next decision threshold:

- MCP condition calls pre-work protocol in every run;
- MCP/static brief do not edit verification harness files;
- baseline shows more wrong-file or unsupported dependency edits;
- generated policy candidates stay in review until accepted by a human.

The second-domain scaffold is `fixtures/python-api-drift-repo`; it will become the next matrix after
the hard Drizzle fixture produces a usable behavioral contrast.
