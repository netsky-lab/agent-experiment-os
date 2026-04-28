# OpenAI Python Responses API Issue-Ingestion Review

Date: 2026-04-28

Source snapshot: `research/issues/2026-04-28-openai-python-responses-api-migration.md`

## Review Decision

Keep the ingested issue-derived knowledge as `evidence_only`. Do not promote it to an accepted decision rule yet.

## Why

Issue ingestion is valuable because it captures real migration pain, workaround language, and failure vocabulary that docs often omit. But issues are not stable ground truth. They may contain stale SDK versions, partial reproductions, user-specific constraints, or advice that conflicts with the local repo's adapter layer.

For API-drift work, the correct workflow is:

1. Use issues to find likely failure modes and terms.
2. Inspect the local SDK shim or vendor wrapper.
3. Verify the installed package/API version.
4. Apply the smallest local edit.
5. Record the issue source as evidence, not as authority.

## Agent Contract

An agent may use this issue ingestion result to:

- search for migration symptoms
- identify candidate failure modes
- build reproduction checks
- propose interventions

An agent must not use it to:

- bypass local API inspection
- edit tests to fit the issue claim
- upgrade dependencies without local version evidence
- promote a policy candidate without reviewer evidence ids

## Product Implication

The dashboard should show issue-derived cards in the review queue with provenance and `allowed_use=evidence_only`. The MCP presentation should expose them under knowledge boundaries, so the agent knows the source exists but also knows it is not a decision rule.
