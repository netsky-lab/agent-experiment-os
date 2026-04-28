from typing import Any

from sqlalchemy.orm import Session

from experiment_os.repositories.runs import RunRepository
from experiment_os.services.completion import CompletionContractService
from experiment_os.services.metrics import MetricsExtractor


class AgentActionService:
    """Decision helper for agents that need one concrete next protocol action."""

    def __init__(self, session: Session) -> None:
        self._runs = RunRepository(session)
        self._completion = CompletionContractService(session)

    def next_required_action(self, run_id: str) -> dict[str, Any]:
        run = self._runs.get_run(run_id)
        if run is None:
            raise ValueError(f"Unknown run_id: {run_id}")
        events = self._runs.list_events(run_id)
        metrics = MetricsExtractor().extract(events)
        event_types = [event.event_type for event in events]
        completion = self._completion.validate(run_id)

        if not metrics["mcp_pre_work_protocol_called"]:
            action = _action("start_pre_work_protocol", "Load Experiment OS pre-work context.")
        elif not metrics["mcp_dependencies_resolved_before_edit"]:
            action = _action("resolve_dependencies", "Load dependsOn graph before editing.")
        elif "decision_recorded" not in event_types and "file_edited" not in event_types:
            action = _action("record_decision", "Record intended change and evidence boundary.")
        elif "test_run" not in event_types:
            action = _action("run_tests", "Run the repository verification command.")
        elif not metrics["tests_passing"]:
            action = _action("fix_or_record_failure", "Fix failing verification or record blocker.")
        elif not metrics["mcp_final_answer_recorded"]:
            action = _action("complete_run", "Record final_answer through the MCP completion tool.")
        else:
            action = _action("none", "Completion contract satisfied.")

        return {
            "run_id": run_id,
            "next_action": action,
            "completion": completion,
            "metrics": metrics,
        }


def _action(action_id: str, reason: str) -> dict[str, str]:
    return {"id": action_id, "reason": reason}
