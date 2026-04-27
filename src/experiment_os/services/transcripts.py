import re

from experiment_os.domain.schemas import RunEventInput


class TranscriptEventExtractor:
    def extract(self, *, run_id: str, transcript: str) -> list[RunEventInput]:
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
    if not any(token in lower for token in ["npm test", "pytest", "db:generate", "test_run"]):
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
