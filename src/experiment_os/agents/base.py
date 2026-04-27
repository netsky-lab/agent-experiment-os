from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


class AgentAdapter(Protocol):
    def run(self, request: "AgentRunRequest") -> "AgentExecutionResult":
        pass


@dataclass(frozen=True)
class AgentRunRequest:
    command: str
    workdir: Path
    prompt: str | None = None
    env: dict[str, str] = field(default_factory=dict)
    timeout_seconds: int = 300


@dataclass(frozen=True)
class AgentExecutionResult:
    command: str
    workdir: Path
    stdout: str
    stderr: str
    exit_code: int
    duration_seconds: float

    @property
    def transcript(self) -> str:
        return (
            f"$ {self.command}\n\n"
            f"## STDOUT\n{self.stdout}\n\n"
            f"## STDERR\n{self.stderr}\n"
        )
