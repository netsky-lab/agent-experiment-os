import pytest

from experiment_os.services.experiment_lifecycle import ExperimentLifecycleService
from experiment_os.services.experiments import ExperimentRunner


def test_experiment_lifecycle_records_valid_transitions(session):
    ExperimentRunner(session).seed_drizzle_experiment()

    service = ExperimentLifecycleService(session)
    running = service.set_status(
        "experiment.001-drizzle-brief",
        "running",
        rationale="Matrix started.",
    )
    interpreted = service.set_status(
        "experiment.001-drizzle-brief",
        "interpreted",
        rationale="Results reviewed.",
    )

    assert running["status"] == "running"
    assert interpreted["status"] == "interpreted"
    assert interpreted["metadata"]["status_history"][-1]["rationale"] == "Results reviewed."


def test_experiment_lifecycle_rejects_invalid_transition(session):
    ExperimentRunner(session).seed_drizzle_experiment()

    with pytest.raises(ValueError, match="Invalid experiment status transition"):
        ExperimentLifecycleService(session).set_status(
            "experiment.001-drizzle-brief",
            "interpreted",
        )
