# Agent Work Context

`agent_work_context.v1` is the primary product surface for agents. It is returned by
`start_pre_work_protocol`, and can also be fetched with `get_agent_work_context` or
`GET /briefs/{brief_id}/agent-work-context`.

The goal is to present knowledge as operational guidance, not as a memory dump.

## Shape

```json
{
  "version": "agent_work_context.v1",
  "brief_id": "brief.x",
  "run_id": "run.x",
  "required_load_order": ["knowledge.python-api-drift-local-shim"],
  "knowledge_boundaries": {
    "decision_capable": ["intervention.local-api-surface-first"],
    "domain_context": ["knowledge.python-api-drift-local-shim"],
    "evidence_only": ["claim.issue.example-llm-sdk.upgrade-advice"]
  },
  "required_checks": [
    "Inspect agent_client/vendor_sdk.py before editing agent_client/client.py."
  ],
  "forbidden_actions": [
    "Do not edit tests, vendor shims, dependency metadata, or migration history unless local evidence requires it."
  ],
  "tool_sequence": [],
  "completion_contract": {}
}
```

## Semantics

- `required_load_order`: pages the agent must read before the first edit.
- `knowledge_boundaries.decision_capable`: accepted policies/interventions that may affect action.
- `knowledge_boundaries.domain_context`: accepted knowledge cards that describe local risk.
- `knowledge_boundaries.evidence_only`: claims and sources that must be verified locally.
- `required_checks`: local facts that should be inspected and recorded.
- `forbidden_actions`: actions that require explicit local proof.
- `completion_contract`: final-answer guardrails.

This lets Experiment OS measure whether an agent loaded knowledge, respected boundaries, verified
local facts, and reported final verification.
