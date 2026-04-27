import json
from collections.abc import Iterable
from typing import Any

from experiment_os.domain.schemas import RunEventInput
from experiment_os.services.transcripts import TranscriptEventExtractor


class CodexJsonlEventExtractor:
    """Extract experiment events from `codex exec --json` JSONL output."""

    def extract(self, *, run_id: str, jsonl: str) -> list[RunEventInput]:
        events: list[RunEventInput] = []
        for index, line in enumerate(jsonl.splitlines()):
            if not line.strip():
                continue
            payload = _parse_json(line)
            if payload is None:
                continue
            text = " ".join(_string_values(payload))
            events.extend(
                TranscriptEventExtractor().extract(
                    run_id=run_id,
                    transcript=text,
                )
            )
            failure = _codex_failure_event(run_id, payload, text, index)
            if failure:
                events.append(failure)
        return _dedupe(events)


def _parse_json(line: str) -> dict[str, Any] | None:
    try:
        value = json.loads(line)
    except json.JSONDecodeError:
        return None
    if isinstance(value, dict):
        return value
    return None


def _string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
        return
    if isinstance(value, dict):
        for nested in value.values():
            yield from _string_values(nested)
        return
    if isinstance(value, list):
        for nested in value:
            yield from _string_values(nested)


def _codex_failure_event(
    run_id: str,
    payload: dict[str, Any],
    text: str,
    index: int,
) -> RunEventInput | None:
    event_type = str(payload.get("type", "")).lower()
    lower = text.lower()
    if event_type not in {"error", "turn.failed", "exec_command.failed"}:
        if "tool call" not in lower and "failed" not in lower and "error" not in lower:
            return None
    failure_type = "tool_call_failure" if "tool call" in lower else "unknown"
    return RunEventInput(
        run_id=run_id,
        event_type="failure_observed",
        payload={
            "failure_type": failure_type,
            "severity": "medium",
            "evidence": text[:1000],
            "codex_event_index": index,
        },
    )


def _dedupe(events: list[RunEventInput]) -> list[RunEventInput]:
    seen: set[tuple[str, str]] = set()
    result: list[RunEventInput] = []
    for event in events:
        key = (event.event_type, json.dumps(event.payload, sort_keys=True, default=str))
        if key in seen:
            continue
        seen.add(key)
        result.append(event)
    return result
