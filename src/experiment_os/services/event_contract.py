from typing import Any


class AgentEventContract:
    """Agent-facing contract for explicit MCP event recording."""

    def as_dict(self) -> dict[str, Any]:
        return {
            "version": "experiment_os.agent_events.v1",
            "recording_rule": (
                "Record events through MCP record_run_event as soon as the observation happens. "
                "Do not wait for the final answer to reconstruct the timeline."
            ),
            "required_before_first_edit": [
                "brief_loaded",
                "dependency_resolved",
                "package_version_checked",
                "file_inspected",
            ],
            "event_types": [
                {
                    "type": "brief_loaded",
                    "when": "After start_pre_work_protocol returns a brief.",
                    "payload": {"brief_id": "brief.x", "required_pages": [], "recommended_pages": []},
                },
                {
                    "type": "dependency_resolved",
                    "when": "After agent_dependency_graph.load_order has been read.",
                    "payload": {"root_pages": [], "dependency_pages": []},
                },
                {
                    "type": "package_version_checked",
                    "when": "After checking package manifests, lockfiles, or installed package views.",
                    "payload": {"package": "drizzle-orm", "version": "1.0.0-beta.22", "source": "package.json"},
                },
                {
                    "type": "file_inspected",
                    "when": "After reading a file that informs the decision.",
                    "payload": {"path": "src/db/schema.ts", "reason": "verify default convention"},
                },
                {
                    "type": "file_edited",
                    "when": "Immediately after editing a file.",
                    "payload": {"path": "package.json", "reason": "minimal version alignment"},
                },
                {
                    "type": "failure_observed",
                    "when": "When a command, tool call, test, or reasoning assumption fails.",
                    "payload": {"failure_type": "command_failed", "severity": "low", "evidence": "..."},
                },
                {
                    "type": "intervention_applied",
                    "when": "When applying a known intervention from the dependency graph.",
                    "payload": {
                        "intervention": "intervention.command-normalization",
                        "target_failure": "failure.shell-escaping",
                        "summary": "split command into smaller steps",
                    },
                },
                {
                    "type": "test_run",
                    "when": "After a verification command completes.",
                    "payload": {"command": "npm test", "passed": True, "summary": "toy repo test passed"},
                },
                {
                    "type": "final_answer",
                    "when": "Immediately before final response.",
                    "payload": {"outcome": "passed", "summary": "no code change needed"},
                },
            ],
            "anti_patterns": [
                "Do not record raw issue claims as policy decisions.",
                "Do not mark tests as passing before the command completes.",
                "Do not record file_edited for files only inspected.",
            ],
        }


def event_contract_prompt() -> str:
    contract = AgentEventContract().as_dict()
    event_types = ", ".join(event["type"] for event in contract["event_types"])
    return (
        "Use Experiment OS MCP as the event recorder. After start_pre_work_protocol, keep the "
        f"run_id and record high-signal events with record_run_event. Event types: {event_types}. "
        "Before the first file edit, record package_version_checked and file_inspected for the "
        "facts that justify the edit. Before final answer, record final_answer and call summarize_run."
    )
