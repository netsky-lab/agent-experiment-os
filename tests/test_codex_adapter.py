from pathlib import Path

from experiment_os.agents import AgentRunRequest, CodexCliAdapter, CodexCliOptions


def test_codex_cli_adapter_invokes_exec_with_stdin_prompt(tmp_path: Path):
    fake_codex = tmp_path / "codex"
    capture = tmp_path / "capture.txt"
    fake_codex.write_text(
        "#!/usr/bin/env bash\n"
        f"printf 'args=%s\\n' \"$*\" > {capture}\n"
        f"printf 'stdin=' >> {capture}\n"
        f"cat >> {capture}\n"
        "echo '{\"event\":\"done\"}'\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)

    result = CodexCliAdapter(CodexCliOptions(binary=str(fake_codex))).run(
        AgentRunRequest(
            command="codex exec",
            workdir=tmp_path,
            prompt="Use Experiment OS brief before editing.",
        )
    )

    captured = capture.read_text(encoding="utf-8")
    assert result.exit_code == 0
    assert "exec --cd" in captured
    assert "--json" in captured
    assert "stdin=Use Experiment OS brief before editing." in captured

