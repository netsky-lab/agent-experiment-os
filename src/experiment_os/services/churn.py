from typing import Any

from experiment_os.db.models import RunEvent


class ChurnDrillDownService:
    """Explain red-green verification churn without asking reviewers to parse transcripts."""

    def from_events(self, events: list[RunEvent], metrics: dict[str, Any]) -> dict[str, Any]:
        test_events = [event for event in events if event.event_type == "test_run"]
        failed = [event for event in test_events if _test_failed(event.payload)]
        passed = [event for event in test_events if _test_passed(event.payload)]
        final_pass = bool(test_events) and _test_passed(test_events[-1].payload)
        recovered = bool(failed) and final_pass and any(
            event.step_index > failed[-1].step_index for event in passed
        )
        return {
            "has_churn": bool(failed),
            "clean_pass": final_pass and not failed,
            "recovered": recovered,
            "test_failure_count": metrics.get("test_failure_count", len(failed)),
            "tests_run": metrics.get("tests_run", len(test_events)),
            "failed_verifications": [_verification_event(event) for event in failed],
            "recovery_verification": _verification_event(passed[-1]) if recovered else None,
            "review_guidance": _review_guidance(failed=failed, recovered=recovered),
        }


def _verification_event(event: RunEvent) -> dict[str, Any]:
    payload = event.payload
    return {
        "step_index": event.step_index,
        "command": payload.get("command") or payload.get("cmd"),
        "exit_code": payload.get("exit_code"),
        "status": payload.get("status") or payload.get("outcome") or payload.get("result"),
        "output_excerpt": _excerpt(payload.get("output") or payload.get("stderr") or ""),
        "payload": payload,
    }


def _test_failed(payload: dict[str, Any]) -> bool:
    if payload.get("passed") is False:
        return True
    exit_code = payload.get("exit_code")
    if isinstance(exit_code, int):
        return exit_code != 0
    status = str(payload.get("status") or payload.get("outcome") or payload.get("result") or "").lower()
    return status in {"failed", "fail", "failure", "error"}


def _test_passed(payload: dict[str, Any]) -> bool:
    if payload.get("passed") is True:
        return True
    exit_code = payload.get("exit_code")
    if isinstance(exit_code, int):
        return exit_code == 0
    status = str(payload.get("status") or payload.get("outcome") or payload.get("result") or "").lower()
    return status in {"passed", "pass", "success", "succeeded", "ok"}


def _excerpt(value: Any, *, limit: int = 800) -> str:
    text = str(value)
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _review_guidance(*, failed: list[RunEvent], recovered: bool) -> list[str]:
    if not failed:
        return ["No failed verification before final state; treat this as a clean pass."]
    guidance = [
        "Inspect the failed verification output before accepting the final patch.",
        "Record the failure cause if the run is used as policy evidence.",
    ]
    if recovered:
        guidance.append("Check whether the recovery was a reusable intervention or task-specific trial-and-error.")
    else:
        guidance.append("Do not treat this run as successful policy evidence without a recovery verification.")
    return guidance
