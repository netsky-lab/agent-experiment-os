import pytest

from experiment_os.services.experiments import ExperimentRunner


def test_drizzle_fixture_produces_baseline_and_brief_metrics(session):
    result = ExperimentRunner(session).run_drizzle_fixture()
    by_condition = {item["condition"]: item for item in result["results"]}

    assert by_condition["baseline"]["metrics"]["stale_api_usage_count"] == 1
    assert by_condition["baseline"]["metrics"]["inspected_package_versions_before_edit"] is False
    assert by_condition["brief-assisted"]["metrics"]["inspected_package_versions_before_edit"] is True
    assert by_condition["brief-assisted"]["metrics"]["tests_passing"] is True


def test_shell_condition_captures_artifacts_and_metrics(session, tmp_path):
    result = ExperimentRunner(session).run_shell_condition(
        condition_id="condition.001-drizzle-brief-assisted",
        command=(
            "printf 'brief=%s\\n' \"$EXPERIMENT_OS_BRIEF_PATH\"; "
            "echo 'drizzle-orm@1.0.0-beta.22'; "
            "echo 'rg migration drizzle/migrations'; "
            "echo 'modified src/db/schema.ts'; "
            "echo 'npm run db:generate passed'"
        ),
        workdir=tmp_path,
    )

    assert result["execution"]["exit_code"] == 0
    assert result["metrics"]["inspected_package_versions_before_edit"] is True
    assert result["metrics"]["tests_passing"] is True
    assert result["artifacts"]["transcript"].endswith("transcript.md")


def test_codex_condition_uses_fake_codex_binary(session, tmp_path, monkeypatch):
    fake_codex = tmp_path / "codex"
    fake_codex.write_text(
        "#!/usr/bin/env bash\n"
        "cat >/dev/null\n"
        "echo 'drizzle-orm@1.0.0-beta.22'\n"
        "echo 'rg migration drizzle/migrations'\n"
        "echo 'modified src/db/schema.ts'\n"
        "echo 'npm run db:generate passed'\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}:{__import__('os').environ['PATH']}")

    result = ExperimentRunner(session).run_codex_condition(
        condition_id="condition.001-drizzle-brief-assisted",
        prompt="Fix Drizzle migration issue.",
        workdir=tmp_path,
    )

    assert result["execution"]["exit_code"] == 0
    assert result["metrics"]["inspected_package_versions_before_edit"] is True
    assert result["metrics"]["tests_passing"] is True


def test_codex_condition_can_enforce_adapter_pre_work_gate(session, tmp_path, monkeypatch):
    fake_codex = tmp_path / "codex"
    capture = tmp_path / "prompt.txt"
    fake_codex.write_text(
        "#!/usr/bin/env bash\n"
        f"cat > {capture}\n"
        "echo '{\"type\":\"item.completed\",\"item\":{\"type\":\"agent_message\","
        "\"text\":\"done\"}}'\n"
        "echo '{\"type\":\"exec_command.end\",\"cmd\":\"python -m pytest\","
        "\"output\":\"passed\",\"exit_code\":0}'\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}:{__import__('os').environ['PATH']}")

    result = ExperimentRunner(session).run_codex_condition(
        condition_id="condition.002-api-drift-brief-assisted",
        prompt="Fix Python API drift.",
        workdir=tmp_path,
        brief_task="Fix a Python SDK/API drift wrapper issue",
        brief_libraries=["example-llm-sdk", "python"],
        pre_work_gate=True,
    )

    prompt = capture.read_text(encoding="utf-8")
    assert "Experiment OS Enforced Pre-work Context" in prompt
    assert "agent_work_context.v1" in prompt
    assert result["metrics"]["mcp_pre_work_protocol_called"] is True
    assert result["metrics"]["mcp_dependency_graph_loaded"] is True
    assert result["metrics"]["mcp_dependencies_resolved_before_edit"] is True
    assert result["metrics"]["mcp_final_answer_recorded"] is True
    assert result["metrics"]["mcp_summary_requested"] is True


def test_adapter_pre_work_gate_rejects_completion_without_test_run(session, tmp_path, monkeypatch):
    fake_codex = tmp_path / "codex"
    fake_codex.write_text(
        "#!/usr/bin/env bash\n"
        "cat >/dev/null\n"
        "echo '{\"type\":\"item.completed\",\"item\":{\"type\":\"agent_message\","
        "\"text\":\"done without verification\"}}'\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}:{__import__('os').environ['PATH']}")

    with pytest.raises(ValueError, match="test_run_missing"):
        ExperimentRunner(session).run_codex_condition(
            condition_id="condition.002-api-drift-brief-assisted",
            prompt="Fix Python API drift.",
            workdir=tmp_path,
            brief_task="Fix a Python SDK/API drift wrapper issue",
            brief_libraries=["example-llm-sdk", "python"],
            pre_work_gate=True,
        )
