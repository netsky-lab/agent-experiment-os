# Public Matrix Report

The current strongest public signal comes from the Python API-drift misleading-issue matrix.

Matrix:

```text
matrix.api-drift-misleading-issue.54194da40068
```

Fixture:

```text
fixtures/python-api-drift-misleading-issue-repo
```

## Key Result

Final task success saturated:

```text
baseline      tests passing rate 1.00
static_brief  tests passing rate 1.00
gated_brief   tests passing rate 1.00
```

But clean pass stayed low:

```text
baseline      clean pass rate 0.00
static_brief  clean pass rate 0.00
gated_brief   clean pass rate 0.00
```

And protocol compliance separated clearly:

```text
baseline      MCP pre-work rate 0.00
static_brief  MCP pre-work rate 0.00
gated_brief   MCP pre-work rate 1.00
```

## Interpretation

This does not prove that a brief makes a strong model solve an easy fixture better. The task was
already mostly solved.

It proves a more useful measurement point:

```text
final pass rate can be saturated while clean pass and protocol compliance still reveal risk.
```

That is why Experiment OS tracks red-green churn, failure causes, and final-answer contracts instead
of treating "green at the end" as enough evidence for policy promotion.

## Policy Consequence

Policy candidates from saturated matrices stay draft unless they show another risk reduction:

- fewer forbidden edits;
- fewer wrong-file edits;
- lower red-green churn;
- stronger evidence provenance;
- stricter agent protocol compliance.

The correct product behavior is conservative promotion, not automatic rule generation.
