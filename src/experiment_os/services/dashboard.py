from typing import Any

from sqlalchemy.orm import Session

from experiment_os.repositories.experiments import ExperimentRepository
from experiment_os.repositories.briefs import BriefRepository
from experiment_os.repositories.runs import RunRepository
from experiment_os.repositories.wiki import WikiRepository
from experiment_os.services.protocol import AgentWorkProtocol
from experiment_os.services.metrics import MetricsExtractor
from experiment_os.services.review import ReviewService
from experiment_os.services.serialization import artifact_to_dict, event_to_dict, run_to_dict


class DashboardReadService:
    """Backend read contract for the future product UI."""

    def __init__(self, session: Session) -> None:
        self._experiments = ExperimentRepository(session)
        self._briefs = BriefRepository(session)
        self._runs = RunRepository(session)
        self._review = ReviewService(session)
        self._wiki = WikiRepository(session)
        self._protocol = AgentWorkProtocol(session)

    def list_experiments(self) -> dict[str, Any]:
        experiments = []
        for experiment in self._experiments.list_experiments():
            conditions = self._experiments.list_conditions(experiment.id)
            results = self._experiments.list_results(experiment.id)
            experiments.append(
                {
                    "id": experiment.id,
                    "title": experiment.title,
                    "hypothesis": experiment.hypothesis,
                    "status": experiment.status,
                    "metadata": experiment.experiment_metadata,
                    "condition_count": len(conditions),
                    "result_count": len(results),
                    "created_at": experiment.created_at.isoformat() if experiment.created_at else None,
                    "updated_at": experiment.updated_at.isoformat() if experiment.updated_at else None,
                }
            )
        return {"experiments": experiments}

    def experiment_detail(self, experiment_id: str) -> dict[str, Any]:
        experiment = self._experiments.get_experiment(experiment_id)
        if experiment is None:
            raise ValueError(f"Unknown experiment_id: {experiment_id}")
        conditions = self._experiments.list_conditions(experiment_id)
        results = self._experiments.list_results(experiment_id)
        return {
            "experiment": {
                "id": experiment.id,
                "title": experiment.title,
                "hypothesis": experiment.hypothesis,
                "status": experiment.status,
                "metadata": experiment.experiment_metadata,
            },
            "conditions": [
                {
                    "id": condition.id,
                    "name": condition.name,
                    "description": condition.description,
                    "config": condition.config,
                }
                for condition in conditions
            ],
            "results": [
                {
                    "id": result.id,
                    "condition_id": result.condition_id,
                    "run_id": result.run_id,
                    "metrics": result.metrics,
                    "report": result.report,
                    "created_at": result.created_at.isoformat() if result.created_at else None,
                }
                for result in results
            ],
        }

    def run_detail(self, run_id: str) -> dict[str, Any]:
        run = self._runs.get_run(run_id)
        if run is None:
            raise ValueError(f"Unknown run_id: {run_id}")
        events = self._runs.list_events(run_id)
        artifacts = self._runs.list_artifacts(run_id)
        return {
            "run": run_to_dict(run),
            "timeline": [event_to_dict(event) for event in events],
            "metrics": MetricsExtractor().extract(events),
            "artifacts": [artifact_to_dict(artifact) for artifact in artifacts],
        }

    def review_queue(self, *, limit: int = 50) -> dict[str, Any]:
        return {"items": self._review.review_queue(limit=limit)}

    def evidence_graph(self, *, brief_id: str) -> dict[str, Any]:
        brief = self._briefs.get(brief_id)
        if brief is None:
            raise ValueError(f"Unknown brief_id: {brief_id}")
        graph = self._protocol.agent_graph_for_brief(brief_id)
        return {
            "brief_id": brief_id,
            "graph": graph,
            "legend": {
                "decision_rule": "Accepted or draft policy that may become an agent rule after review.",
                "intervention": "Action that mitigates a known failure mode.",
                "failure_mode": "Failure taxonomy node.",
                "domain_knowledge": "Library or repo-specific knowledge.",
                "evidence": "Source-backed claim or raw source; verify locally before acting.",
            },
        }

    def review_actions(self, page_id: str) -> dict[str, Any]:
        page = self._wiki.get_page(page_id)
        if page is None:
            raise ValueError(f"Unknown page_id: {page_id}")
        actions: list[dict[str, Any]] = []
        if page.status == "draft":
            actions.extend(
                [
                    {"id": "accept", "label": "Accept", "target_status": "accepted"},
                    {"id": "reject", "label": "Reject", "target_status": "rejected"},
                ]
            )
        if page.type == "claim":
            actions.extend(
                [
                    {"id": "promote_knowledge", "label": "Promote to knowledge card"},
                    {"id": "promote_policy", "label": "Promote to policy"},
                    {"id": "promote_intervention", "label": "Promote to intervention"},
                ]
            )
        return {
            "page": {
                "id": page.id,
                "type": page.type,
                "status": page.status,
                "title": page.title,
                "metadata": page.page_metadata,
            },
            "actions": actions,
        }
