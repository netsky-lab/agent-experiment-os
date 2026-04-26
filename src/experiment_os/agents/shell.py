import os
import subprocess
import time

from experiment_os.agents.base import AgentExecutionResult, AgentRunRequest


class ShellAgentAdapter:
    def run(self, request: AgentRunRequest) -> AgentExecutionResult:
        env = {**os.environ, **request.env}
        if request.prompt is not None:
            env["EXPERIMENT_OS_PROMPT"] = request.prompt

        started = time.monotonic()
        completed = subprocess.run(
            request.command,
            cwd=request.workdir,
            env=env,
            shell=True,
            text=True,
            capture_output=True,
            timeout=request.timeout_seconds,
            check=False,
        )
        duration = time.monotonic() - started
        return AgentExecutionResult(
            command=request.command,
            workdir=request.workdir,
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
            duration_seconds=duration,
        )

