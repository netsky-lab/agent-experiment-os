from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from experiment_os.db.models import Run, RunArtifact, RunEvent
from experiment_os.domain.schemas import RunArtifactInput, RunEventInput, RunStartInput


class RunRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_run(self, run_id: str, data: RunStartInput) -> Run:
        run = Run(
            id=run_id,
            task=data.task,
            repo=data.repo,
            agent=data.agent,
            model=data.model,
            toolchain=data.toolchain,
            run_metadata=data.metadata,
        )
        self._session.add(run)
        self._session.flush()
        return run

    def get_run(self, run_id: str) -> Run | None:
        return self._session.get(Run, run_id)

    def next_step_index(self, run_id: str) -> int:
        value = self._session.scalar(
            select(func.coalesce(func.max(RunEvent.step_index), -1)).where(RunEvent.run_id == run_id)
        )
        return int(value) + 1

    def append_event(self, data: RunEventInput) -> RunEvent:
        step_index = data.step_index
        if step_index is None:
            step_index = self.next_step_index(data.run_id)
        event = RunEvent(
            run_id=data.run_id,
            step_index=step_index,
            event_type=data.event_type,
            payload=data.payload,
        )
        self._session.add(event)
        self._session.flush()
        return event

    def list_events(self, run_id: str) -> list[RunEvent]:
        return self._session.scalars(
            select(RunEvent).where(RunEvent.run_id == run_id).order_by(RunEvent.step_index)
        ).all()

    def add_artifact(self, artifact_id: str, data: RunArtifactInput) -> RunArtifact:
        artifact = RunArtifact(
            id=artifact_id,
            run_id=data.run_id,
            artifact_type=data.artifact_type,
            path=data.path,
            content_type=data.content_type,
            artifact_metadata=data.metadata,
        )
        self._session.add(artifact)
        self._session.flush()
        return artifact

    def list_artifacts(self, run_id: str) -> list[RunArtifact]:
        return self._session.scalars(
            select(RunArtifact).where(RunArtifact.run_id == run_id).order_by(RunArtifact.created_at)
        ).all()

    def event_exists(self, event_id: UUID) -> bool:
        return self._session.get(RunEvent, event_id) is not None
