from experiment_os.domain.schemas import RunEventInput, RunStartInput
from experiment_os.services.runs import RunRecorder


def test_metrics_detect_pre_edit_checks(session):
    recorder = RunRecorder(session)
    run = recorder.start_run(RunStartInput(task="metrics test"))

    recorder.record_event(
        RunEventInput(
            run_id=run["run_id"],
            event_type="package_version_checked",
            payload={"package": "drizzle-orm", "version": "1.0.0-beta.22"},
        )
    )
    recorder.record_event(
        RunEventInput(
            run_id=run["run_id"],
            event_type="file_inspected",
            payload={"path": "drizzle/migrations", "reason": "migration conventions"},
        )
    )
    recorder.record_event(
        RunEventInput(
            run_id=run["run_id"],
            event_type="file_edited",
            payload={"path": "src/db/schema.ts"},
        )
    )

    summary = recorder.summarize_run(run["run_id"])

    assert summary["metrics"]["inspected_package_versions_before_edit"] is True
    assert summary["metrics"]["inspected_migration_conventions_before_edit"] is True

