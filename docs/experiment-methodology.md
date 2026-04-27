# Experiment Methodology

Experiment OS treats agent work as a knowledge-production loop:

```text
hypothesis -> task fixture -> agent run -> observed failures -> metric movement
-> interpretation -> intervention -> next experiment -> policy candidate
```

## Conditions

Each matrix should compare at least three conditions:

- `baseline`: task prompt only;
- `static_brief`: the same task with a precompiled work brief;
- `mcp_brief`: the agent must call Experiment OS MCP and self-record its work.

## Required Measurements

For each run, capture:

- final verification outcome;
- intermediate test failures and red-green behavior;
- wrong-file edits;
- dependency edits;
- forbidden edits;
- MCP pre-work protocol usage;
- dependency graph loading before first edit;
- final answer recording and summary request;
- duration and retry count.

## Evidence Rules

Raw issues, source snapshots, and claims are evidence only. They cannot become agent decision rules
until a reviewed policy or intervention is accepted.

Good experiments make misleading evidence available, then measure whether the agent verifies local
facts before acting on it.

## Promotion Rule

A policy candidate should stay draft unless repeated matrix evidence shows a behavioral improvement
or risk reduction. Observability alone is useful, but it is not enough to promote a policy.
