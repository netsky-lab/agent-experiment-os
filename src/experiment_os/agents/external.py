import os
import shlex
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from experiment_os.agents.base import AgentExecutionResult, AgentRunRequest


PromptMode = Literal["stdin", "argument", "flag_argument", "none"]


@dataclass(frozen=True)
class ExternalCliOptions:
    binary: str
    args: tuple[str, ...] = ()
    extra_args: tuple[str, ...] = ()
    env: dict[str, str] = field(default_factory=dict)
    prompt_mode: PromptMode = "stdin"
    prompt_flag: str | None = None
    workdir_flag: str | None = None


class ExternalCliAdapter:
    """Configurable adapter for agent CLIs that can run a single prompted task."""

    def __init__(self, options: ExternalCliOptions) -> None:
        self._options = options

    def run(self, request: AgentRunRequest) -> AgentExecutionResult:
        prompt = request.prompt or request.command
        args = self._build_args(request.workdir, prompt)
        stdin = prompt if self._options.prompt_mode == "stdin" else None
        env = {**os.environ, **self._options.env, **request.env}

        started = time.monotonic()
        completed = subprocess.run(
            args,
            input=stdin,
            cwd=request.workdir,
            env=env,
            text=True,
            capture_output=True,
            timeout=request.timeout_seconds,
            check=False,
        )
        duration = time.monotonic() - started
        return AgentExecutionResult(
            command=shlex.join(args),
            workdir=request.workdir,
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
            duration_seconds=duration,
        )

    def _build_args(self, workdir: Path, prompt: str) -> list[str]:
        args = [self._options.binary, *self._options.args]
        if self._options.workdir_flag:
            args.extend([self._options.workdir_flag, str(workdir.resolve())])
        args.extend(self._options.extra_args)
        if self._options.prompt_mode == "argument":
            args.append(prompt)
        elif self._options.prompt_mode == "flag_argument":
            if not self._options.prompt_flag:
                raise ValueError("prompt_flag is required for flag_argument prompt mode")
            args.extend([self._options.prompt_flag, prompt])
        return args


@dataclass(frozen=True)
class AiderCliOptions:
    binary: str = "aider"
    model: str | None = None
    extra_args: tuple[str, ...] = ("--yes-always", "--no-auto-commits")
    env: dict[str, str] = field(default_factory=dict)


class AiderCliAdapter(ExternalCliAdapter):
    def __init__(self, options: AiderCliOptions | None = None) -> None:
        options = options or AiderCliOptions()
        args = []
        if options.model:
            args.extend(["--model", options.model])
        super().__init__(
            ExternalCliOptions(
                binary=options.binary,
                args=tuple(args),
                extra_args=options.extra_args,
                env=options.env,
                prompt_mode="flag_argument",
                prompt_flag="--message",
            )
        )


@dataclass(frozen=True)
class OpenCodeCliOptions:
    binary: str = "opencode"
    model: str | None = None
    agent: str | None = None
    json_events: bool = True
    dangerously_skip_permissions: bool = False
    extra_args: tuple[str, ...] = ()
    env: dict[str, str] = field(default_factory=dict)


class OpenCodeCliAdapter(ExternalCliAdapter):
    def __init__(self, options: OpenCodeCliOptions | None = None) -> None:
        options = options or OpenCodeCliOptions()
        args = ["run"]
        if options.json_events:
            args.extend(["--format", "json"])
        if options.model:
            args.extend(["--model", options.model])
        if options.agent:
            args.extend(["--agent", options.agent])
        if options.dangerously_skip_permissions:
            args.append("--dangerously-skip-permissions")
        super().__init__(
            ExternalCliOptions(
                binary=options.binary,
                args=tuple(args),
                extra_args=options.extra_args,
                env=options.env,
                prompt_mode="argument",
                workdir_flag="--dir",
            )
        )
