from typing import Any

from sqlalchemy.orm import Session

from experiment_os.db.models import Experiment
from experiment_os.repositories.experiments import ExperimentRepository


ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"running", "archived"},
    "running": {"interpreted", "archived"},
    "interpreted": {"archived", "running"},
    "archived": set(),
}


class ExperimentLifecycleService:
    def __init__(self, session: Session) -> None:
        self._experiments = ExperimentRepository(session)

    def set_status(
        self,
        experiment_id: str,
        status: str,
        *,
        rationale: str | None = None,
    ) -> dict[str, Any]:
        experiment = self._experiments.get_experiment(experiment_id)
        if experiment is None:
            raise ValueError(f"Unknown experiment_id: {experiment_id}")
        current = experiment.status
        if status != current and status not in ALLOWED_TRANSITIONS.get(current, set()):
            raise ValueError(f"Invalid experiment status transition: {current} -> {status}")
        experiment.status = status
        metadata = dict(experiment.experiment_metadata)
        history = list(metadata.get("status_history", []))
        history.append({"from": current, "to": status, "rationale": rationale})
        metadata["status_history"] = history
        experiment.experiment_metadata = metadata
        return _experiment_dict(experiment)


def _experiment_dict(experiment: Experiment) -> dict[str, Any]:
    return {
        "id": experiment.id,
        "title": experiment.title,
        "hypothesis": experiment.hypothesis,
        "status": experiment.status,
        "metadata": experiment.experiment_metadata,
    }
