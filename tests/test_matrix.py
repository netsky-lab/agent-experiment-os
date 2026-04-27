import os

from experiment_os.services.matrix import ExperimentMatrixRunner


def test_version_trap_matrix_runs_conditions_and_aggregates(session, tmp_path, monkeypatch):
    fake_codex = tmp_path / "codex"
    fake_codex.write_text(
        "#!/usr/bin/env bash\n"
        "cat >/dev/null\n"
        "if [[ \"$*\" == *mcp_servers.experiment_os.command* ]]; then\n"
        "  echo '{\"type\":\"item.completed\",\"item\":{\"type\":\"mcp_tool_call\","
        "\"server\":\"experiment_os\",\"tool\":\"start_pre_work_protocol\","
        "\"arguments\":{},\"status\":\"completed\"}}'\n"
        "  echo '{\"type\":\"item.completed\",\"item\":{\"type\":\"mcp_tool_call\","
        "\"server\":\"experiment_os\",\"tool\":\"resolve_dependencies\","
        "\"arguments\":{},\"status\":\"completed\"}}'\n"
        "  echo '{\"type\":\"item.completed\",\"item\":{\"type\":\"mcp_tool_call\","
        "\"server\":\"experiment_os\",\"tool\":\"record_run_event\","
        "\"arguments\":{\"run_id\":\"run.inner\",\"event_type\":\"final_answer\"},"
        "\"status\":\"completed\"}}'\n"
        "fi\n"
        "echo '{\"type\":\"exec_command.end\",\"cmd\":\"cat package.json\","
        "\"output\":\"\\\\\\\"drizzle-kit\\\\\\\": \\\\\\\"0.31.1\\\\\\\"\","
        "\"exit_code\":0}'\n"
        "echo '{\"type\":\"exec_command.end\",\"cmd\":\"rg migration drizzle/migrations\","
        "\"output\":\"drizzle/migrations/0001_initial.sql\",\"exit_code\":0}'\n"
        "echo '{\"type\":\"exec_command.end\",\"cmd\":\"npm run db:generate\","
        "\"output\":\"passed\",\"exit_code\":0}'\n"
        "echo '{\"type\":\"exec_command.end\",\"cmd\":\"npm test\","
        "\"output\":\"passed\",\"exit_code\":0}'\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")

    progress_events = []
    report = ExperimentMatrixRunner(session).run_version_trap_matrix(
        repeat_count=1,
        sandbox="danger-full-access",
        progress=progress_events.append,
        write_result_artifact=True,
        result_dir=tmp_path / "results",
    )

    assert report["repeat_count"] == 1
    assert report["models"] == ["codex-default"]
    assert {item["id"] for item in report["conditions"]} == {
        "baseline",
        "static_brief",
        "mcp_brief",
    }
    assert len(report["runs"]) == 3
    assert report["summary"]["mcp_brief"]["metrics"]["mcp_tool_call_count"]["mean"] == 3
    assert (
        report["summary"]["mcp_brief"]["metrics"]["mcp_pre_work_protocol_called"]["rate"]
        == 1
    )
    assert progress_events[0]["event"] == "matrix_started"
    assert progress_events[-1]["event"] == "matrix_finished"
    assert "result_artifact" in report
    assert (tmp_path / "results").exists()


def test_version_trap_matrix_can_skip_mcp_condition(session, tmp_path, monkeypatch):
    fake_codex = tmp_path / "codex"
    fake_codex.write_text(
        "#!/usr/bin/env bash\n"
        "cat >/dev/null\n"
        "echo '{\"type\":\"exec_command.end\",\"cmd\":\"npm test\","
        "\"output\":\"passed\",\"exit_code\":0}'\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")

    report = ExperimentMatrixRunner(session).run_version_trap_matrix(
        repeat_count=1,
        include_mcp=False,
    )

    assert {item["id"] for item in report["conditions"]} == {"baseline", "static_brief"}
    assert len(report["runs"]) == 2


def test_version_trap_matrix_can_run_multiple_models(session, tmp_path, monkeypatch):
    fake_codex = tmp_path / "codex"
    fake_codex.write_text(
        "#!/usr/bin/env bash\n"
        "cat >/dev/null\n"
        "echo '{\"type\":\"exec_command.end\",\"cmd\":\"npm test\","
        "\"output\":\"passed\",\"exit_code\":0}'\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")

    report = ExperimentMatrixRunner(session).run_version_trap_matrix(
        repeat_count=1,
        models=["model-a", "model-b"],
        include_mcp=False,
    )

    assert report["models"] == ["model-a", "model-b"]
    assert len(report["runs"]) == 4
    assert set(report["summary_by_model"]) == {"model-a", "model-b"}
