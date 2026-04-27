from fastapi.testclient import TestClient

from experiment_os.domain.schemas import BriefRequest
from experiment_os.http_api import create_app
from experiment_os.services.briefs import BriefCompiler
from experiment_os.services.experiments import ExperimentRunner


def test_http_api_exposes_dashboard_read_models(session):
    ExperimentRunner(session).run_drizzle_fixture()
    brief = BriefCompiler(session).compile(
        BriefRequest(
            task="Fix Drizzle migration default behavior",
            libraries=["drizzle"],
            agent="codex",
            toolchain="shell",
        )
    )
    session.commit()
    client = TestClient(create_app())

    experiments = client.get("/experiments")
    graph = client.get(f"/briefs/{brief['brief_id']}/evidence-graph")

    assert experiments.status_code == 200
    assert experiments.json()["experiments"]
    assert graph.status_code == 200
    assert graph.json()["graph"]["nodes"]
