# Codex Version-Trap Matrix

Date: 2026-04-27

Matrix id: `matrix.version-trap.16770fe51cc9`

Fixture: `fixtures/drizzle-version-trap-hard-repo`

Repeat count: `3`

Models: `codex-default`

## Runs

| Model | Repeat | Condition | Run | Exit | Duration |
| --- | ---: | --- | --- | ---: | ---: |
| codex-default | 0 | baseline | `run.50afd3ba7878` | 0 | 77.07s |
| codex-default | 0 | static_brief | `run.5174c9e9ae5f` | 0 | 55.55s |
| codex-default | 0 | mcp_brief | `run.d27d24cf4bf0` | 0 | 190.96s |
| codex-default | 1 | baseline | `run.e638637a4a77` | 0 | 55.40s |
| codex-default | 1 | static_brief | `run.a34d37a058f2` | 0 | 68.10s |
| codex-default | 1 | mcp_brief | `run.00fe4827fb10` | 0 | 157.48s |
| codex-default | 2 | baseline | `run.aa4d9e4fc9dc` | 0 | 67.61s |
| codex-default | 2 | static_brief | `run.d1c22ca769be` | 0 | 90.97s |
| codex-default | 2 | mcp_brief | `run.0a5b414ab19a` | 0 | 154.84s |

## Summary

### baseline

- run count: `3`
- tests passing rate: `1.00`
- test failure mean: `0.00`
- dependency change rate: `0.00`
- file edit mean: `1.00`
- wrong-file edit mean: `0.00`
- MCP pre-work rate: `0.00`
- MCP call mean: `0.00`

### mcp_brief

- run count: `3`
- tests passing rate: `1.00`
- test failure mean: `0.67`
- dependency change rate: `0.00`
- file edit mean: `1.00`
- wrong-file edit mean: `0.00`
- MCP pre-work rate: `1.00`
- MCP call mean: `11.00`

### static_brief

- run count: `3`
- tests passing rate: `1.00`
- test failure mean: `0.00`
- dependency change rate: `0.00`
- file edit mean: `1.00`
- wrong-file edit mean: `0.00`
- MCP pre-work rate: `0.00`
- MCP call mean: `0.00`

## Interpretation

- All 9 hard-fixture runs completed successfully and made the same minimal local edit:
  `src/db/schema.ts` gained `defaultNow()` for `users.createdAt`.
- No condition changed dependency versions, rewrote migration history, edited harness scripts, or produced wrong-file edits.
- Current Codex was strong enough to solve this fixture without Experiment OS context:
  baseline was `3/3`, static brief was `3/3`, and MCP brief was `3/3`.
- MCP added protocol evidence, not a correctness win in this matrix: `3/3` MCP runs called the
  pre-work protocol and resolved dependencies before the first edit, with `11.00` Experiment OS MCP
  calls on average.
- The apparent original `0.67` MCP test pass rate was a metric semantics bug. Run
  `run.00fe4827fb10` recorded failing pre-edit checks, then fixed the schema and recorded passing
  post-edit checks. This is a useful red-green trace, not a failed run.
- The cost signal is real: mean duration was about `66.69s` for baseline, `71.54s` for static brief,
  and `167.76s` for MCP brief.
- No policy candidate should be promoted from this matrix. The supported conclusion is narrower:
  Experiment OS currently improves observability and protocol compliance, while this fixture is too
  easy to demonstrate a correctness or safety lift for current Codex.

## Next Experiment Implication

Use a harder cross-agent matrix where the baseline actually has room to fail:

- weaker/open models via OpenCode or Aider;
- API-drift fixtures where stale issue knowledge is actively misleading;
- multi-file repair tasks where wrong-file edits, dependency edits, or premature completion are likely;
- the same MCP pre-work protocol, but with stricter measurement of final verification, observed
  red-green loops, dependency graph loading, and time cost.
