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
        test_runs = [event for event in events if event.event_type == "test_run"]
        failures = [event for event in events if event.event_type == "failure_observed"]
        interventions = [event for event in events if event.event_type == "intervention_applied"]
        edits = [event for event in events if event.event_type == "file_edited"]
        dependency_edits = [event for event in edits if _looks_like_dependency_edit(event.payload)]
        migration_edits = [event for event in edits if _looks_like_migration_edit(event.payload)]
        local_drizzle_kit_version = _checked_version(events, "drizzle-kit")

        return {
            "event_count": len(events),
            "inspected_package_versions_before_edit": _before_first_edit(
                package_version_indices, first_edit_index
            ),
            "inspected_migration_conventions_before_edit": _before_first_edit(
                migration_inspection_indices, first_edit_index
            ),
            "tests_run": len(test_runs),
            "tests_passing": any(event.payload.get("passed") is True for event in test_runs),
            "failure_count": len(failures),
            "intervention_count": len(interventions),
            "file_edit_count": len(edits),
            "wrong_file_edits": _wrong_file_edits(edits),
            "dependency_changed": bool(dependency_edits),
            "dependency_edit_count": len(dependency_edits),
            "rewrote_migration_history": bool(migration_edits),
            "migration_history_edit_count": len(migration_edits),
            "preserved_local_version_constraint": (
                local_drizzle_kit_version == "0.31.1" and not dependency_edits
            ),
            "blind_issue_version_alignment": (
                local_drizzle_kit_version == "0.31.1" and bool(dependency_edits)
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
    path = str(payload.get("path", "")).lower()
    reason = str(payload.get("reason", "")).lower()
    return "migration" in path or "migration" in reason


def _wrong_file_edits(edits: list[RunEvent]) -> int:
    count = 0
    for event in edits:
        path = str(event.payload.get("path", "")).lower()
        if path and not _looks_like_allowed_drizzle_task_edit(path):
            count += 1
    return count


def _looks_like_allowed_drizzle_task_edit(path: str) -> bool:
    return (
        path.endswith("package.json")
        or "src/db/schema" in path
        or "drizzle.config" in path
        or "drizzle/migrations/" in path
        or "/migrations/" in path
    )


def _looks_like_dependency_edit(payload: dict) -> bool:
    path = str(payload.get("path", "")).lower()
    return (
        path.endswith("package.json")
        or path.endswith("package-lock.json")
        or "pnpm-lock" in path
    )


def _looks_like_migration_edit(payload: dict) -> bool:
    path = str(payload.get("path", "")).lower()
    return "drizzle/migrations" in path or "/migrations/" in path


def _checked_version(events: list[RunEvent], package: str) -> str | None:
    package = package.lower()
    for event in events:
        if event.event_type != "package_version_checked":
            continue
        if str(event.payload.get("package", "")).lower() == package:
            version = event.payload.get("version")
            if version is not None:
                return str(version)
    return None


def _count_failure_type(failures: list[RunEvent], failure_type: str) -> int:
    return sum(1 for event in failures if event.payload.get("failure_type") == failure_type)
