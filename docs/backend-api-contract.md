# Backend API Contract

The dashboard should be built on top of backend use cases, not directly on database tables. The
first UI transport can be REST, MCP, or a server-rendered adapter, but it should expose the same
read shapes.

The current HTTP transport is `experiment-os api serve`, backed by `experiment_os.http_api`.

## Experiments List

Use case: `DashboardReadService.list_experiments()`

HTTP: `GET /experiments`

```json
{
  "experiments": [
    {
      "id": "experiment.001-drizzle-brief",
      "title": "Drizzle Issue-Informed Work Brief",
      "hypothesis": "...",
      "status": "draft",
      "metadata": {},
      "condition_count": 2,
      "result_count": 4,
      "created_at": "2026-04-27T00:00:00+00:00",
      "updated_at": "2026-04-27T00:00:00+00:00"
    }
  ]
}
```

## Experiment Detail

Use case: `DashboardReadService.experiment_detail(experiment_id)`

HTTP: `GET /experiments/{experiment_id}`

Contains the experiment, its conditions, and result reports. The UI can render this as hypothesis,
conditions, metric deltas, and run links.

## Experiment Matrix

Use case: `DashboardReadService.experiment_matrix(experiment_id)`

HTTP: `GET /experiments/{experiment_id}/matrix`

Groups repeated condition runs by `matrix_id` and `matrix_condition`. The first matrix view should
compare baseline, static brief, and MCP brief conditions across repeat counts.

## Run Detail

Use case: `DashboardReadService.run_detail(run_id)`

HTTP: `GET /runs/{run_id}`

```json
{
  "run": {},
  "timeline": [],
  "metrics": {},
  "artifacts": []
}
```

The timeline is the source of truth for agent behavior. Metrics are derived from timeline events.

## Review Queue

Use case: `DashboardReadService.review_queue(limit=50)`

HTTP: `GET /review-queue?limit=50`

Shows draft claims, knowledge cards, policies, and interventions that are evidence-only until
reviewed. The UI should make the review gate explicit: raw issue claims and generated policy
candidates are not accepted policy.

## Policy Candidates

Use case: `DashboardReadService.policy_candidates(limit=50)`

HTTP: `GET /policy-candidates?limit=50`

Shows generated draft policies that came from experiment results or promoted claims. These are the
main human review object before a candidate becomes an agent decision rule.

## Evidence Graph

The agent-facing graph is already emitted in `brief.content.agent_dependency_graph` and by MCP
`get_agent_dependency_graph`. The dashboard should visualize the same graph instead of inventing a
separate human-only model.

Use case: `DashboardReadService.evidence_graph(brief_id=...)`

HTTP: `GET /briefs/{brief_id}/evidence-graph`

```json
{
  "brief_id": "brief.x",
  "graph": {
    "version": "agent_dependency_graph.v1",
    "nodes": [],
    "edges": []
  },
  "legend": {}
}
```

## Agent Work Context

HTTP: `POST /briefs`

Compiles a work brief from a `BriefRequest` payload.

HTTP: `GET /briefs/{brief_id}/agent-work-context`

Returns the operational agent-facing presentation:

```json
{
  "version": "agent_work_context.v1",
  "required_load_order": [],
  "knowledge_boundaries": {},
  "required_checks": [],
  "forbidden_actions": [],
  "tool_sequence": [],
  "completion_contract": {}
}
```

This is the surface an agent or UI should use when it needs to know what must be loaded and verified
before work begins.

## Knowledge Search

HTTP: `POST /knowledge/search`

```json
{
  "query": "python api drift local shim",
  "libraries": ["example-llm-sdk"],
  "page_types": ["knowledge_card"],
  "status": "accepted",
  "limit": 8
}
```

HTTP: `POST /issue-knowledge/search`

Searches source, claim, and knowledge-card pages for a library/topic pair. This endpoint includes
draft claims because issue-derived claims are useful evidence even before review.

## Review Actions

Use case: `DashboardReadService.review_actions(page_id)`

HTTP: `GET /review-actions/{page_id}`

For draft claims, the UI can show actions for:

- accept/reject status change
- promote to knowledge card
- promote to policy
- promote to intervention

Review actions are command intents. The UI should call the review service/transport adapter rather
than mutating wiki tables directly.

HTTP command endpoints:

- `POST /review-actions/{page_id}/status`
- `POST /claims/{claim_id}/promote/knowledge`
- `POST /claims/{claim_id}/promote/policy`
- `POST /claims/{claim_id}/promote/intervention`

Status updates accept a rationale:

```json
{
  "status": "accepted",
  "rationale": "Repeated matrix evidence supports this policy.",
  "reviewer": "maintainer"
}
```
