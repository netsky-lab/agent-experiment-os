# Product Dashboard

The Next.js dashboard is a product workbench for two audiences:

- humans review experiment state, failure evidence, policy candidates, and knowledge health;
- agents consume the agent-facing contract: `must_load`, `dependsOn`, decision rules, evidence boundaries, and required checks.

Current views:

- `Experiments`: seeded experiment matrix overview and latest story.
- `Runs`: churn-oriented review queue for failed verification, forbidden edits, and wrong-file edits.
- `Agent Contract`: demo agent presentation contract with must-load pages and dependency edges.
- `Review Queue`: accept/reject actions with rationale and evidence ids.
- `Issue Evidence`: GitHub issue ingestion into source-backed, evidence-only claims.
- `Issue Evidence`: local version alignment and claim promotion into draft knowledge, policy, or intervention pages.
- `Knowledge Graph`: wiki pages and edge read model.
- `Knowledge Health`: stale and duplicate knowledge candidates.

The dashboard intentionally keeps issue text out of direct instructions. Issue ingestion creates source pages and low-confidence claims. Promotion to policies or interventions stays draft until review records rationale and provenance.
