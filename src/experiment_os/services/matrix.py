from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from experiment_os.prompts import (
    CODEX_MCP_AWARE_VERSION_TRAP_PROMPT,
    CODEX_VERSION_TRAP_BASELINE_PROMPT,
    CODEX_VERSION_TRAP_PROMPT,
)
from experiment_os.services.experiments import DRIZZLE_EXPERIMENT_ID, ExperimentRunner
from experiment_os.services.policy_candidates import PolicyCandidateService


@dataclass(frozen=True)
class MatrixCondition:
    id: str
    condition_id: str
    prompt: str
    mcp_enabled: bool


class ExperimentMatrixRunner:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._runner = ExperimentRunner(session)

    def run_version_trap_matrix(
        self,
        *,
        repeat_count: int = 1,
        model: str | None = None,
        sandbox: str = "workspace-write",
        approval_policy: str = "never",
        timeout_seconds: int = 900,
        fixture_path: Path = Path("fixtures/drizzle-version-trap-repo"),
        include_mcp: bool = True,
    ) -> dict:
        if repeat_count < 1:
            raise ValueError("repeat_count must be at least 1")

        matrix_id = f"matrix.version-trap.{uuid4().hex[:12]}"
        conditions = _version_trap_conditions(include_mcp=include_mcp)
        runs: list[dict] = []

        for repeat_index in range(repeat_count):
            for condition in conditions:
                run_metadata = {
                    "matrix_id": matrix_id,
                    "matrix_kind": "version_trap",
                    "matrix_condition": condition.id,
                    "matrix_repeat_index": repeat_index,
                    "mcp_enabled": condition.mcp_enabled,
                }
                if condition.mcp_enabled:
                    run = self._runner.run_codex_mcp_aware_version_trap(
                        condition_id=condition.condition_id,
                        model=model,
                        sandbox=sandbox,
                        approval_policy=approval_policy,
                        timeout_seconds=timeout_seconds,
                        fixture_path=fixture_path,
                        run_metadata=run_metadata,
                    )
                else:
                    run = self._runner.run_codex_toy_fixture(
                        condition_id=condition.condition_id,
                        prompt=condition.prompt,
                        model=model,
                        sandbox=sandbox,
                        approval_policy=approval_policy,
                        timeout_seconds=timeout_seconds,
                        fixture_path=fixture_path,
                        run_metadata=run_metadata,
                    )
                runs.append(
                    {
                        "matrix_condition": condition.id,
                        "repeat_index": repeat_index,
                        "mcp_enabled": condition.mcp_enabled,
                        "run": run,
                    }
                )

        report = {
            "matrix_id": matrix_id,
            "experiment_id": DRIZZLE_EXPERIMENT_ID,
            "matrix_kind": "version_trap",
            "repeat_count": repeat_count,
            "fixture_path": str(fixture_path),
            "conditions": [
                {
                    "id": condition.id,
                    "condition_id": condition.condition_id,
                    "mcp_enabled": condition.mcp_enabled,
                }
                for condition in conditions
            ],
            "runs": runs,
            "summary": _matrix_summary(runs),
        }
        report["policy_candidates"] = self._policy_candidates_from_matrix(report)
        return report

    def _policy_candidates_from_matrix(self, matrix_report: dict) -> list[dict]:
        baseline_runs = [
            item["run"]
            for item in matrix_report["runs"]
            if item["matrix_condition"] == "baseline"
        ]
        if not baseline_runs:
            return []

        service = PolicyCandidateService(self._session)
        candidates: list[dict] = []
        for candidate_condition in ("static_brief", "mcp_brief"):
            candidate_runs = [
                item["run"]
                for item in matrix_report["runs"]
                if item["matrix_condition"] == candidate_condition
            ]
            for index, candidate_run in enumerate(candidate_runs):
                if index >= len(baseline_runs):
                    continue
                comparison = _comparison_payload(
                    matrix_report=matrix_report,
                    baseline=baseline_runs[index],
                    candidate=candidate_run,
                    candidate_condition=candidate_condition,
                )
                page = service.propose_from_version_trap(comparison)
                if page is not None:
                    candidates.append(page)
        return candidates


def _version_trap_conditions(*, include_mcp: bool) -> list[MatrixCondition]:
    conditions = [
        MatrixCondition(
            id="baseline",
            condition_id="condition.001-drizzle-baseline",
            prompt=CODEX_VERSION_TRAP_BASELINE_PROMPT,
            mcp_enabled=False,
        ),
        MatrixCondition(
            id="static_brief",
            condition_id="condition.001-drizzle-brief-assisted",
            prompt=CODEX_VERSION_TRAP_PROMPT,
            mcp_enabled=False,
        ),
    ]
    if include_mcp:
        conditions.append(
            MatrixCondition(
                id="mcp_brief",
                condition_id="condition.001-drizzle-brief-assisted",
                prompt=CODEX_MCP_AWARE_VERSION_TRAP_PROMPT,
                mcp_enabled=True,
            )
        )
    return conditions


def _matrix_summary(runs: list[dict]) -> dict:
    by_condition: dict[str, list[dict]] = {}
    for item in runs:
        by_condition.setdefault(item["matrix_condition"], []).append(item["run"])
    return {
        condition_id: {
            "run_count": len(condition_runs),
            "metrics": _aggregate_metrics([run["metrics"] for run in condition_runs]),
        }
        for condition_id, condition_runs in sorted(by_condition.items())
    }


def _aggregate_metrics(metrics_list: list[dict]) -> dict:
    if not metrics_list:
        return {}

    keys = sorted({key for metrics in metrics_list for key in metrics})
    aggregate: dict[str, dict] = {}
    for key in keys:
        values = [metrics.get(key) for metrics in metrics_list if key in metrics]
        if all(isinstance(value, bool) for value in values):
            true_count = sum(1 for value in values if value)
            aggregate[key] = {
                "true_count": true_count,
                "false_count": len(values) - true_count,
                "rate": true_count / len(values) if values else 0,
            }
            continue
        if all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in values):
            aggregate[key] = {
                "mean": sum(values) / len(values) if values else 0,
                "min": min(values) if values else None,
                "max": max(values) if values else None,
            }
    return aggregate


def _comparison_payload(
    *,
    matrix_report: dict,
    baseline: dict,
    candidate: dict,
    candidate_condition: str,
) -> dict:
    return {
        "experiment_id": matrix_report["experiment_id"],
        "comparison": f"{matrix_report['matrix_id']}.baseline_vs_{candidate_condition}",
        "conditions": {
            "baseline": baseline,
            "brief_assisted": candidate,
        },
        "metric_deltas": _metric_deltas(baseline["metrics"], candidate["metrics"]),
        "matrix_id": matrix_report["matrix_id"],
        "candidate_condition": candidate_condition,
    }


def _metric_deltas(baseline: dict, candidate: dict) -> dict:
    deltas: dict[str, object] = {}
    for key in sorted(set(baseline) | set(candidate)):
        baseline_value = baseline.get(key)
        candidate_value = candidate.get(key)
        if isinstance(baseline_value, bool) or isinstance(candidate_value, bool):
            deltas[key] = {"baseline": baseline_value, "brief_assisted": candidate_value}
        elif isinstance(baseline_value, (int, float)) and isinstance(
            candidate_value,
            (int, float),
        ):
            deltas[key] = candidate_value - baseline_value
        else:
            deltas[key] = {"baseline": baseline_value, "brief_assisted": candidate_value}
    return deltas
