# Thesis

Experiment OS is not an eval dashboard.

Evals usually answer whether a model passed a task. Experiment OS asks a more useful engineering
question:

```text
What did this run teach us, and when is that lesson safe to reuse?
```

The project turns agent work into an auditable knowledge loop:

```text
hypothesis -> test design -> run -> observed failures -> metric movement
-> interpretation -> intervention -> next experiment -> accumulated policy
```

## Product Claim

Coding-agent infrastructure needs a system of record for experimental knowledge:

- hypotheses become testable matrices;
- matrices produce run-level evidence;
- run events expose failure modes and recovery behavior;
- repeated evidence can become draft policy;
- accepted policy is presented back to agents through MCP.

The main user is not only the human reviewer. The agent itself needs a presentation layer that says:

- which pages must be loaded;
- which pages are only evidence;
- which decision rules are accepted;
- which dependencies and source claims support the rule;
- which final-answer claims are forbidden without verification.

## Why This Is Different From Memory

Generic memory systems optimize recall. Experiment OS optimizes governed reuse.

The system does not say "an issue mentioned this workaround, so do it." It says:

```text
This issue is external evidence.
Verify the local version and API surface.
Only accepted policies can change agent behavior.
```

That distinction is the product.

## Research Direction

The near-term research target is not higher pass rate on saturated tasks. It is better separation of:

- final pass rate;
- clean pass rate;
- protocol compliance;
- red-green churn;
- wrong-file edits;
- forbidden edits;
- policy evidence quality.

Once those signals are separated, policy decisions become inspectable instead of vibes.
