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
