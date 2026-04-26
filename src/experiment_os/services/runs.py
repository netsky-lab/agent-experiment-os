from uuid import uuid4

from sqlalchemy.orm import Session

from experiment_os.domain.schemas import RunEventInput, RunStartInput
from experiment_os.repositories.runs import RunRepository
from experiment_os.services.metrics import MetricsExtractor
from experiment_os.services.serialization import event_to_dict, run_to_dict


class RunRecorder:
    def __init__(self, session: Session) -> None:
        self._runs = RunRepository(session)

    def start_run(self, data: RunStartInput) -> dict:
        run = self._runs.create_run(f"run.{uuid4().hex[:12]}", data)
        return run_to_dict(run)

    def record_event(self, data: RunEventInput) -> dict:
        if self._runs.get_run(data.run_id) is None:
            raise ValueError(f"Unknown run_id: {data.run_id}")
        event = self._runs.append_event(data)
        return event_to_dict(event)

    def summarize_run(self, run_id: str) -> dict:
        run = self._runs.get_run(run_id)
        if run is None:
            raise ValueError(f"Unknown run_id: {run_id}")
        events = self._runs.list_events(run_id)
        return {
            "run": run_to_dict(run),
            "event_count": len(events),
            "events": [event_to_dict(event) for event in events],
            "metrics": MetricsExtractor().extract(events),
        }
