from pathlib import Path

from fastapi.testclient import TestClient

from experiment_os.domain.schemas import BriefRequest, WikiPageInput
from experiment_os.http_api import create_app
from experiment_os.repositories.wiki import WikiRepository
from experiment_os.services.briefs import BriefCompiler
from experiment_os.services.experiments import ExperimentRunner
from experiment_os.services.issues import GitHubIssueIngestor


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
    ExperimentRunner(session).run_shell_condition(
        condition_id="condition.001-drizzle-brief-assisted",
        command="echo 'npm test failed'; echo 'npm test passed'",
        workdir=Path("."),
        run_metadata={
            "matrix_id": "matrix.http-right",
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
    latest_matrix = client.get("/experiments/experiment.001-drizzle-brief/matrix/latest")
    latest_comparison = client.get(
        "/experiments/experiment.001-drizzle-brief/matrix/latest-comparison"
    )
    story = client.get("/experiments/experiment.001-drizzle-brief/story")
    compliance = client.get("/experiments/experiment.001-drizzle-brief/protocol-compliance")
    comparison = client.get(
        "/experiments/experiment.001-drizzle-brief/matrix/compare",
        params={
            "left_matrix_id": "matrix.http",
            "right_matrix_id": "matrix.http-right",
        },
    )
    regression = client.get(
        "/experiments/experiment.001-drizzle-brief/matrix/regression",
        params={
            "left_matrix_id": "matrix.http",
            "right_matrix_id": "matrix.http-right",
        },
    )
    policies = client.get("/policy-candidates")
    churn = client.get(
        "/experiments/experiment.001-drizzle-brief/churn",
        params={"matrix_id": "matrix.http-right"},
    )
    latest_churn = client.get("/experiments/experiment.001-drizzle-brief/churn/latest")
    categories = client.get("/policy-candidates/categories")
    ui_contract = client.get("/ui/contract")
    ui_bootstrap = client.get(
        "/ui/bootstrap",
        params={"experiment_id": "experiment.001-drizzle-brief"},
    )
    wiki_graph = client.get("/wiki/graph")
    stale = client.get("/knowledge/stale")
    duplicates = client.get("/knowledge/duplicates")
    app_index = client.get("/app/")

    assert experiments.status_code == 200
    assert experiments.json()["experiments"]
    assert graph.status_code == 200
    assert graph.json()["graph"]["nodes"]
    assert matrix.status_code == 200
    assert matrix.json()["matrices"]
    assert latest_matrix.status_code == 200
    assert latest_matrix.json()["matrix"]["matrix_id"] == "matrix.http-right"
    assert latest_comparison.status_code == 200
    assert latest_comparison.json()["comparison"]["right_matrix_id"] == "matrix.http-right"
    assert story.status_code == 200
    assert story.json()["latest_matrix"]["matrix_id"] == "matrix.http-right"
    assert compliance.status_code == 200
    assert compliance.json()["matrices"]
    assert comparison.status_code == 200
    assert comparison.json()["comparison"]["right_matrix_id"] == "matrix.http-right"
    assert regression.status_code == 200
    assert regression.json()["regression"]["status"] == "regressed"
    assert policies.status_code == 200
    assert policies.json()["items"]
    assert churn.status_code == 200
    assert churn.json()["matrices"][0]["conditions"]["static_brief"]["runs"][0]["needs_review"] is True
    assert latest_churn.status_code == 200
    assert latest_churn.json()["items"]
    assert categories.status_code == 200
    assert categories.json()["categories"]
    assert ui_contract.status_code == 200
    assert any(surface["id"] == "MatrixCompare" for surface in ui_contract.json()["surfaces"])
    assert any(surface["id"] == "ExperimentStory" for surface in ui_contract.json()["surfaces"])
    assert ui_bootstrap.status_code == 200
    assert ui_bootstrap.json()["contract"]["version"] == "ui_contract.v1"
    assert ui_bootstrap.json()["story"]["experiment"]["id"] == "experiment.001-drizzle-brief"
    assert wiki_graph.status_code == 200
    assert wiki_graph.json()["nodes"]
    assert stale.status_code == 200
    assert "items" in stale.json()
    assert duplicates.status_code == 200
    assert "items" in duplicates.json()
    assert app_index.status_code == 200
    assert "Agent Experiment OS" in app_index.text


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
    preview_response = client.get(
        f"/briefs/{brief['brief_id']}/presentation-preview",
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
            "limit": 20,
        },
    )

    assert context_response.status_code == 200
    assert preview_response.status_code == 200
    assert preview_response.json()["presentation_contract"]["must_load"]
    context = context_response.json()
    assert context["version"] == "agent_work_context.v1"
    assert context["presentation_contract"]["must_load"]
    assert "knowledge.python-api-drift-local-shim" in context["required_load_order"]
    assert knowledge_response.status_code == 200
    assert knowledge_response.json()["results"]
    assert issue_response.status_code == 200
    assert any(
        item["id"] == "claim.issue.example-llm-sdk.upgrade-advice"
        for item in issue_response.json()["results"]
    )


def test_http_api_exposes_lifecycle_and_issue_version_alignment(session):
    ExperimentRunner(session).seed_drizzle_experiment()
    GitHubIssueIngestor(session).ingest(
        repo="drizzle-team/drizzle-orm",
        query="migration default",
        issues=[
            {
                "number": 5661,
                "title": "Migration default regression",
                "body": """
### What version of `drizzle-orm` are you using?
1.0.0-beta.22
""",
                "html_url": "https://github.com/drizzle-team/drizzle-orm/issues/5661",
                "url": "https://api.github.com/repos/drizzle-team/drizzle-orm/issues/5661",
                "state": "open",
                "labels": [{"name": "bug"}],
            }
        ],
    )
    session.commit()
    client = TestClient(create_app())

    status = client.post(
        "/experiments/experiment.001-drizzle-brief/status",
        json={"status": "running", "rationale": "Matrix started."},
    )
    alignment = client.post(
        "/issue-knowledge/claim.github-issue.drizzle-team.drizzle-orm.5661.versions/version-alignment",
        json={"local_versions": {"drizzle-orm": "0.44.5"}},
    )

    assert status.status_code == 200
    assert status.json()["status"] == "running"
    assert alignment.status_code == 200
    assert alignment.json()["status"] == "mismatch"


def test_http_api_exposes_run_completion_and_page_provenance(session, tmp_path):
    result = ExperimentRunner(session).run_shell_condition(
        condition_id="condition.001-drizzle-brief-assisted",
        command="echo 'npm test passed'",
        workdir=tmp_path,
        run_metadata={"matrix_id": "matrix.completion-http"},
    )
    WikiRepository(session).upsert_page(
        WikiPageInput(
            id="source.test.provenance",
            type="source",
            title="Source provenance",
            status="accepted",
            confidence=None,
            summary="A source page.",
            metadata={
                "allowed_use": "evidence_only",
                "source_updated_at": "2026-04-28T00:00:00+00:00",
                "retrieved_at": "2026-04-27T00:00:00+00:00",
            },
        )
    )
    session.commit()
    client = TestClient(create_app())

    completion = client.get(f"/runs/{result['run']['run_id']}/completion-contract")
    next_action = client.get(f"/runs/{result['run']['run_id']}/next-required-action")
    provenance = client.get("/pages/source.test.provenance/provenance")

    assert completion.status_code == 200
    assert completion.json()["status"] == "failed"
    assert "pre_work_missing" in completion.json()["violations"]
    assert next_action.status_code == 200
    assert next_action.json()["next_action"]["id"] == "start_pre_work_protocol"
    assert provenance.status_code == 200
    assert provenance.json()["freshness"]["stale_warning"] is True


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
            "evidence_ids": ["run.http-status"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert body["metadata"]["review"]["rationale"] == "Evidence reviewed."
    assert body["metadata"]["review"]["evidence_ids"] == ["run.http-status"]
