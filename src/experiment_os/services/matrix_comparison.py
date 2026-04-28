from typing import Any


class MatrixComparisonService:
    def compare(self, *, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
        left_conditions = left.get("conditions", {})
        right_conditions = right.get("conditions", {})
        condition_ids = sorted(set(left_conditions) | set(right_conditions))
        return {
            "left_matrix_id": left["matrix_id"],
            "right_matrix_id": right["matrix_id"],
            "left": _matrix_header(left),
            "right": _matrix_header(right),
            "conditions": {
                condition_id: self._compare_condition(
                    left_conditions.get(condition_id),
                    right_conditions.get(condition_id),
                )
                for condition_id in condition_ids
            },
        }

    def _compare_condition(
        self,
        left: dict[str, Any] | None,
        right: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if left is None or right is None:
            return {
                "present_left": left is not None,
                "present_right": right is not None,
                "metric_deltas": {},
                "quality_signal_deltas": {},
                "protocol_compliance_delta": {},
            }
        return {
            "present_left": True,
            "present_right": True,
            "run_count_delta": right["run_count"] - left["run_count"],
            "metric_deltas": _metric_deltas(left["metrics"], right["metrics"]),
            "quality_signal_deltas": _flat_numeric_delta(
                left.get("quality_signals", {}),
                right.get("quality_signals", {}),
            ),
            "protocol_compliance_delta": _protocol_delta(
                left.get("protocol_compliance", {}),
                right.get("protocol_compliance", {}),
            ),
        }


def _matrix_header(matrix: dict[str, Any]) -> dict[str, Any]:
    return {
        "matrix_id": matrix["matrix_id"],
        "matrix_kind": matrix.get("matrix_kind"),
        "run_count": matrix.get("run_count"),
        "latest_result_created_at": matrix.get("latest_result_created_at"),
    }


def _metric_deltas(left: dict[str, dict], right: dict[str, dict]) -> dict[str, Any]:
    deltas: dict[str, Any] = {}
    for key in sorted(set(left) | set(right)):
        left_value = _metric_value(left.get(key))
        right_value = _metric_value(right.get(key))
        if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
            deltas[key] = {
                "left": left_value,
                "right": right_value,
                "delta": right_value - left_value,
            }
    return deltas


def _metric_value(value: dict | None) -> float | None:
    if not isinstance(value, dict):
        return None
    if "rate" in value and isinstance(value["rate"], (int, float)):
        return float(value["rate"])
    if "mean" in value and isinstance(value["mean"], (int, float)):
        return float(value["mean"])
    return None


def _flat_numeric_delta(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    deltas: dict[str, Any] = {}
    for key in sorted(set(left) | set(right)):
        left_value = left.get(key)
        right_value = right.get(key)
        if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
            deltas[key] = {
                "left": left_value,
                "right": right_value,
                "delta": right_value - left_value,
            }
    return deltas


def _protocol_delta(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_steps = left.get("steps", {})
    right_steps = right.get("steps", {})
    return _flat_numeric_delta(left_steps, right_steps)
