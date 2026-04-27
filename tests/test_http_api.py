from pathlib import Path

from fastapi.testclient import TestClient

from experiment_os.domain.schemas import BriefRequest, WikiPageInput
from experiment_os.http_api import create_app
from experiment_os.repositories.wiki import WikiRepository
from experiment_os.services.briefs import BriefCompiler
from experiment_os.services.experiments import ExperimentRunner


def test_http_api_exposes_dashboard_read_models(session):
    ExperimentRunner(session).run_drizzle_fixture()
    ExperimentRunner(session).run_shell_condition(
        condition_id="condition.001-drizzle-brief-assisted",
        command="echo 'npm test passed'",
        workdir=Path("."),
        run_metadata={
            "matrix_id": "matrix.http",
            "matrix_kind": "version_trap",
            "matrix_condition": "static_brief",
        },
    )
    brief = BriefCompiler(session).compile(
        BriefRequest(
            task="Fix Drizzle migration default behavior",
            libraries=["drizzle"],
            agent="codex",
            toolchain="shell",
        )
    )
    WikiRepository(session).upsert_page(
        WikiPageInput(
            id="policy.candidate.http",
            type="policy",
            title="HTTP policy candidate",
            status="draft",
            confidence="medium",
            summary="A policy candidate.",
            metadata={"review_required": True},
        )
    )
    session.commit()
    client = TestClient(create_app())

    experiments = client.get("/experiments")
    graph = client.get(f"/briefs/{brief['brief_id']}/evidence-graph")
    matrix = client.get("/experiments/experiment.001-drizzle-brief/matrix")
    policies = client.get("/policy-candidates")

    assert experiments.status_code == 200
    assert experiments.json()["experiments"]
    assert graph.status_code == 200
    assert graph.json()["graph"]["nodes"]
    assert matrix.status_code == 200
    assert matrix.json()["matrices"]
    assert policies.status_code == 200
    assert policies.json()["items"]


def test_http_api_exposes_agent_work_context_and_search(session):
    client = TestClient(create_app())

    brief_response = client.post(
        "/briefs",
        json={
            "task": "Fix Python SDK API drift wrapper failure",
            "libraries": ["example-llm-sdk", "python"],
            "agent": "codex",
            "toolchain": "shell",
            "token_budget": 2000,
        },
    )
    assert brief_response.status_code == 200
    brief = brief_response.json()

    context_response = client.get(
        f"/briefs/{brief['brief_id']}/agent-work-context",
    )
    knowledge_response = client.post(
        "/knowledge/search",
        json={
            "query": "python api drift local shim",
            "libraries": ["example-llm-sdk"],
            "page_types": ["knowledge_card"],
        },
    )
    issue_response = client.post(
        "/issue-knowledge/search",
        json={
            "library": "example-llm-sdk",
            "topic": "upgrade advice api drift",
            "limit": 5,
        },
    )

    assert context_response.status_code == 200
    context = context_response.json()
    assert context["version"] == "agent_work_context.v1"
    assert "knowledge.python-api-drift-local-shim" in context["required_load_order"]
    assert knowledge_response.status_code == 200
    assert knowledge_response.json()["results"]
    assert issue_response.status_code == 200
    assert any(
        item["id"] == "claim.issue.example-llm-sdk.upgrade-advice"
        for item in issue_response.json()["results"]
    )


def test_http_api_review_status_accepts_rationale(session):
    WikiRepository(session).upsert_page(
        WikiPageInput(
            id="policy.candidate.http-status",
            type="policy",
            title="HTTP status policy",
            status="draft",
            confidence="medium",
            summary="A policy candidate.",
            metadata={"review_required": True},
        )
    )
    session.commit()
    client = TestClient(create_app())

    response = client.post(
        "/review-actions/policy.candidate.http-status/status",
        json={
            "status": "accepted",
            "rationale": "Evidence reviewed.",
            "reviewer": "maintainer",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert body["metadata"]["review"]["rationale"] == "Evidence reviewed."
