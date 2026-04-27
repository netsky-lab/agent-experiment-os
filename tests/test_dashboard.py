from experiment_os.services.dashboard import DashboardReadService
from experiment_os.services.experiments import ExperimentRunner
from experiment_os.domain.schemas import BriefRequest, WikiPageInput
from experiment_os.repositories.wiki import WikiRepository
from experiment_os.services.briefs import BriefCompiler


def test_dashboard_lists_experiments_and_run_detail(session):
    fixture = ExperimentRunner(session).run_drizzle_fixture()
    run_id = fixture["results"][0]["run"]["run_id"]

    dashboard = DashboardReadService(session)
    experiments = dashboard.list_experiments()
    detail = dashboard.experiment_detail("experiment.001-drizzle-brief")
    run = dashboard.run_detail(run_id)

    assert experiments["experiments"]
    assert detail["conditions"]
    assert run["timeline"]
    assert "metrics" in run


def test_dashboard_exposes_evidence_graph_and_review_actions(session):
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
            id="claim.test.dashboard",
            type="claim",
            title="Dashboard claim",
            status="draft",
            confidence="low",
            summary="A claim for review actions.",
            metadata={"claim_type": "problem", "source_page_id": "source.test"},
        )
    )
    dashboard = DashboardReadService(session)
    graph = dashboard.evidence_graph(brief_id=brief["brief_id"])
    actions = dashboard.review_actions("claim.test.dashboard")

    assert graph["graph"]["nodes"]
    assert "evidence" in graph["legend"]
    assert any(action["id"] == "promote_policy" for action in actions["actions"])
