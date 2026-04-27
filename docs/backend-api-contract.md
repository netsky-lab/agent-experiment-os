# Backend API Contract

The dashboard should be built on top of backend use cases, not directly on database tables. The
first UI transport can be REST, MCP, or a server-rendered adapter, but it should expose the same
read shapes.

## Experiments List

Use case: `DashboardReadService.list_experiments()`

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

Contains the experiment, its conditions, and result reports. The UI can render this as hypothesis,
conditions, metric deltas, and run links.

## Run Detail

Use case: `DashboardReadService.run_detail(run_id)`

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

Shows draft claims and knowledge cards that are evidence-only until reviewed. The UI should make the
review gate explicit: raw issue claims are not policy.

## Evidence Graph

The agent-facing graph is already emitted in `brief.content.agent_dependency_graph` and by MCP
`get_agent_dependency_graph`. The dashboard should visualize the same graph instead of inventing a
separate human-only model.

Use case: `DashboardReadService.evidence_graph(brief_id=...)`

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

## Review Actions

Use case: `DashboardReadService.review_actions(page_id)`

For draft claims, the UI can show actions for:

- accept/reject status change
- promote to knowledge card
- promote to policy
- promote to intervention

Review actions are command intents. The UI should call the review service/transport adapter rather
than mutating wiki tables directly.
