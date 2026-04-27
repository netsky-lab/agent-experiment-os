from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExperimentReportV2:
    data: dict[str, Any]
    markdown: str


class ExperimentReportGenerator:
    def comparison(
        self,
        *,
        experiment_id: str,
        hypothesis: str,
        baseline: dict,
        candidate: dict,
        metric_deltas: dict,
        interpretation: str,
    ) -> ExperimentReportV2:
        observed_failures = _observed_failures(baseline, candidate)
        policy_candidates = _policy_candidates(baseline, candidate)
        next_experiment = _next_experiment(metric_deltas, observed_failures)
        data = {
            "schema": "experiment_report.v2",
            "experiment_id": experiment_id,
            "hypothesis": hypothesis,
            "conditions": {
                "baseline": _condition_summary(baseline),
                "candidate": _condition_summary(candidate),
            },
            "metric_deltas": metric_deltas,
            "observed_failures": observed_failures,
            "interpretation": interpretation,
            "next_experiment": next_experiment,
            "policy_candidates": policy_candidates,
        }
        return ExperimentReportV2(data=data, markdown=_markdown(data))


def _condition_summary(report: dict) -> dict[str, Any]:
    return {
        "name": report["condition"],
        "run_id": report["run"]["run_id"],
        "metrics": report["metrics"],
        "execution": report["execution"],
        "artifacts": report.get("artifacts", {}),
    }


def _observed_failures(baseline: dict, candidate: dict) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for label, report in [("baseline", baseline), ("candidate", candidate)]:
        metrics = report["metrics"]
        if metrics.get("failure_count", 0):
            failures.append(
                {
                    "condition": label,
                    "failure_type": "observed_failure_events",
                    "count": metrics["failure_count"],
                }
            )
        if metrics.get("wrong_file_edits", 0):
            failures.append(
                {
                    "condition": label,
                    "failure_type": "wrong_file_edit",
                    "count": metrics["wrong_file_edits"],
                }
            )
    return failures


def _policy_candidates(baseline: dict, candidate: dict) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    if (
        not baseline["metrics"].get("inspected_package_versions_before_edit")
        and candidate["metrics"].get("inspected_package_versions_before_edit")
    ):
        candidates.append(
            {
                "title": "Require package version inspection before dependency-specific edits",
                "source": "metric_delta",
                "status": "candidate",
            }
        )
    if baseline["metrics"].get("wrong_file_edits", 0) > candidate["metrics"].get("wrong_file_edits", 0):
        candidates.append(
            {
                "title": "Use issue knowledge as evidence before editing dependency manifests",
                "source": "metric_delta",
                "status": "candidate",
            }
        )
    return candidates


def _next_experiment(metric_deltas: dict, observed_failures: list[dict[str, Any]]) -> dict[str, Any]:
    if not observed_failures and not _has_behavioral_delta(metric_deltas):
        return {
            "title": "Add a harder fixture with a version-conflict trap",
            "reason": "Current task does not separate baseline and brief-assisted behavior.",
        }
    return {
        "title": "Repeat comparison on a less synthetic repo",
        "reason": "Observed failures or metric deltas need replication before policy promotion.",
    }


def _has_behavioral_delta(metric_deltas: dict) -> bool:
    for value in metric_deltas.values():
        if isinstance(value, (int, float)) and value != 0:
            return True
        if isinstance(value, dict) and value.get("baseline") != value.get("brief_assisted"):
            return True
    return False


def _markdown(data: dict[str, Any]) -> str:
    lines = [
        f"# Experiment Report: {data['experiment_id']}",
        "",
        "## Hypothesis",
        "",
        data["hypothesis"],
        "",
        "## Conditions",
        "",
    ]
    for key, condition in data["conditions"].items():
        lines.append(f"- `{key}`: `{condition['run_id']}`")
    lines.extend(["", "## Metric Deltas", ""])
    for key, value in data["metric_deltas"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Interpretation", "", data["interpretation"], "", "## Next Experiment", ""])
    lines.append(f"- {data['next_experiment']['title']}: {data['next_experiment']['reason']}")
    return "\n".join(lines) + "\n"
