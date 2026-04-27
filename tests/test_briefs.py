from experiment_os.domain.schemas import BriefRequest
from experiment_os.services.briefs import BriefCompiler


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
