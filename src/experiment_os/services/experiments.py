from uuid import uuid4

from sqlalchemy.orm import Session

from experiment_os.db.models import ExperimentRunResult
from experiment_os.domain.schemas import (
    BriefRequest,
    ExperimentConditionInput,
    ExperimentInput,
    RunEventInput,
    RunStartInput,
)
from experiment_os.repositories.experiments import ExperimentRepository
from experiment_os.repositories.runs import RunRepository
from experiment_os.services.briefs import BriefCompiler
from experiment_os.services.dependencies import DependencyResolver
from experiment_os.services.metrics import MetricsExtractor
from experiment_os.services.runs import RunRecorder
from experiment_os.services.seed import SeedService
from experiment_os.services.serialization import run_to_dict


DRIZZLE_EXPERIMENT_ID = "experiment.001-drizzle-brief"


class ExperimentRunner:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._experiments = ExperimentRepository(session)
        self._runs = RunRepository(session)
        self._recorder = RunRecorder(session)

    def seed_drizzle_experiment(self) -> dict:
        self._experiments.upsert_experiment(
            ExperimentInput(
                id=DRIZZLE_EXPERIMENT_ID,
                title="Drizzle Issue-Informed Work Brief",
                hypothesis=(
                    "Issue-informed MCP work briefs reduce stale-library and wrong-workaround "
                    "failures when a coding agent works on Drizzle migration/default-value problems."
                ),
                status="draft",
                metadata={
                    "path": "experiments/001-drizzle-brief",
                    "task_family": "drizzle_migration_defaults",
                    "primary_metric": "inspected_package_versions_before_edit",
                },
            )
        )
        conditions = [
            ExperimentConditionInput(
                id="condition.001-drizzle-baseline",
                experiment_id=DRIZZLE_EXPERIMENT_ID,
                name="baseline",
                description="Agent receives only the task prompt.",
                config={"brief_required": False},
            ),
            ExperimentConditionInput(
                id="condition.001-drizzle-brief-assisted",
                experiment_id=DRIZZLE_EXPERIMENT_ID,
                name="brief-assisted",
                description="Agent must load MCP work brief and dependencies before editing.",
                config={"brief_required": True},
            ),
        ]
        for condition in conditions:
            self._experiments.upsert_condition(condition)
        return {"experiment_id": DRIZZLE_EXPERIMENT_ID, "conditions": [item.id for item in conditions]}

    def run_drizzle_fixture(self) -> dict:
        SeedService(self._session).seed()
        self.seed_drizzle_experiment()
        results = [
            self._run_condition("condition.001-drizzle-baseline"),
            self._run_condition("condition.001-drizzle-brief-assisted"),
        ]
        return {"experiment_id": DRIZZLE_EXPERIMENT_ID, "results": results}

    def _run_condition(self, condition_id: str) -> dict:
        condition = self._experiments.get_condition(condition_id)
        if condition is None:
            raise ValueError(f"Unknown condition_id: {condition_id}")

        run = self._recorder.start_run(
            RunStartInput(
                task="Fix a Drizzle migration default-value issue after dependency update",
                repo="example/drizzle-app",
                agent="fixture-agent",
                model="fixture-model",
                toolchain="shell",
                metadata={
                    "experiment_id": DRIZZLE_EXPERIMENT_ID,
                    "condition_id": condition_id,
                    "condition": condition.name,
                },
            )
        )

        if condition.config.get("brief_required"):
            self._record_brief_assisted_events(run["run_id"])
        else:
            self._record_baseline_events(run["run_id"])

        events = self._runs.list_events(run["run_id"])
        metrics = MetricsExtractor().extract(events)
        report = {
            "condition": condition.name,
            "run": run_to_dict(self._runs.get_run(run["run_id"])),
            "metrics": metrics,
            "interpretation": _interpret(condition.name, metrics),
        }
        result = ExperimentRunResult(
            id=f"experiment-result.{uuid4().hex[:12]}",
            experiment_id=DRIZZLE_EXPERIMENT_ID,
            condition_id=condition.id,
            run_id=run["run_id"],
            metrics=metrics,
            report=report,
        )
        self._experiments.create_result(result)
        return report

    def _record_baseline_events(self, run_id: str) -> None:
        self._recorder.record_event(
            RunEventInput(
                run_id=run_id,
                event_type="file_inspected",
                payload={"path": "src/db/schema.ts", "reason": "start from schema"},
            )
        )
        self._recorder.record_event(
            RunEventInput(
                run_id=run_id,
                event_type="file_edited",
                payload={"path": "src/db/schema.ts", "reason": "attempt default fix"},
            )
        )
        self._recorder.record_event(
            RunEventInput(
                run_id=run_id,
                event_type="failure_observed",
                payload={
                    "failure_type": "stale_library_knowledge",
                    "severity": "medium",
                    "evidence": "edited schema before checking installed Drizzle versions",
                },
            )
        )
        self._recorder.record_event(
            RunEventInput(
                run_id=run_id,
                event_type="test_run",
                payload={"command": "npm run db:generate", "passed": False},
            )
        )

    def _record_brief_assisted_events(self, run_id: str) -> None:
        brief = BriefCompiler(self._session).compile(
            BriefRequest(
                task="Fix a Drizzle migration default-value issue after dependency update",
                repo="example/drizzle-app",
                libraries=["drizzle", "drizzle-orm"],
                agent="opencode",
                model="gemma",
                toolchain="shell",
            )
        )
        dependencies = DependencyResolver(self._session).resolve(brief["required_pages"], depth=2)
        self._recorder.record_event(
            RunEventInput(
                run_id=run_id,
                event_type="brief_loaded",
                payload={
                    "brief_id": brief["brief_id"],
                    "required_pages": brief["required_pages"],
                    "recommended_pages": brief["recommended_pages"],
                },
            )
        )
        self._recorder.record_event(
            RunEventInput(
                run_id=run_id,
                event_type="dependency_resolved",
                payload={
                    "root_pages": dependencies.root_pages,
                    "dependency_pages": [page["id"] for page in dependencies.pages],
                },
            )
        )
        self._recorder.record_event(
            RunEventInput(
                run_id=run_id,
                event_type="package_version_checked",
                payload={"package": "drizzle-orm", "version": "1.0.0-beta.22", "source": "package.json"},
            )
        )
        self._recorder.record_event(
            RunEventInput(
                run_id=run_id,
                event_type="file_inspected",
                payload={"path": "drizzle/migrations", "reason": "inspect migration conventions"},
            )
        )
        self._recorder.record_event(
            RunEventInput(
                run_id=run_id,
                event_type="file_edited",
                payload={"path": "src/db/schema.ts", "reason": "minimal version-aware fix"},
            )
        )
        self._recorder.record_event(
            RunEventInput(
                run_id=run_id,
                event_type="test_run",
                payload={"command": "npm run db:generate", "passed": True},
            )
        )


def _interpret(condition_name: str, metrics: dict) -> str:
    if condition_name == "brief-assisted":
        if (
            metrics["inspected_package_versions_before_edit"]
            and metrics["inspected_migration_conventions_before_edit"]
        ):
            return "Brief-assisted fixture performed the expected pre-edit checks."
        return "Brief-assisted fixture did not perform all expected pre-edit checks."

    if metrics["stale_api_usage_count"]:
        return "Baseline fixture reproduced stale-library behavior before version inspection."
    return "Baseline fixture did not reproduce the expected failure signal."
