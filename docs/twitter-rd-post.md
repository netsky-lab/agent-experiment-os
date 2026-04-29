# R&D Post Draft

Most "agent memory" products optimize for recall.

I think coding agents need something stricter: experimental knowledge.

The interesting object is not "remember this fact." It is:

hypothesis -> run -> failure -> metric movement -> interpretation -> intervention -> reviewed policy

We just added the first product loop to Agent Experiment OS:

- MCP work briefs with `must_load` and `dependsOn`
- GitHub issues ingested as evidence-only claims
- review gates before claims become policies
- clean pass tracked separately from final pass
- dashboard views for humans, but presentation contracts for agents

The key idea: a green run is not enough.

If an agent failed tests, repaired itself, and ended green, that is useful evidence only if the failed command, cause, and recovery are recorded.

Otherwise you are promoting luck into policy.
