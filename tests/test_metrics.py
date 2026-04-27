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


def test_metrics_detect_version_trap_dependency_edit(session):
    recorder = RunRecorder(session)
    run = recorder.start_run(RunStartInput(task="version trap metrics test"))

    recorder.record_event(
        RunEventInput(
            run_id=run["run_id"],
            event_type="package_version_checked",
            payload={"package": "drizzle-kit", "version": "0.31.1"},
        )
    )
    recorder.record_event(
        RunEventInput(
            run_id=run["run_id"],
            event_type="file_edited",
            payload={"path": "/tmp/repo/package.json"},
        )
    )

    summary = recorder.summarize_run(run["run_id"])

    assert summary["metrics"]["dependency_changed"] is True
    assert summary["metrics"]["blind_issue_version_alignment"] is True
    assert summary["metrics"]["preserved_local_version_constraint"] is False


def test_metrics_count_harness_script_edits_as_wrong_file_edits(session):
    recorder = RunRecorder(session)
    run = recorder.start_run(RunStartInput(task="wrong edit metrics test"))

    recorder.record_event(
        RunEventInput(
            run_id=run["run_id"],
            event_type="file_edited",
            payload={
                "path": (
                    "/workspace/artifacts/workdirs/condition-001-drizzle-baseline/scripts/test.js"
                )
            },
        )
    )

    summary = recorder.summarize_run(run["run_id"])

    assert summary["metrics"]["wrong_file_edits"] == 1


def test_metrics_detect_mcp_pre_work_protocol(session):
    recorder = RunRecorder(session)
    run = recorder.start_run(RunStartInput(task="mcp metrics test"))

    recorder.record_event(
        RunEventInput(
            run_id=run["run_id"],
            event_type="mcp_tool_called",
            payload={"tool": "list_mcp_resources", "server": "codex"},
        )
    )
    recorder.record_event(
        RunEventInput(
            run_id=run["run_id"],
            event_type="mcp_tool_called",
            payload={"tool": "start_pre_work_protocol", "server": "experiment_os"},
        )
    )
    recorder.record_event(
        RunEventInput(
            run_id=run["run_id"],
            event_type="mcp_tool_called",
            payload={"tool": "resolve_dependencies", "server": "experiment_os"},
        )
    )
    recorder.record_event(
        RunEventInput(
            run_id=run["run_id"],
            event_type="mcp_tool_called",
            payload={
                "tool": "record_run_event",
                "recorded_event_type": "final_answer",
                "server": "experiment_os",
            },
        )
    )
    recorder.record_event(
        RunEventInput(
            run_id=run["run_id"],
            event_type="mcp_tool_called",
            payload={"tool": "summarize_run", "server": "experiment_os"},
        )
    )

    summary = recorder.summarize_run(run["run_id"])

    assert summary["metrics"]["mcp_tool_call_count"] == 4
    assert summary["metrics"]["mcp_pre_work_protocol_called"] is True
    assert summary["metrics"]["mcp_dependencies_resolved_before_edit"] is True
    assert summary["metrics"]["mcp_final_answer_recorded"] is True
    assert summary["metrics"]["mcp_summary_requested"] is True
