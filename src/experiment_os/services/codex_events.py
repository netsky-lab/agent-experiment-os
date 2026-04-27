import json
import re
from collections.abc import Iterable
from typing import Any

from experiment_os.domain.schemas import RunEventInput


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
            events.extend(_events_from_payload(run_id, payload))
            failure = _codex_failure_event(run_id, payload, index)
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


def _events_from_payload(run_id: str, payload: dict[str, Any]) -> list[RunEventInput]:
    item = payload.get("item")
    if isinstance(item, dict):
        if item.get("type") == "command_execution":
            return _events_from_command_item(run_id, item)
        if item.get("type") == "file_change":
            return _file_change_events(run_id, item)

    if payload.get("type") == "file_change":
        return _file_change_events(run_id, payload)

    command = _optional_string(payload.get("cmd") or payload.get("command"))
    output = _optional_string(payload.get("output") or payload.get("aggregated_output"))
    if command or output:
        synthetic_item = {
            "command": command or "",
            "aggregated_output": output or "",
            "status": payload.get("status"),
            "exit_code": payload.get("exit_code"),
        }
        return _events_from_command_item(run_id, synthetic_item)

    return []


def _events_from_command_item(run_id: str, item: dict[str, Any]) -> list[RunEventInput]:
    command = _optional_string(item.get("command")) or ""
    output = _optional_string(item.get("aggregated_output")) or ""
    exit_code = item.get("exit_code")
    status = _optional_string(item.get("status"))

    if status == "in_progress":
        return []

    events: list[RunEventInput] = []
    events.extend(_version_events(run_id, command, output))
    inspected = _inspection_event(run_id, command)
    if inspected:
        events.append(inspected)
    test_run = _test_event(run_id, command, exit_code)
    if test_run:
        events.append(test_run)
    if _command_failed(status, exit_code):
        events.append(
            RunEventInput(
                run_id=run_id,
                event_type="failure_observed",
                payload={
                    "failure_type": "command_failed",
                    "severity": "low",
                    "command": command,
                    "exit_code": exit_code,
                    "evidence": output[:1000],
                },
            )
        )
    return events


def _version_events(run_id: str, command: str, output: str) -> list[RunEventInput]:
    text = f"{command}\n{output}"
    if "package.json" not in command and "npm list" not in command and "npm ls" not in command:
        return []

    matches = re.findall(
        (
            r'"(drizzle-orm|drizzle-kit)"\s*:\s*"([^"]+)"|'
            r"(drizzle-orm|drizzle-kit)[@=: ]+([0-9][\w.\-]+)"
        ),
        text,
        re.IGNORECASE,
    )
    events: list[RunEventInput] = []
    for quoted_package, quoted_version, inline_package, inline_version in matches:
        package = quoted_package or inline_package
        version = quoted_version or inline_version
        events.append(
            RunEventInput(
                run_id=run_id,
                event_type="package_version_checked",
                payload={"package": package, "version": version, "source": "codex_jsonl"},
            )
        )
    if events:
        return events
    if "package.json" in command:
        return [
            RunEventInput(
                run_id=run_id,
                event_type="package_version_checked",
                payload={"package": "unknown", "version": None, "source": "package.json"},
            )
        ]
    return []


def _inspection_event(run_id: str, command: str) -> RunEventInput | None:
    match = re.search(
        r"(?:cat|find|ls|rg|grep|sed).*?([\w./-]*(?:migration|schema|drizzle\.config)[\w./-]*)",
        command,
    )
    if not match:
        return None
    return RunEventInput(
        run_id=run_id,
        event_type="file_inspected",
        payload={"path": match.group(1), "reason": "codex command"},
    )


def _test_event(run_id: str, command: str, exit_code: Any) -> RunEventInput | None:
    if "npm run db:generate" not in command and "npm test" not in command and "pytest" not in command:
        return None
    if not isinstance(exit_code, int):
        return None
    return RunEventInput(
        run_id=run_id,
        event_type="test_run",
        payload={"command": command, "passed": exit_code == 0},
    )


def _file_change_events(run_id: str, item: dict[str, Any]) -> list[RunEventInput]:
    text = " ".join(_string_values(item))
    match = re.search(r"(?:modified|changed|edited|patched)\s+([A-Za-z0-9_./-]+\.[A-Za-z0-9_]+)", text)
    if not match:
        return []
    return [
        RunEventInput(
            run_id=run_id,
            event_type="file_edited",
            payload={"path": match.group(1), "reason": "codex file_change", "line": text},
        )
    ]


def _codex_failure_event(
    run_id: str,
    payload: dict[str, Any],
    index: int,
) -> RunEventInput | None:
    event_type = str(payload.get("type", "")).lower()
    text = " ".join(_string_values(payload))
    lower = text.lower()
    if event_type != "error" and event_type not in {"turn.failed", "exec_command.failed"}:
        return None
    if _transient_codex_error(lower):
        return None
    failure_type = "tool_call_failure" if "tool call" in lower else "codex_error"
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


def _command_failed(status: str | None, exit_code: Any) -> bool:
    if status == "failed":
        return True
    if isinstance(exit_code, int):
        return exit_code != 0
    return False


def _transient_codex_error(text: str) -> bool:
    transient_tokens = [
        "reconnecting",
        "stream disconnected",
        "failed to lookup address information",
        "failed to record rollout items",
    ]
    return any(token in text for token in transient_tokens)


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    return None


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
