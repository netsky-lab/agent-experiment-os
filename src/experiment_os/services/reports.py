from dataclasses import dataclass
from typing import Any

from experiment_os.db.models import RunEvent


@dataclass(frozen=True)
class RunReport:
    data: dict[str, Any]
    markdown: str


class RunReportGenerator:
    def generate(
        self,
        *,
        condition_name: str,
        run: dict,
        metrics: dict,
        execution: dict,
        events: list[RunEvent],
        artifacts: dict[str, str],
        interpretation: str | None = None,
    ) -> RunReport:
        data = {
            "condition": condition_name,
            "run": run,
            "metrics": metrics,
            "execution": execution,
            "artifacts": artifacts,
        }
        if interpretation:
            data["interpretation"] = interpretation

        markdown = "\n".join(
            [
                f"# Run Report: {condition_name}",
                "",
                f"- Run: `{run['run_id']}`",
                f"- Agent: `{run['agent']}`",
                f"- Repo: `{run['repo']}`",
                f"- Exit code: `{execution['exit_code']}`",
                f"- Duration seconds: `{execution['duration_seconds']:.2f}`",
                "",
                "## Metrics",
                "",
                *[f"- `{key}`: `{value}`" for key, value in sorted(metrics.items())],
                "",
                "## Timeline",
                "",
                *[_event_line(event) for event in events],
                "",
                "## Artifacts",
                "",
                *[f"- `{name}`: `{path}`" for name, path in sorted(artifacts.items())],
                "",
                "## Interpretation",
                "",
                interpretation or _default_interpretation(metrics),
                "",
            ]
        )
        return RunReport(data=data, markdown=markdown)


def _event_line(event: RunEvent) -> str:
    summary = event.payload.get("path") or event.payload.get("package")
    if not summary:
        summary = event.payload.get("failure_type") or event.payload.get("command") or ""
    return f"- `{event.step_index}` `{event.event_type}` {summary}".rstrip()


def _default_interpretation(metrics: dict) -> str:
    if metrics.get("tests_passing") is True:
        return "The run reached a passing verification signal."
    if metrics.get("failure_count", 0) > 0:
        return "The run produced failure signals that should be classified before reuse."
    return "The run produced an observation record but no strong success or failure signal."
