from pathlib import Path

from experiment_os.agents import (
    AgentRunRequest,
    AiderCliAdapter,
    AiderCliOptions,
    ExternalCliAdapter,
    ExternalCliOptions,
    OpenCodeCliAdapter,
    OpenCodeCliOptions,
)


def test_external_cli_adapter_can_send_prompt_on_stdin(tmp_path: Path):
    fake_agent = tmp_path / "agent"
    capture = tmp_path / "capture.txt"
    fake_agent.write_text(
        "#!/usr/bin/env bash\n"
        f"printf 'args=%s\\n' \"$*\" > {capture}\n"
        f"printf 'stdin=' >> {capture}\n"
        f"cat >> {capture}\n"
        "echo ok\n",
        encoding="utf-8",
    )
    fake_agent.chmod(0o755)

    result = ExternalCliAdapter(
        ExternalCliOptions(binary=str(fake_agent), args=("run",), prompt_mode="stdin")
    ).run(
        AgentRunRequest(
            command="agent run",
            workdir=tmp_path,
            prompt="load Experiment OS context",
        )
    )

    captured = capture.read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "args=run" in captured
    assert "stdin=load Experiment OS context" in captured


def test_aider_adapter_uses_message_flag_and_model(tmp_path: Path):
    fake_aider = tmp_path / "aider"
    capture = tmp_path / "capture.txt"
    fake_aider.write_text(
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$*\" > {capture}\n"
        "echo ok\n",
        encoding="utf-8",
    )
    fake_aider.chmod(0o755)

    result = AiderCliAdapter(
        AiderCliOptions(binary=str(fake_aider), model="openrouter/qwen", extra_args=())
    ).run(
        AgentRunRequest(
            command="aider",
            workdir=tmp_path,
            prompt="fix the wrapper",
        )
    )

    captured = capture.read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "--model openrouter/qwen" in captured
    assert "--message fix the wrapper" in captured


def test_opencode_adapter_uses_run_dir_json_and_prompt_argument(tmp_path: Path):
    fake_opencode = tmp_path / "opencode"
    capture = tmp_path / "capture.txt"
    fake_opencode.write_text(
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$*\" > {capture}\n"
        "echo '{\"type\":\"done\"}'\n",
        encoding="utf-8",
    )
    fake_opencode.chmod(0o755)

    result = OpenCodeCliAdapter(
        OpenCodeCliOptions(
            binary=str(fake_opencode),
            model="github-copilot/gpt-5.1-codex",
            dangerously_skip_permissions=True,
        )
    ).run(
        AgentRunRequest(
            command="opencode run",
            workdir=tmp_path,
            prompt="fix the wrapper",
        )
    )

    captured = capture.read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "run --format json" in captured
    assert f"--dir {tmp_path}" in captured
    assert "--model github-copilot/gpt-5.1-codex" in captured
    assert "--dangerously-skip-permissions" in captured
    assert captured.rstrip().endswith("fix the wrapper")
