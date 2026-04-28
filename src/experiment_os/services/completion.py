from typing import Any

from sqlalchemy.orm import Session

from experiment_os.repositories.runs import RunRepository
from experiment_os.services.metrics import MetricsExtractor


class CompletionContractService:
    def __init__(self, session: Session) -> None:
        self._runs = RunRepository(session)

    def validate(self, run_id: str) -> dict[str, Any]:
        run = self._runs.get_run(run_id)
        if run is None:
            raise ValueError(f"Unknown run_id: {run_id}")
        events = self._runs.list_events(run_id)
        metrics = MetricsExtractor().extract(events)
        event_types = [event.event_type for event in events]
        violations: list[str] = []

        if not metrics["mcp_pre_work_protocol_called"]:
            violations.append("pre_work_missing")
        if not metrics["mcp_dependencies_resolved_before_edit"]:
            violations.append("dependencies_not_loaded_before_edit")
        if "test_run" not in event_types:
            violations.append("test_run_missing")
        if not metrics["tests_passing"]:
            violations.append("tests_not_passing")
        if not metrics["mcp_final_answer_recorded"]:
            violations.append("final_answer_not_recorded")

        return {
            "run_id": run_id,
            "status": "passed" if not violations else "failed",
            "violations": violations,
            "metrics": metrics,
            "required": [
                "pre_work",
                "dependencies_before_edit",
                "test_run",
                "passing_tests",
                "final_answer_recorded",
            ],
        }
