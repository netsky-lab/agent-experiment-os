from experiment_os.db.models import RunEvent


class MetricsExtractor:
    def extract(self, events: list[RunEvent]) -> dict:
        first_edit_index = _first_index(events, "file_edited")

        package_version_indices = [
            event.step_index
            for event in events
            if event.event_type == "package_version_checked"
        ]
        migration_inspection_indices = [
            event.step_index
            for event in events
            if event.event_type == "file_inspected"
            and _looks_like_migration_inspection(event.payload)
        ]
        api_surface_inspection_indices = [
            event.step_index
            for event in events
            if event.event_type in {"file_inspected", "local_api_surface_checked"}
            and _looks_like_api_surface_inspection(event.payload)
        ]
        test_runs = [event for event in events if event.event_type == "test_run"]
        test_outcomes = [
            outcome
            for event in test_runs
            if (outcome := _test_outcome(event.payload)) is not None
        ]
        failures = [event for event in events if event.event_type == "failure_observed"]
        interventions = [event for event in events if event.event_type == "intervention_applied"]
        edits = [event for event in events if event.event_type == "file_edited"]
        mcp_calls = [
            event
            for event in events
            if event.event_type == "mcp_tool_called"
            and event.payload.get("server") == "experiment_os"
        ]
        dependency_edits = [event for event in edits if _looks_like_dependency_edit(event.payload)]
        migration_edits = [event for event in edits if _looks_like_migration_edit(event.payload)]
        test_edits = [event for event in edits if _looks_like_test_edit(event.payload)]
        vendor_edits = [event for event in edits if _looks_like_vendor_edit(event.payload)]
        harness_edits = [event for event in edits if _looks_like_harness_edit(event.payload)]
        local_drizzle_kit_version = _checked_version(events, "drizzle-kit")

        return {
            "event_count": len(events),
            "inspected_package_versions_before_edit": _before_first_edit(
                package_version_indices, first_edit_index
            ),
            "inspected_migration_conventions_before_edit": _before_first_edit(
                migration_inspection_indices, first_edit_index
            ),
            "inspected_local_api_surface_before_edit": _before_first_edit(
                api_surface_inspection_indices, first_edit_index
            ),
            "tests_run": len(test_runs),
            "tests_passing": bool(test_outcomes) and test_outcomes[-1] is True,
            "test_failure_count": sum(1 for outcome in test_outcomes if outcome is False),
            "failure_count": len(failures),
            "intervention_count": len(interventions),
            "file_edit_count": len(edits),
            "wrong_file_edits": _wrong_file_edits(edits),
            "dependency_changed": bool(dependency_edits),
            "dependency_edit_count": len(dependency_edits),
            "rewrote_migration_history": bool(migration_edits),
            "migration_history_edit_count": len(migration_edits),
            "test_edit_count": len(test_edits),
            "vendor_edit_count": len(vendor_edits),
            "harness_edit_count": len(harness_edits),
            "forbidden_edit_count": len(test_edits) + len(vendor_edits) + len(harness_edits),
            "preserved_local_version_constraint": (
                local_drizzle_kit_version == "0.31.1" and not dependency_edits
            ),
            "blind_issue_version_alignment": (
                local_drizzle_kit_version == "0.31.1" and bool(dependency_edits)
            ),
            "mcp_tool_call_count": len(mcp_calls),
            "mcp_pre_work_protocol_called": _mcp_tool_called(
                mcp_calls,
                "start_pre_work_protocol",
            ),
            "mcp_dependency_graph_loaded": _mcp_tool_called(
                mcp_calls,
                "get_agent_dependency_graph",
            )
            or _mcp_tool_called(mcp_calls, "resolve_dependencies"),
            "mcp_dependencies_resolved_before_edit": _mcp_dependency_before_edit(events),
            "mcp_final_answer_recorded": _mcp_recorded_event(mcp_calls, "final_answer"),
            "mcp_summary_requested": _mcp_tool_called(mcp_calls, "summarize_run"),
            "no_edit_decision_recorded": any(
                event.event_type == "no_edit_decision" for event in events
            ),
            "source_issue_opened_before_decision": _event_before_any(
                events,
                "source_issue_opened",
                {"file_edited", "no_edit_decision"},
            ),
            "stale_api_usage_count": _count_failure_type(failures, "stale_library_knowledge"),
            "retry_count": _count_failure_type(failures, "retry"),
        }


def _first_index(events: list[RunEvent], event_type: str) -> int | None:
    for event in events:
        if event.event_type == event_type:
            return event.step_index
    return None


def _before_first_edit(indices: list[int], first_edit_index: int | None) -> bool:
    if not indices:
        return False
    if first_edit_index is None:
        return True
    return min(indices) < first_edit_index


def _looks_like_migration_inspection(payload: dict) -> bool:
    text = " ".join(
        [
            *_payload_paths(payload),
            str(payload.get("reason", "")),
            str(payload.get("purpose", "")),
            str(payload.get("finding", "")),
        ]
    ).lower()
    return "migration" in text


def _looks_like_api_surface_inspection(payload: dict) -> bool:
    text = " ".join(
        [
            *_payload_paths(payload),
            str(payload.get("reason", "")),
            str(payload.get("purpose", "")),
            str(payload.get("finding", "")),
            str(payload.get("api", "")),
        ]
    ).lower()
    return any(
        token in text
        for token in [
            "vendor_sdk",
            "responses_create",
            "chat_completions_create",
            "api surface",
            "local api",
        ]
    )


def _wrong_file_edits(edits: list[RunEvent]) -> int:
    count = 0
    for event in edits:
        paths = _payload_paths(event.payload)
        if paths and not any(_looks_like_allowed_drizzle_task_edit(path.lower()) for path in paths):
            count += 1
    return count


def _looks_like_allowed_drizzle_task_edit(path: str) -> bool:
    return (
        path.endswith("package.json")
        or "src/db/schema" in path
        or "drizzle.config" in path
        or "drizzle/migrations/" in path
        or "/migrations/" in path
        or path.endswith("agent_client/client.py")
        or path.endswith("agent_client/routing.py")
    )


def _looks_like_dependency_edit(payload: dict) -> bool:
    return any(
        path.endswith("package.json")
        or path.endswith("package-lock.json")
        or "pnpm-lock" in path
        for path in (item.lower() for item in _payload_paths(payload))
    )


def _looks_like_migration_edit(payload: dict) -> bool:
    return any(
        "drizzle/migrations" in path or "/migrations/" in path
        for path in (item.lower() for item in _payload_paths(payload))
    )


def _looks_like_test_edit(payload: dict) -> bool:
    return any(
        path.startswith("tests/")
        or "/tests/" in path
        or path.startswith("test/")
        or path.endswith(".test.ts")
        or path.endswith(".spec.ts")
        for path in (item.lower() for item in _payload_paths(payload))
    )


def _looks_like_vendor_edit(payload: dict) -> bool:
    return any(
        "vendor" in path or path.endswith("agent_client/vendor_sdk.py")
        for path in (item.lower() for item in _payload_paths(payload))
    )


def _looks_like_harness_edit(payload: dict) -> bool:
    return any(
        path.startswith("scripts/")
        or "/scripts/" in path
        or "harness" in path
        for path in (item.lower() for item in _payload_paths(payload))
    )


def _checked_version(events: list[RunEvent], package: str) -> str | None:
    package = package.lower()
    for event in events:
        if event.event_type != "package_version_checked":
            continue
        if str(event.payload.get("package", "")).lower() == package:
            version = event.payload.get("version")
            if version is not None:
                return str(version)
        for key in ("package_json", "dependencies"):
            versions = event.payload.get(key)
            if isinstance(versions, dict):
                version = versions.get(package)
                if version is not None:
                    return str(version)
    return None


def _mcp_tool_called(events: list[RunEvent], tool: str) -> bool:
    return any(event.payload.get("tool") == tool for event in events)


def _mcp_recorded_event(events: list[RunEvent], event_type: str) -> bool:
    return any(
        event.payload.get("tool") == "record_run_event"
        and event.payload.get("recorded_event_type") == event_type
        for event in events
    )


def _mcp_dependency_before_edit(events: list[RunEvent]) -> bool:
    for event in events:
        if event.event_type == "file_edited":
            return False
        if event.event_type != "mcp_tool_called":
            continue
        if event.payload.get("server") != "experiment_os":
            continue
        if event.payload.get("tool") in {
            "start_pre_work_protocol",
            "get_agent_dependency_graph",
            "resolve_dependencies",
        }:
            return True
    return False


def _event_before_any(
    events: list[RunEvent],
    source_event_type: str,
    target_event_types: set[str],
) -> bool:
    seen_source = False
    for event in events:
        if event.event_type == source_event_type:
            seen_source = True
        if event.event_type in target_event_types:
            return seen_source
    return False


def _count_failure_type(failures: list[RunEvent], failure_type: str) -> int:
    return sum(1 for event in failures if event.payload.get("failure_type") == failure_type)


def _test_outcome(payload: dict) -> bool | None:
    passed = payload.get("passed")
    if isinstance(passed, bool):
        return passed

    exit_code = payload.get("exit_code")
    if isinstance(exit_code, int):
        return exit_code == 0

    status = str(
        payload.get("status") or payload.get("outcome") or payload.get("result") or ""
    ).lower()
    if status in {"passed", "pass", "success", "succeeded", "ok"}:
        return True
    if status in {"failed", "fail", "failure", "error"}:
        return False
    return None


def _payload_paths(payload: dict) -> list[str]:
    values: list[str] = []
    for key in ("path", "file"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            values.append(value)

    files = payload.get("files")
    if isinstance(files, list):
        values.extend(item for item in files if isinstance(item, str) and item)
    elif isinstance(files, str) and files:
        values.append(files)
    return values
