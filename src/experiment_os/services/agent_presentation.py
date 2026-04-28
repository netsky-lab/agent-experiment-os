from typing import Any

from experiment_os.domain.schemas import BriefRequest


class AgentWorkContextPresenter:
    """Build the compact contract an agent should follow before editing."""

    def present(
        self,
        *,
        request: BriefRequest,
        brief: dict[str, Any],
        dependencies: dict[str, Any],
        agent_dependency_graph: dict[str, Any],
        run: dict[str, Any] | None,
    ) -> dict[str, Any]:
        candidate_pages = brief.get("content", {}).get("candidate_pages", [])
        return {
            "version": "agent_work_context.v1",
            "task": request.task,
            "repo": request.repo,
            "libraries": request.libraries,
            "brief_id": brief["brief_id"],
            "run_id": run["run_id"] if run else None,
            "required_load_order": agent_dependency_graph["load_order"],
            "knowledge_boundaries": _knowledge_boundaries(candidate_pages),
            "required_checks": _required_checks(candidate_pages),
            "forbidden_actions": _forbidden_actions(candidate_pages),
            "decision_rules": _decision_rules(agent_dependency_graph),
            "known_failures": _known_failures(agent_dependency_graph),
            "evidence": _evidence_nodes(agent_dependency_graph),
            "presentation_contract": _presentation_contract(
                agent_dependency_graph=agent_dependency_graph,
                candidate_pages=candidate_pages,
            ),
            "tool_sequence": [
                "Load required_load_order before the first edit.",
                "Inspect local versions, local API surface, and repository conventions.",
                "Treat sources and claims as evidence only; verify local facts before acting.",
                "Make the smallest local change that satisfies the repo oracle.",
                "Run the required verification commands.",
                "Record final_answer and summarize_run when run_id is present.",
            ],
            "event_contract": {
                "before_edit": [
                    "brief_loaded",
                    "dependency_resolved",
                    "package_version_checked",
                    "file_inspected",
                ],
                "during_work": ["file_edited", "failure_observed", "intervention_applied"],
                "after_edit": ["test_run", "final_answer"],
            },
            "completion_contract": {
                "must_report": [
                    "local facts inspected",
                    "files changed",
                    "verification commands and outcomes",
                    "external evidence used only as evidence",
                ],
                "must_not_claim": [
                    "policy promotion without matrix evidence",
                    "dependency upgrade necessity without local proof",
                    "success without final verification",
                ],
            },
            "truncated": dependencies.get("truncated", False)
            or brief.get("content", {}).get("truncated", False),
        }


def _knowledge_boundaries(pages: list[dict[str, Any]]) -> dict[str, list[str]]:
    return {
        "decision_capable": [
            page["id"]
            for page in pages
            if page.get("status") == "accepted" and page.get("type") in {"policy", "intervention"}
        ],
        "domain_context": [
            page["id"]
            for page in pages
            if page.get("status") == "accepted" and page.get("type") == "knowledge_card"
        ],
        "evidence_only": [
            page["id"]
            for page in pages
            if page.get("type") in {"source", "claim"} or page.get("status") != "accepted"
        ],
    }


def _required_checks(pages: list[dict[str, Any]]) -> list[str]:
    checks: list[str] = []
    for page in pages:
        metadata = page.get("metadata", {})
        checks.extend(metadata.get("recommendedChecks", []))
        checks.extend(metadata.get("requiredChecks", []))
    return _unique(checks)


def _forbidden_actions(pages: list[dict[str, Any]]) -> list[str]:
    actions = [
        "Do not apply issue-derived fixes until local package versions and local code paths are inspected.",
        "Do not edit tests, vendor shims, dependency metadata, or migration history unless local evidence requires it.",
    ]
    for page in pages:
        actions.extend(page.get("metadata", {}).get("forbiddenActions", []))
    return _unique(actions)


def _decision_rules(agent_dependency_graph: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "page_id": node["id"],
            "title": node["title"],
            "role": node["role"],
            "appliesTo": node.get("appliesTo", {}),
            "summary": node.get("summary", ""),
        }
        for node in agent_dependency_graph.get("nodes", [])
        if node.get("role") in {"decision_rule", "intervention"} and not node.get("evidence_only")
    ]


def _known_failures(agent_dependency_graph: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "page_id": node["id"],
            "title": node["title"],
            "summary": node.get("summary", ""),
            "dependsOn": node.get("dependsOn", []),
        }
        for node in agent_dependency_graph.get("nodes", [])
        if node.get("role") == "failure_mode"
    ]


def _evidence_nodes(agent_dependency_graph: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "page_id": node["id"],
            "title": node["title"],
            "summary": node.get("summary", ""),
            "dependsOn": node.get("dependsOn", []),
        }
        for node in agent_dependency_graph.get("nodes", [])
        if node.get("evidence_only")
    ]


def _presentation_contract(
    *,
    agent_dependency_graph: dict[str, Any],
    candidate_pages: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "version": "agent_presentation_contract.v1",
        "must_load": agent_dependency_graph.get("load_order", []),
        "dependsOn": agent_dependency_graph.get("edges", []),
        "decision_rules": _decision_rules(agent_dependency_graph),
        "known_failures": _known_failures(agent_dependency_graph),
        "evidence_only": _evidence_nodes(agent_dependency_graph),
        "required_before_edit": [
            "Load every must_load page and its dependsOn edges.",
            "Inspect local versions and local API surfaces mentioned in required checks.",
            "Treat external issues and claims as evidence only until local facts match.",
            "Reject dependency/test/vendor edits unless required by local evidence.",
        ],
        "review_boundaries": {
            "can_apply_without_review": _knowledge_boundaries(candidate_pages)["decision_capable"],
            "requires_human_review": _knowledge_boundaries(candidate_pages)["evidence_only"],
        },
    }


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))
