from experiment_os.domain.schemas import RunEventInput, RunStartInput
from experiment_os.repositories.runs import RunRepository
from experiment_os.services.reports import RunReportGenerator
from experiment_os.services.runs import RunRecorder


def test_run_report_generator_renders_metrics_and_timeline(session):
    recorder = RunRecorder(session)
    run = recorder.start_run(
        RunStartInput(
            task="Task",
            repo="repo",
            agent="codex",
            model=None,
            toolchain="shell",
            metadata={},
        )
    )
    recorder.record_event(
        RunEventInput(
            run_id=run["run_id"],
            event_type="package_version_checked",
            payload={"package": "drizzle-orm", "version": "1.0.0-beta.22"},
        )
    )
    events = RunRepository(session).list_events(run["run_id"])

    report = RunReportGenerator().generate(
        condition_name="brief-assisted",
        run=run,
        metrics={"tests_passing": True},
        execution={"exit_code": 0, "duration_seconds": 1.25},
        events=events,
        artifacts={"transcript": "artifacts/run/transcript.md"},
    )

    assert report.data["condition"] == "brief-assisted"
    assert "`package_version_checked` drizzle-orm" in report.markdown
