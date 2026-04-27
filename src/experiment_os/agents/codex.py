import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from experiment_os.agents.base import AgentExecutionResult, AgentRunRequest


@dataclass(frozen=True)
class CodexCliOptions:
    binary: str = "codex"
    model: str | None = None
    sandbox: str = "workspace-write"
    approval_policy: str = "never"
    json_events: bool = True
    skip_git_repo_check: bool = True
    experiment_os_mcp: bool = False
    extra_args: tuple[str, ...] = ()


class CodexCliAdapter:
    def __init__(self, options: CodexCliOptions | None = None) -> None:
        self._options = options or CodexCliOptions()

    def run(self, request: AgentRunRequest) -> AgentExecutionResult:
        prompt = request.prompt or request.command
        args = self._build_args(request.workdir)
        env = {**os.environ, **request.env}

        started = time.monotonic()
        completed = subprocess.run(
            args,
            input=prompt,
            cwd=request.workdir,
            env=env,
            text=True,
            capture_output=True,
            timeout=request.timeout_seconds,
            check=False,
        )
        duration = time.monotonic() - started
        return AgentExecutionResult(
            command=" ".join(args),
            workdir=request.workdir,
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
            duration_seconds=duration,
        )

    def _build_args(self, workdir: Path) -> list[str]:
        args = [
            self._options.binary,
        ]
        if self._options.approval_policy:
            args.extend(["--ask-for-approval", self._options.approval_policy])
        args.extend(
            [
                "exec",
                "--cd",
                str(workdir.resolve()),
                "--sandbox",
                self._options.sandbox,
            ]
        )
        if self._options.skip_git_repo_check:
            args.append("--skip-git-repo-check")
        if self._options.json_events:
            args.append("--json")
        if self._options.model:
            args.extend(["--model", self._options.model])
        if self._options.experiment_os_mcp:
            args.extend(_experiment_os_mcp_config_args())
        args.extend(self._options.extra_args)
        args.append("-")
        return args


def _experiment_os_mcp_config_args() -> list[str]:
    args = [
        "-c",
        'mcp_servers.experiment_os.command="uv"',
        "-c",
        'mcp_servers.experiment_os.args=["run","experiment-os","mcp","serve"]',
    ]
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        args.extend(["-c", f'mcp_servers.experiment_os.env.DATABASE_URL="{database_url}"'])
    return args
