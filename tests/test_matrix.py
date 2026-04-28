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
        "\"output\":\"failed\",\"exit_code\":1}'\n"
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
    artifact = next((tmp_path / "results").glob("*.md"))
    text = artifact.read_text(encoding="utf-8")
    assert "## Interpretation" in text
    assert "## Policy Decision" in text
    assert "red-green churn" in text
    assert "Interpretation Scaffold" not in text


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


def test_api_drift_matrix_runs_python_fixture_conditions(session, tmp_path, monkeypatch):
    fake_codex = tmp_path / "codex"
    fake_codex.write_text(
        "#!/usr/bin/env bash\n"
        "cat >/dev/null\n"
        "if [[ \"$*\" == *mcp_servers.experiment_os.command* ]]; then\n"
        "  echo '{\"type\":\"item.completed\",\"item\":{\"type\":\"mcp_tool_call\","
        "\"server\":\"experiment_os\",\"tool\":\"start_pre_work_protocol\","
        "\"arguments\":{},\"status\":\"completed\"}}'\n"
        "fi\n"
        "echo '{\"type\":\"exec_command.end\",\"cmd\":\"sed -n 1,80p agent_client/vendor_sdk.py\","
        "\"output\":\"def responses_create\",\"exit_code\":0}'\n"
        "echo '{\"type\":\"file_change\",\"changes\":[{\"path\":\"agent_client/client.py\","
        "\"kind\":\"modify\"}]}'\n"
        "echo '{\"type\":\"exec_command.end\",\"cmd\":\"python -m pytest\","
        "\"output\":\"passed\",\"exit_code\":0}'\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")

    report = ExperimentMatrixRunner(session).run_api_drift_matrix(
        repeat_count=1,
        sandbox="danger-full-access",
        include_mcp=True,
    )

    assert report["matrix_kind"] == "api_drift"
    assert report["experiment_id"] == "experiment.002-python-api-drift"
    assert len(report["runs"]) == 3
    assert report["summary"]["baseline"]["metrics"]["tests_passing"]["rate"] == 1
    assert report["summary"]["baseline"]["metrics"]["wrong_file_edits"]["mean"] == 0


def test_api_drift_matrix_can_include_adapter_gated_condition(session, tmp_path, monkeypatch):
    fake_codex = tmp_path / "codex"
    fake_codex.write_text(
        "#!/usr/bin/env bash\n"
        "cat >/dev/null\n"
        "echo '{\"type\":\"exec_command.end\",\"cmd\":\"python -m pytest\","
        "\"output\":\"passed\",\"exit_code\":0}'\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")

    report = ExperimentMatrixRunner(session).run_api_drift_matrix(
        repeat_count=1,
        include_mcp=False,
        include_gated=True,
    )

    assert {item["id"] for item in report["conditions"]} == {
        "baseline",
        "static_brief",
        "gated_brief",
    }
    assert report["summary"]["gated_brief"]["metrics"]["mcp_pre_work_protocol_called"][
        "rate"
    ] == 1
    assert report["summary"]["gated_brief"]["metrics"]["mcp_summary_requested"]["rate"] == 1


def test_api_drift_matrix_can_include_opencode_gated_condition(session, tmp_path, monkeypatch):
    fake_codex = tmp_path / "codex"
    fake_codex.write_text(
        "#!/usr/bin/env bash\n"
        "cat >/dev/null\n"
        "echo '{\"type\":\"exec_command.end\",\"cmd\":\"python -m pytest\","
        "\"output\":\"passed\",\"exit_code\":0}'\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)
    fake_opencode = tmp_path / "opencode"
    fake_opencode.write_text(
        "#!/usr/bin/env bash\n"
        "echo \"$*\" > opencode-args.txt\n"
        "echo '{\"type\":\"tool_use\",\"part\":{\"type\":\"tool\",\"tool\":\"bash\","
        "\"state\":{\"status\":\"completed\",\"input\":{\"command\":\"python -m pytest\"},"
        "\"metadata\":{\"exit\":0}}}}'\n",
        encoding="utf-8",
    )
    fake_opencode.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")

    report = ExperimentMatrixRunner(session).run_api_drift_matrix(
        repeat_count=1,
        include_mcp=False,
        include_opencode=True,
    )

    assert "opencode_gated_brief" in {item["id"] for item in report["conditions"]}
    assert report["summary"]["opencode_gated_brief"]["metrics"][
        "mcp_pre_work_protocol_called"
    ]["rate"] == 1
    assert report["summary"]["opencode_gated_brief"]["metrics"]["tests_passing"]["rate"] == 1
