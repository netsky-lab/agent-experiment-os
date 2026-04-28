from experiment_os.domain.schemas import BriefRequest
from experiment_os.services.briefs import BriefCompiler
from experiment_os.services.protocol import AgentWorkProtocol


def test_brief_compiler_returns_required_pages_and_ranking(session):
    brief = BriefCompiler(session).compile(
        BriefRequest(
            task="Fix shell escaping in a Drizzle migration task",
            libraries=["drizzle"],
            agent="opencode",
            model="gemma",
            toolchain="shell",
        )
    )

    assert "policy.opencode-gemma-shell-escaping" in brief["required_pages"]
    assert "knowledge.drizzle-migration-defaults" in brief["required_pages"]
    assert brief["content"]["ranking"]
    agent_graph = brief["content"]["agent_dependency_graph"]
    assert agent_graph["version"] == "agent_dependency_graph.v1"
    assert "policy.opencode-gemma-shell-escaping" in agent_graph["load_order"]
    assert any(node["role"] == "decision_rule" for node in agent_graph["nodes"])
    assert brief["content"]["truncated"] is False


def test_brief_compiler_prunes_by_token_budget(session):
    brief = BriefCompiler(session).compile(
        BriefRequest(
            task="Fix shell escaping in a Drizzle migration task",
            libraries=["drizzle"],
            agent="opencode",
            model="gemma",
            toolchain="shell",
            token_budget=20,
        )
    )

    assert brief["content"]["candidate_pages"]
    assert brief["content"]["truncated"] is True


def test_brief_compiler_returns_api_drift_knowledge_and_agent_context(session):
    request = BriefRequest(
        task="Fix Python SDK API drift wrapper failure",
        libraries=["example-llm-sdk", "python"],
        agent="codex",
        toolchain="shell",
    )

    protocol = AgentWorkProtocol(session).start(request=request)

    brief = protocol["brief"]
    context = protocol["agent_work_context"]

    assert "knowledge.python-api-drift-local-shim" in brief["required_pages"]
    assert "knowledge.python-api-drift-local-shim" in context["required_load_order"]
    assert any("vendor_sdk.py" in item for item in context["required_checks"])
    assert any("Do not edit tests" in item for item in context["forbidden_actions"])
    assert "claim.issue.example-llm-sdk.upgrade-advice" in context["knowledge_boundaries"]["evidence_only"]
    presentation = context["presentation_contract"]
    assert presentation["version"] == "agent_presentation_contract.v1"
    assert "knowledge.python-api-drift-local-shim" in presentation["must_load"]
    assert "dependsOn" in presentation
    assert presentation["required_before_edit"]
