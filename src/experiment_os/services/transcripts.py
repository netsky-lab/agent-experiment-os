import json
import re
from typing import Any

from experiment_os.domain.schemas import RunEventInput


class TranscriptEventExtractor:
    def extract(self, *, run_id: str, transcript: str) -> list[RunEventInput]:
        if _looks_like_opencode_json_transcript(transcript):
            return _extract_opencode_json_events(run_id, transcript)

        events: list[RunEventInput] = []
        lines = transcript.splitlines()

        for line in lines:
            version = _package_version_event(run_id, line)
            if version:
                events.append(version)

            inspected = _file_inspection_event(run_id, line)
            if inspected:
                events.append(inspected)

            edited = _file_edit_event(run_id, line)
            if edited:
                events.append(edited)

            test_run = _test_run_event(run_id, line)
            if test_run:
                events.append(test_run)

            failure = _failure_event(run_id, line)
            if failure:
                events.append(failure)

        return _dedupe_events(events)


def _looks_like_opencode_json_transcript(transcript: str) -> bool:
    first_line = transcript.splitlines()[0] if transcript.splitlines() else ""
    return first_line.startswith("$ opencode run") and "--format json" in first_line


def _extract_opencode_json_events(run_id: str, transcript: str) -> list[RunEventInput]:
    events: list[RunEventInput] = []
    for line in transcript.splitlines():
        payload = _parse_json_line(line)
        if payload is None:
            continue
        event = _opencode_event(run_id, payload)
        if event is not None:
            events.append(event)
    return _dedupe_events(events)


def _parse_json_line(line: str) -> dict[str, Any] | None:
    try:
        value = json.loads(line)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _opencode_event(run_id: str, payload: dict[str, Any]) -> RunEventInput | None:
    part = payload.get("part")
    if not isinstance(part, dict):
        return None

    if payload.get("type") == "text" and isinstance(part.get("text"), str):
        return RunEventInput(
            run_id=run_id,
            event_type="final_answer",
            payload={"answer": part["text"], "source": "opencode_json"},
        )

    if payload.get("type") != "tool_use" or part.get("type") != "tool":
        return None

    state = part.get("state")
    if not isinstance(state, dict) or state.get("status") == "in_progress":
        return None
    tool = part.get("tool")
    tool_input = state.get("input") if isinstance(state.get("input"), dict) else {}

    if tool == "read":
        path = tool_input.get("filePath")
        if isinstance(path, str) and path:
            return RunEventInput(
                run_id=run_id,
                event_type="file_inspected",
                payload={"path": path, "source": "opencode_json"},
            )
        return None

    if tool == "edit":
        path = tool_input.get("filePath")
        if isinstance(path, str) and path:
            return RunEventInput(
                run_id=run_id,
                event_type="file_edited",
                payload={"path": path, "source": "opencode_json"},
            )
        return None

    if tool == "bash":
        command = tool_input.get("command")
        if not isinstance(command, str) or not command:
            return None
        exit_code = _opencode_exit_code(state)
        if _looks_like_test_command(command):
            return RunEventInput(
                run_id=run_id,
                event_type="test_run",
                payload={
                    "command": command,
                    "exit_code": exit_code,
                    "source": "opencode_json",
                },
            )
        if exit_code not in {None, 0}:
            return RunEventInput(
                run_id=run_id,
                event_type="failure_observed",
                payload={
                    "failure_type": "command_failed",
                    "severity": "low",
                    "command": command,
                    "exit_code": exit_code,
                    "source": "opencode_json",
                },
            )
        return None

    return None


def _opencode_exit_code(state: dict[str, Any]) -> int | None:
    metadata = state.get("metadata")
    if isinstance(metadata, dict) and isinstance(metadata.get("exit"), int):
        return metadata["exit"]
    return None


def _looks_like_test_command(command: str) -> bool:
    lower = command.lower()
    return any(token in lower for token in ["pytest", "npm test", "db:generate"])


def _package_version_event(run_id: str, line: str) -> RunEventInput | None:
    match = re.search(r"(drizzle-orm|drizzle-kit)[@=: ]+([0-9][\w.\-]+)", line, re.IGNORECASE)
    if not match:
        if "package.json" not in line.lower():
            return None
        return RunEventInput(
            run_id=run_id,
            event_type="package_version_checked",
            payload={"package": "unknown", "version": None, "source": "package.json", "line": line},
        )
    return RunEventInput(
        run_id=run_id,
        event_type="package_version_checked",
        payload={"package": match.group(1), "version": match.group(2), "source": "transcript"},
    )


def _file_inspection_event(run_id: str, line: str) -> RunEventInput | None:
    match = re.search(
        (
            r"(?:inspect|read|cat|open|ls|grep|rg).*?([\w./-]*(?:migration|schema|"
            r"vendor_sdk|agent_client/client|tests/test_client|pyproject)[\w./-]*)"
        ),
        line,
        re.IGNORECASE,
    )
    if not match:
        return None
    return RunEventInput(
        run_id=run_id,
        event_type="file_inspected",
        payload={"path": match.group(1), "reason": "transcript heuristic", "line": line},
    )


def _file_edit_event(run_id: str, line: str) -> RunEventInput | None:
    match = re.search(
        r"(?:edit|edited|write|wrote|patch|patched|modified|changed).*?([A-Za-z0-9_./-]+\.[A-Za-z0-9_]+)",
        line,
        re.IGNORECASE,
    )
    if not match:
        return None
    return RunEventInput(
        run_id=run_id,
        event_type="file_edited",
        payload={"path": match.group(1), "reason": "transcript heuristic", "line": line},
    )


def _test_run_event(run_id: str, line: str) -> RunEventInput | None:
    lower = line.lower()
    if not (
        "npm test" in lower
        or "db:generate" in lower
        or "test_run" in lower
        or re.search(r"(^|[\s;&|])(?:python\s+-m\s+)?pytest(?:\s|$)", lower)
    ):
        return None
    return RunEventInput(
        run_id=run_id,
        event_type="test_run",
        payload={"command": line.strip(), "passed": _line_looks_successful(line)},
    )


def _failure_event(run_id: str, line: str) -> RunEventInput | None:
    lower = line.lower()
    if "stale" in lower and ("api" in lower or "library" in lower):
        return RunEventInput(
            run_id=run_id,
            event_type="failure_observed",
            payload={"failure_type": "stale_library_knowledge", "severity": "medium", "evidence": line},
        )
    if "error" not in lower and "failed" not in lower:
        return None
    return RunEventInput(
        run_id=run_id,
        event_type="failure_observed",
        payload={"failure_type": "unknown", "severity": "low", "evidence": line},
    )


def _line_looks_successful(line: str) -> bool | None:
    lower = line.lower()
    if any(token in lower for token in ["pass", "passed", "success", "ok"]):
        return True
    if any(token in lower for token in ["fail", "failed", "error"]):
        return False
    return None


def _dedupe_events(events: list[RunEventInput]) -> list[RunEventInput]:
    seen: set[tuple[str, str]] = set()
    deduped: list[RunEventInput] = []
    for event in events:
        key = (event.event_type, str(sorted(event.payload.items())))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(event)
    return deduped
