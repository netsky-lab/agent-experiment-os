from typing import Any


class AgentDependencyGraphPresenter:
    """Build the compact dependency graph an agent should load before work."""

    def present(
        self,
        *,
        required_pages: list[str],
        recommended_pages: list[str],
        dependency_graph: dict[str, Any],
    ) -> dict[str, Any]:
        pages = dependency_graph.get("pages", [])
        required = set(required_pages)
        recommended = set(recommended_pages)
        nodes = [_node(page, required, recommended) for page in pages]
        edges = dependency_graph.get("edges") or _edges_from_pages(pages)
        return {
            "version": "agent_dependency_graph.v1",
            "load_order": [node["id"] for node in nodes if node["load_required"]],
            "nodes": nodes,
            "edges": edges,
            "instructions": [
                "Load every node marked load_required before editing.",
                "Use policy and intervention nodes as decision rules only when appliesTo matches.",
                "Use source and claim nodes as evidence; verify versions and local facts before acting.",
                "Record brief_loaded and dependency_resolved before the first file edit.",
            ],
            "truncated": dependency_graph.get("truncated", False),
        }


def _node(page: dict[str, Any], required: set[str], recommended: set[str]) -> dict[str, Any]:
    page_id = page["id"]
    page_type = page.get("type")
    status = page.get("status")
    evidence_only = page_type in {"source", "claim"} or status not in {"accepted", None}
    load_required = page_id in required or page_id in recommended
    return {
        "id": page_id,
        "type": page_type,
        "title": page.get("title", page_id),
        "status": status,
        "confidence": page.get("confidence"),
        "summary": page.get("summary", ""),
        "role": _role(page_type, evidence_only),
        "load_required": load_required,
        "evidence_only": evidence_only,
        "appliesTo": page.get("metadata", {}).get("appliesTo", {}),
        "dependsOn": page.get("dependsOn", []),
    }


def _role(page_type: str | None, evidence_only: bool) -> str:
    if evidence_only:
        return "evidence"
    return {
        "policy": "decision_rule",
        "knowledge_card": "domain_knowledge",
        "failure": "failure_mode",
        "intervention": "intervention",
        "run_report": "prior_observation",
    }.get(page_type or "", "context")


def _edges_from_pages(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for page in pages:
        for target in page.get("dependsOn", []):
            edges.append({"source": page["id"], "target": target, "type": "dependsOn"})
    return edges
