from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from experiment_os.db.models import Experiment, ExperimentCondition, ExperimentRunResult
from experiment_os.domain.schemas import ExperimentConditionInput, ExperimentInput


class ExperimentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert_experiment(self, data: ExperimentInput) -> Experiment:
        stmt = (
            insert(Experiment)
            .values(
                id=data.id,
                title=data.title,
                hypothesis=data.hypothesis,
                status=data.status,
                experiment_metadata=data.metadata,
            )
            .on_conflict_do_update(
                index_elements=[Experiment.id],
                set_={
                    "title": data.title,
                    "hypothesis": data.hypothesis,
                    "status": data.status,
                    "metadata": data.metadata,
                },
            )
            .returning(Experiment)
        )
        return self._session.execute(stmt).scalar_one()

    def upsert_condition(self, data: ExperimentConditionInput) -> ExperimentCondition:
        stmt = (
            insert(ExperimentCondition)
            .values(
                id=data.id,
                experiment_id=data.experiment_id,
                name=data.name,
                description=data.description,
                config=data.config,
            )
            .on_conflict_do_update(
                index_elements=[ExperimentCondition.id],
                set_={
                    "name": data.name,
                    "description": data.description,
                    "config": data.config,
                },
            )
            .returning(ExperimentCondition)
        )
        return self._session.execute(stmt).scalar_one()

    def get_experiment(self, experiment_id: str) -> Experiment | None:
        return self._session.get(Experiment, experiment_id)

    def get_condition(self, condition_id: str) -> ExperimentCondition | None:
        return self._session.get(ExperimentCondition, condition_id)

    def list_conditions(self, experiment_id: str) -> list[ExperimentCondition]:
        return self._session.scalars(
            select(ExperimentCondition)
            .where(ExperimentCondition.experiment_id == experiment_id)
            .order_by(ExperimentCondition.name)
        ).all()

    def create_result(self, result: ExperimentRunResult) -> ExperimentRunResult:
        self._session.add(result)
        self._session.flush()
        return result

    def list_results(self, experiment_id: str) -> list[ExperimentRunResult]:
        return self._session.scalars(
            select(ExperimentRunResult)
            .where(ExperimentRunResult.experiment_id == experiment_id)
            .order_by(ExperimentRunResult.created_at)
        ).all()
