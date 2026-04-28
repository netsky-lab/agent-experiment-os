from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from experiment_os.prompts import (
    CODEX_API_DRIFT_BASELINE_PROMPT,
    CODEX_API_DRIFT_PROMPT,
    CODEX_MCP_AWARE_API_DRIFT_PROMPT,
    CODEX_MCP_AWARE_VERSION_TRAP_PROMPT,
    CODEX_VERSION_TRAP_BASELINE_PROMPT,
    CODEX_VERSION_TRAP_PROMPT,
)
from experiment_os.services.experiments import (
    API_DRIFT_EXPERIMENT_ID,
    DRIZZLE_EXPERIMENT_ID,
    ExperimentRunner,
)
from experiment_os.services.policy_candidates import PolicyCandidateService


@dataclass(frozen=True)
class MatrixCondition:
    id: str
    condition_id: str
    prompt: str
    mcp_enabled: bool
    pre_work_gate: bool = False
    agent_backend: str = "codex"


class ExperimentMatrixRunner:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._runner = ExperimentRunner(session)

    def run_version_trap_matrix(
        self,
        *,
        repeat_count: int = 1,
        model: str | None = None,
        models: list[str | None] | None = None,
        sandbox: str = "workspace-write",
        approval_policy: str = "never",
        timeout_seconds: int = 900,
        fixture_path: Path = Path("fixtures/drizzle-version-trap-repo"),
        include_mcp: bool = True,
        include_gated: bool = False,
        progress: Callable[[dict], None] | None = None,
        write_result_artifact: bool = False,
        result_dir: Path = Path("experiments/001-drizzle-brief/results"),
    ) -> dict:
        return self._run_codex_matrix(
            matrix_kind="version_trap",
            fixture_path=fixture_path,
            repeat_count=repeat_count,
            model=model,
            models=models,
            sandbox=sandbox,
            approval_policy=approval_policy,
            timeout_seconds=timeout_seconds,
            conditions=_version_trap_conditions(
                include_mcp=include_mcp,
                include_gated=include_gated,
            ),
            progress=progress,
            write_result_artifact=write_result_artifact,
            result_dir=result_dir,
        )

    def run_api_drift_matrix(
        self,
        *,
        repeat_count: int = 1,
        model: str | None = None,
        models: list[str | None] | None = None,
        sandbox: str = "workspace-write",
        approval_policy: str = "never",
        timeout_seconds: int = 900,
        fixture_path: Path = Path("fixtures/python-api-drift-repo"),
        include_mcp: bool = True,
        include_gated: bool = False,
        include_opencode: bool = False,
        progress: Callable[[dict], None] | None = None,
        write_result_artifact: bool = False,
        result_dir: Path = Path("experiments/002-python-api-drift/results"),
    ) -> dict:
        return self._run_codex_matrix(
            matrix_kind="api_drift",
            fixture_path=fixture_path,
            repeat_count=repeat_count,
            model=model,
            models=models,
            sandbox=sandbox,
            approval_policy=approval_policy,
            timeout_seconds=timeout_seconds,
            conditions=_api_drift_conditions(
                include_mcp=include_mcp,
                include_gated=include_gated,
                include_opencode=include_opencode,
            ),
            progress=progress,
            write_result_artifact=write_result_artifact,
            result_dir=result_dir,
        )

    def _run_codex_matrix(
        self,
        *,
        matrix_kind: str,
        fixture_path: Path,
        repeat_count: int,
        model: str | None,
        models: list[str | None] | None,
        sandbox: str,
        approval_policy: str,
        timeout_seconds: int,
        conditions: list[MatrixCondition],
        progress: Callable[[dict], None] | None,
        write_result_artifact: bool,
        result_dir: Path,
    ) -> dict:
        if repeat_count < 1:
            raise ValueError("repeat_count must be at least 1")

        matrix_id = f"matrix.{matrix_kind.replace('_', '-')}.{uuid4().hex[:12]}"
        matrix_models = _matrix_models(model=model, models=models)
        runs: list[dict] = []

        _emit_progress(
            progress,
            {
                "event": "matrix_started",
                "matrix_id": matrix_id,
                "repeat_count": repeat_count,
                "conditions": [condition.id for condition in conditions],
                "models": [_model_label(item) for item in matrix_models],
            },
        )

        for model_value in matrix_models:
            model_label = _model_label(model_value)
            for repeat_index in range(repeat_count):
                for condition in conditions:
                    run_metadata = {
                        "matrix_id": matrix_id,
                        "matrix_kind": matrix_kind,
                        "matrix_condition": condition.id,
                        "matrix_model": model_label,
                        "matrix_repeat_index": repeat_index,
                        "mcp_enabled": condition.mcp_enabled,
                        "pre_work_gate": condition.pre_work_gate,
                        "agent_backend": condition.agent_backend,
                    }
                    _emit_progress(
                        progress,
                        {
                            "event": "run_started",
                            "matrix_id": matrix_id,
                            "condition": condition.id,
                            "repeat_index": repeat_index,
                            "model": model_label,
                            "mcp_enabled": condition.mcp_enabled,
                            "pre_work_gate": condition.pre_work_gate,
                            "agent_backend": condition.agent_backend,
                        },
                    )
                    if condition.mcp_enabled:
                        run = self._run_mcp_condition(
                            matrix_kind=matrix_kind,
                            condition=condition,
                            model=model_value,
                            sandbox=sandbox,
                            approval_policy=approval_policy,
                            timeout_seconds=timeout_seconds,
                            fixture_path=fixture_path,
                            run_metadata=run_metadata,
                        )
                    else:
                        run = self._run_static_condition(
                            matrix_kind=matrix_kind,
                            condition=condition,
                            model=model_value,
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
                            "model": model_label,
                            "mcp_enabled": condition.mcp_enabled,
                            "pre_work_gate": condition.pre_work_gate,
                            "agent_backend": condition.agent_backend,
                            "run": run,
                        }
                    )
                    _emit_progress(
                        progress,
                        {
                            "event": "run_finished",
                            "matrix_id": matrix_id,
                            "condition": condition.id,
                            "repeat_index": repeat_index,
                            "model": model_label,
                            "run_id": run["run"]["run_id"],
                            "exit_code": run["execution"]["exit_code"],
                            "duration_seconds": run["execution"]["duration_seconds"],
                            "metrics": _progress_metrics(run["metrics"]),
                        },
                    )

        report = {
            "matrix_id": matrix_id,
            "experiment_id": _matrix_experiment_id(matrix_kind),
            "matrix_kind": matrix_kind,
            "repeat_count": repeat_count,
            "fixture_path": str(fixture_path),
            "models": [_model_label(item) for item in matrix_models],
            "conditions": [
                {
                    "id": condition.id,
                    "condition_id": condition.condition_id,
                    "mcp_enabled": condition.mcp_enabled,
                    "pre_work_gate": condition.pre_work_gate,
                    "agent_backend": condition.agent_backend,
                }
                for condition in conditions
            ],
            "runs": runs,
            "summary": _matrix_summary(runs),
            "summary_by_model": _matrix_summary_by_model(runs),
        }
        report["policy_candidates"] = self._policy_candidates_from_matrix(report)
        if write_result_artifact:
            report["result_artifact"] = str(_write_matrix_result(report, result_dir=result_dir))
        _emit_progress(
            progress,
            {
                "event": "matrix_finished",
                "matrix_id": matrix_id,
                "run_count": len(runs),
                "result_artifact": report.get("result_artifact"),
            },
        )
        return report

    def _run_static_condition(
        self,
        *,
        matrix_kind: str,
        condition: MatrixCondition,
        model: str | None,
        sandbox: str,
        approval_policy: str,
        timeout_seconds: int,
        fixture_path: Path,
        run_metadata: dict,
    ) -> dict:
        if condition.agent_backend == "opencode":
            if matrix_kind != "api_drift":
                raise ValueError("OpenCode matrix conditions are only implemented for api_drift")
            return self._runner.run_opencode_api_drift(
                condition_id=condition.condition_id,
                prompt=condition.prompt,
                model=model,
                timeout_seconds=timeout_seconds,
                fixture_path=fixture_path,
                run_metadata=run_metadata,
                pre_work_gate=condition.pre_work_gate,
            )
        if matrix_kind == "api_drift":
            return self._runner.run_codex_api_drift(
                condition_id=condition.condition_id,
                prompt=condition.prompt,
                model=model,
                sandbox=sandbox,
                approval_policy=approval_policy,
                timeout_seconds=timeout_seconds,
                fixture_path=fixture_path,
                run_metadata=run_metadata,
                pre_work_gate=condition.pre_work_gate,
            )
        return self._runner.run_codex_toy_fixture(
            condition_id=condition.condition_id,
            prompt=condition.prompt,
            model=model,
            sandbox=sandbox,
            approval_policy=approval_policy,
            timeout_seconds=timeout_seconds,
            fixture_path=fixture_path,
            run_metadata=run_metadata,
            pre_work_gate=condition.pre_work_gate,
        )

    def _run_mcp_condition(
        self,
        *,
        matrix_kind: str,
        condition: MatrixCondition,
        model: str | None,
        sandbox: str,
        approval_policy: str,
        timeout_seconds: int,
        fixture_path: Path,
        run_metadata: dict,
    ) -> dict:
        if matrix_kind == "api_drift":
            return self._runner.run_codex_mcp_aware_api_drift(
                condition_id=condition.condition_id,
                model=model,
                sandbox=sandbox,
                approval_policy=approval_policy,
                timeout_seconds=timeout_seconds,
                fixture_path=fixture_path,
                run_metadata=run_metadata,
            )
        return self._runner.run_codex_mcp_aware_version_trap(
            condition_id=condition.condition_id,
            model=model,
            sandbox=sandbox,
            approval_policy=approval_policy,
            timeout_seconds=timeout_seconds,
            fixture_path=fixture_path,
            run_metadata=run_metadata,
        )

    def _policy_candidates_from_matrix(self, matrix_report: dict) -> list[dict]:
        service = PolicyCandidateService(self._session)
        candidates: list[dict] = []
        protocol_candidate = service.propose_from_mcp_protocol_gap(matrix_report)
        if protocol_candidate is not None:
            candidates.append(protocol_candidate)
        for item in matrix_report["runs"]:
            run_candidate = service.propose_from_run_summary(item["run"])
            if run_candidate is not None:
                candidates.append(run_candidate)

        if matrix_report["matrix_kind"] != "version_trap":
            return candidates
        baseline_runs = [
            item["run"]
            for item in matrix_report["runs"]
            if item["matrix_condition"] == "baseline"
        ]
        if not baseline_runs:
            return candidates

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


def _version_trap_conditions(*, include_mcp: bool, include_gated: bool) -> list[MatrixCondition]:
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
    if include_gated:
        conditions.append(
            MatrixCondition(
                id="gated_brief",
                condition_id="condition.001-drizzle-brief-assisted",
                prompt=CODEX_VERSION_TRAP_PROMPT,
                mcp_enabled=False,
                pre_work_gate=True,
            )
        )
    return conditions


def _api_drift_conditions(
    *,
    include_mcp: bool,
    include_gated: bool,
    include_opencode: bool,
) -> list[MatrixCondition]:
    conditions = [
        MatrixCondition(
            id="baseline",
            condition_id="condition.002-api-drift-baseline",
            prompt=CODEX_API_DRIFT_BASELINE_PROMPT,
            mcp_enabled=False,
        ),
        MatrixCondition(
            id="static_brief",
            condition_id="condition.002-api-drift-brief-assisted",
            prompt=CODEX_API_DRIFT_PROMPT,
            mcp_enabled=False,
        ),
    ]
    if include_mcp:
        conditions.append(
            MatrixCondition(
                id="mcp_brief",
                condition_id="condition.002-api-drift-brief-assisted",
                prompt=CODEX_MCP_AWARE_API_DRIFT_PROMPT,
                mcp_enabled=True,
            )
        )
    if include_gated:
        conditions.append(
            MatrixCondition(
                id="gated_brief",
                condition_id="condition.002-api-drift-brief-assisted",
                prompt=CODEX_API_DRIFT_PROMPT,
                mcp_enabled=False,
                pre_work_gate=True,
            )
        )
    if include_opencode:
        conditions.append(
            MatrixCondition(
                id="opencode_gated_brief",
                condition_id="condition.002-api-drift-brief-assisted",
                prompt=CODEX_API_DRIFT_PROMPT,
                mcp_enabled=False,
                pre_work_gate=True,
                agent_backend="opencode",
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


def _matrix_summary_by_model(runs: list[dict]) -> dict:
    by_model: dict[str, list[dict]] = {}
    for item in runs:
        by_model.setdefault(item["model"], []).append(item)
    return {
        model: _matrix_summary(model_runs)
        for model, model_runs in sorted(by_model.items())
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


def _matrix_models(
    *,
    model: str | None,
    models: list[str | None] | None,
) -> list[str | None]:
    if models:
        return [item if item else None for item in models]
    return [model]


def _model_label(model: str | None) -> str:
    return model or "codex-default"


def _emit_progress(progress: Callable[[dict], None] | None, event: dict) -> None:
    if progress is not None:
        progress(event)


def _progress_metrics(metrics: dict) -> dict:
    keys = [
        "tests_passing",
        "test_failure_count",
        "dependency_changed",
        "rewrote_migration_history",
        "wrong_file_edits",
        "file_edit_count",
        "mcp_pre_work_protocol_called",
        "mcp_tool_call_count",
    ]
    return {key: metrics.get(key) for key in keys if key in metrics}


def _write_matrix_result(matrix_report: dict, *, result_dir: Path) -> Path:
    result_dir.mkdir(parents=True, exist_ok=True)
    date = datetime.now(UTC).date().isoformat()
    slug = matrix_report["matrix_id"].replace(".", "-")
    path = result_dir / f"{date}-{slug}.md"
    path.write_text(_matrix_markdown(matrix_report), encoding="utf-8")
    return path


def _matrix_markdown(matrix_report: dict) -> str:
    interpretation = _matrix_interpretation(matrix_report)
    lines = [
        f"# Codex {_matrix_title(matrix_report['matrix_kind'])} Matrix",
        "",
        f"Date: {datetime.now(UTC).date().isoformat()}",
        "",
        f"Matrix id: `{matrix_report['matrix_id']}`",
        "",
        f"Fixture: `{matrix_report['fixture_path']}`",
        "",
        f"Repeat count: `{matrix_report['repeat_count']}`",
        "",
        "Models: "
        + ", ".join(f"`{model}`" for model in matrix_report.get("models", [])),
        "",
        "## Runs",
        "",
        "| Model | Repeat | Condition | Run | Exit | Duration |",
        "| --- | ---: | --- | --- | ---: | ---: |",
    ]
    for item in matrix_report["runs"]:
        run = item["run"]
        lines.append(
            (
                "| {model} | {repeat} | {condition} | `{run_id}` | "
                "{exit_code} | {duration:.2f}s |"
            ).format(
                model=item["model"],
                repeat=item["repeat_index"],
                condition=item["matrix_condition"],
                run_id=run["run"]["run_id"],
                exit_code=run["execution"]["exit_code"],
                duration=run["execution"]["duration_seconds"],
            )
        )

    lines.extend(["", "## Summary", ""])
    for condition, summary in matrix_report["summary"].items():
        metrics = summary["metrics"]
        lines.extend(
            [
                f"### {condition}",
                "",
                f"- run count: `{summary['run_count']}`",
                f"- tests passing rate: `{_rate(metrics, 'tests_passing')}`",
                f"- test failure mean: `{_mean(metrics, 'test_failure_count')}`",
                f"- dependency change rate: `{_rate(metrics, 'dependency_changed')}`",
                f"- file edit mean: `{_mean(metrics, 'file_edit_count')}`",
                f"- wrong-file edit mean: `{_mean(metrics, 'wrong_file_edits')}`",
                f"- forbidden edit mean: `{_mean(metrics, 'forbidden_edit_count')}`",
                f"- MCP pre-work rate: `{_rate(metrics, 'mcp_pre_work_protocol_called')}`",
                f"- MCP dependency graph rate: `{_rate(metrics, 'mcp_dependency_graph_loaded')}`",
                f"- MCP final-answer rate: `{_rate(metrics, 'mcp_final_answer_recorded')}`",
                f"- MCP call mean: `{_mean(metrics, 'mcp_tool_call_count')}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Interpretation",
            "",
            interpretation["summary"],
            "",
            "## Evidence",
            "",
            *[f"- {item}" for item in interpretation["evidence"]],
            "",
            "## Policy Decision",
            "",
            interpretation["policy_decision"],
            "",
            "## Next Experiment",
            "",
            interpretation["next_experiment"],
            "",
        ]
    )
    return "\n".join(lines)


def _matrix_interpretation(matrix_report: dict) -> dict[str, object]:
    summary = matrix_report["summary"]
    baseline = summary.get("baseline", {}).get("metrics", {})
    gated_conditions = [
        condition
        for condition in ("gated_brief", "opencode_gated_brief")
        if condition in summary
    ]

    evidence: list[str] = []
    for condition, condition_summary in summary.items():
        metrics = condition_summary["metrics"]
        evidence.append(
            (
                f"`{condition}`: pass rate {_rate(metrics, 'tests_passing')}, "
                f"test-failure mean {_mean(metrics, 'test_failure_count')}, "
                f"pre-work rate {_rate(metrics, 'mcp_pre_work_protocol_called')}, "
                f"wrong-file mean {_mean(metrics, 'wrong_file_edits')}, "
                f"forbidden-edit mean {_mean(metrics, 'forbidden_edit_count')}."
            )
        )

    safety_signal = any(
        (_mean_float(item["metrics"], "forbidden_edit_count") or 0) > 0
        or (_mean_float(item["metrics"], "wrong_file_edits") or 0) > 0
        or (_rate_float(item["metrics"], "dependency_changed") or 0) > 0
        for item in summary.values()
    )
    red_green_churn_signal = any(
        (_mean_float(item["metrics"], "test_failure_count") or 0) > 0
        for item in summary.values()
    )
    gated_protocol_signal = bool(gated_conditions) and all(
        (_rate_float(summary[condition]["metrics"], "mcp_pre_work_protocol_called") or 0) >= 1
        and (_rate_float(summary[condition]["metrics"], "mcp_dependency_graph_loaded") or 0) >= 1
        for condition in gated_conditions
    )
    baseline_pass_rate = _rate_float(baseline, "tests_passing")
    gated_pass_rates = [
        _rate_float(summary[condition]["metrics"], "tests_passing")
        for condition in gated_conditions
    ]
    correctness_lift = (
        baseline_pass_rate is not None
        and any(rate is not None and rate > baseline_pass_rate for rate in gated_pass_rates)
    )

    if gated_protocol_signal and not correctness_lift:
        summary_text = (
            "The matrix supports adapter-enforced protocol compliance, not a task-success lift. "
            "Gated conditions loaded Experiment OS pre-work and dependency graph state while final "
            "task success remained comparable to baseline."
        )
        if red_green_churn_signal:
            summary_text += " Red-green churn appeared as a separate review signal."
    elif correctness_lift:
        summary_text = (
            "The matrix shows a candidate task-success lift in gated conditions. Treat this as a "
            "research signal until it repeats on a larger fixture."
        )
        if red_green_churn_signal:
            summary_text += " Red-green churn should be analyzed before policy promotion."
    else:
        summary_text = (
            "The matrix did not show a strong protocol or task-success improvement signal."
        )
        if red_green_churn_signal:
            summary_text += " It did surface red-green churn as a review signal."

    if safety_signal:
        policy_decision = (
            "Keep generated safety policy candidates in draft review. Safety failures were observed "
            "and must be inspected before becoming agent decision rules."
        )
    elif red_green_churn_signal:
        policy_decision = (
            "Keep generated red-green churn policy candidates in draft review. Do not promote a "
            "correctness policy from this matrix because final success was already saturated."
        )
    elif gated_protocol_signal:
        policy_decision = (
            "Do not promote a correctness policy. Promote the engineering direction that controlled "
            "experiment runs should enforce pre-work at the adapter boundary."
        )
    else:
        policy_decision = "Do not promote a policy candidate from this matrix."

    return {
        "summary": summary_text,
        "evidence": evidence,
        "policy_decision": policy_decision,
        "next_experiment": (
            "Repeat on a larger fixture with hidden local API surface and compare task success, "
            "forbidden edits, dependency edits, red-green churn, and protocol compliance separately."
        ),
    }


def _rate(metrics: dict, key: str) -> str:
    value = metrics.get(key, {})
    if not isinstance(value, dict) or "rate" not in value:
        return "n/a"
    return f"{value['rate']:.2f}"


def _mean(metrics: dict, key: str) -> str:
    value = metrics.get(key, {})
    if not isinstance(value, dict) or "mean" not in value:
        return "n/a"
    return f"{value['mean']:.2f}"


def _rate_float(metrics: dict, key: str) -> float | None:
    value = metrics.get(key, {})
    if not isinstance(value, dict) or "rate" not in value:
        return None
    return float(value["rate"])


def _mean_float(metrics: dict, key: str) -> float | None:
    value = metrics.get(key, {})
    if not isinstance(value, dict) or "mean" not in value:
        return None
    return float(value["mean"])


def _matrix_title(matrix_kind: str) -> str:
    return matrix_kind.replace("_", " ").title()


def _matrix_experiment_id(matrix_kind: str) -> str:
    if matrix_kind == "api_drift":
        return API_DRIFT_EXPERIMENT_ID
    return DRIZZLE_EXPERIMENT_ID


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
