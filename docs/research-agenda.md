# Research Agenda

Agent Experiment OS is a research repo for studying how agent work becomes reusable experimental knowledge.

Near-term questions:

- Can agent-facing `must_load` contracts reduce stale API and issue replay failures?
- Which failure classes predict bad policy promotion?
- When does red-green verification churn represent useful repair versus unreliable trial-and-error?
- How much issue evidence should be shown before it starts biasing an agent toward stale fixes?
- Can `dependsOn` graphs make agent memory auditable enough for review?

Product experiments:

- compare raw task prompts against MCP work briefs;
- compare issue evidence shown as prose versus source-backed claims;
- measure clean pass rate separately from final pass rate;
- require agents to record dependency resolution before edits;
- test policy promotion gates against saturated or churn-heavy matrices.

Artifacts to publish:

- matrix reports;
- failure taxonomy updates;
- intervention library updates;
- source-backed issue evidence case studies;
- protocol compliance versus task success analyses.
