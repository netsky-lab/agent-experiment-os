from typing import Any


class RegressionDetector:
    """Compare two matrix projections and surface quality regressions."""

    def detect(self, comparison: dict[str, Any]) -> dict[str, Any]:
        regressions: list[dict[str, Any]] = []
        improvements: list[dict[str, Any]] = []
        for condition_id, condition in comparison.get("conditions", {}).items():
            if not condition.get("present_left") or not condition.get("present_right"):
                continue
            for key, delta in condition.get("quality_signal_deltas", {}).items():
                classification = _classify_quality_delta(key, delta.get("delta"))
                if classification == "regression":
                    regressions.append(_signal(condition_id, key, delta))
                elif classification == "improvement":
                    improvements.append(_signal(condition_id, key, delta))
            for key, delta in condition.get("metric_deltas", {}).items():
                classification = _classify_metric_delta(key, delta.get("delta"))
                if classification == "regression":
                    regressions.append(_signal(condition_id, key, delta))
                elif classification == "improvement":
                    improvements.append(_signal(condition_id, key, delta))
        return {
            "status": "regressed" if regressions else "stable",
            "regressions": regressions,
            "improvements": improvements,
        }


def _signal(condition_id: str, metric: str, delta: dict[str, Any]) -> dict[str, Any]:
    return {"condition_id": condition_id, "metric": metric, **delta}


def _classify_quality_delta(key: str, delta: Any) -> str | None:
    if not isinstance(delta, (int, float)) or delta == 0:
        return None
    lower_is_better = {
        "red_green_churn_mean",
        "forbidden_edit_mean",
        "wrong_file_edit_mean",
    }
    higher_is_better = {"clean_pass_rate"}
    if key in lower_is_better:
        return "regression" if delta > 0 else "improvement"
    if key in higher_is_better:
        return "regression" if delta < 0 else "improvement"
    return None


def _classify_metric_delta(key: str, delta: Any) -> str | None:
    if not isinstance(delta, (int, float)) or delta == 0:
        return None
    lower_is_better_tokens = ("failure", "forbidden", "wrong_file", "retry")
    higher_is_better_tokens = ("passing", "pre_work", "dependency_graph", "final_answer")
    if any(token in key for token in lower_is_better_tokens):
        return "regression" if delta > 0 else "improvement"
    if any(token in key for token in higher_is_better_tokens):
        return "regression" if delta < 0 else "improvement"
    return None
