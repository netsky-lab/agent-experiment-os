# Experiment OS vs Evals

Date: 2026-04-28

Experiment OS is not an eval dashboard. Evals usually answer whether a model passed a task. This repo is designed to preserve why the run behaved the way it did and what should change before the next run.

The unit of value is the chain:

```text
hypothesis -> test design -> run -> failure -> metric movement -> interpretation -> intervention -> policy
```

The product surface follows that chain:

- MCP presents `must_load`, `dependsOn`, known failures, and decision rules to agents before editing.
- Runs record structured events while work happens, not only after completion.
- Matrices separate final pass rate from clean pass rate, churn, forbidden edits, and protocol compliance.
- Issue-derived knowledge remains evidence-only until local verification and review.
- Policies require evidence ids before becoming agent decision rules.

The research claim is narrower than "memory improves agents." The claim is that agent work should become inspectable experimental knowledge, and that accepted knowledge must be gated by provenance, failure taxonomy, and repeated evidence.

