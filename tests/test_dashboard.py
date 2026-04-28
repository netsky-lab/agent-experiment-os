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


def test_dashboard_exposes_matrix_projection(session, tmp_path):
    ExperimentRunner(session).run_shell_condition(
        condition_id="condition.001-drizzle-brief-assisted",
        command="echo 'npm test passed'",
        workdir=tmp_path,
        timeout_seconds=30,
        run_metadata={
            "matrix_id": "matrix.test",
            "matrix_kind": "version_trap",
            "matrix_condition": "static_brief",
        },
    )

    dashboard = DashboardReadService(session)
    matrix = dashboard.experiment_matrix("experiment.001-drizzle-brief")
    latest = dashboard.latest_experiment_matrix("experiment.001-drizzle-brief")
    compliance = dashboard.protocol_compliance("experiment.001-drizzle-brief")
    matrices = {item["matrix_id"]: item for item in matrix["matrices"]}

    assert "matrix.test" in matrices
    assert "static_brief" in matrices["matrix.test"]["conditions"]
    assert "protocol_compliance" in matrices["matrix.test"]["conditions"]["static_brief"]
    assert latest["matrix"]["matrix_id"] == "matrix.test"
    assert latest["matrix"]["run_count"] >= 1
    assert compliance["matrices"]
    assert "overall" in compliance["matrices"][0]
    assert "quality_signals" in matrices["matrix.test"]["conditions"]["static_brief"]


def test_dashboard_exposes_latest_comparison_story_and_categories(session, tmp_path):
    ExperimentRunner(session).run_shell_condition(
        condition_id="condition.001-drizzle-brief-assisted",
        command="echo 'npm test passed'",
        workdir=tmp_path,
        timeout_seconds=30,
        run_metadata={
            "matrix_id": "matrix.story-left",
            "matrix_kind": "version_trap",
            "matrix_condition": "static_brief",
        },
    )
    ExperimentRunner(session).run_shell_condition(
        condition_id="condition.001-drizzle-brief-assisted",
        command="echo 'npm test failed'; echo 'npm test passed'",
        workdir=tmp_path,
        timeout_seconds=30,
        run_metadata={
            "matrix_id": "matrix.story-right",
            "matrix_kind": "version_trap",
            "matrix_condition": "static_brief",
        },
    )
    WikiRepository(session).upsert_page(
        WikiPageInput(
            id="policy.candidate.story-churn",
            type="policy",
            title="Review red-green churn before accepting agent policy",
            status="draft",
            confidence="medium",
            summary="Churn policy candidate.",
            metadata={"review_required": True, "source_signal": "red_green_churn"},
        )
    )

    dashboard = DashboardReadService(session)
    comparison = dashboard.latest_matrix_comparison_candidate("experiment.001-drizzle-brief")
    churn = dashboard.latest_churn_runs("experiment.001-drizzle-brief")
    categories = dashboard.policy_candidate_categories()
    story = dashboard.experiment_story("experiment.001-drizzle-brief")

    assert comparison["comparison"]["right_matrix_id"] == "matrix.story-right"
    assert churn["items"][0]["run_id"]
    assert any(category["id"] == "red_green_churn" for category in categories["categories"])
    assert story["latest_matrix"]["matrix_id"] == "matrix.story-right"
    assert story["latest_churn_runs"]


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
    assert any(
        action["id"] == "accept" and "evidence_ids" in action["requires"]
        for action in actions["actions"]
    )


def test_dashboard_lists_policy_candidates(session):
    WikiRepository(session).upsert_page(
        WikiPageInput(
            id="policy.candidate.dashboard",
            type="policy",
            title="Candidate policy",
            status="draft",
            confidence="medium",
            summary="A policy candidate.",
            metadata={"review_required": True},
        )
    )

    candidates = DashboardReadService(session).policy_candidates()

    assert candidates["items"][0]["id"] == "policy.candidate.dashboard"


def test_dashboard_compares_matrices(session, tmp_path):
    ExperimentRunner(session).run_shell_condition(
        condition_id="condition.001-drizzle-brief-assisted",
        command="echo 'npm test passed'",
        workdir=tmp_path,
        timeout_seconds=30,
        run_metadata={
            "matrix_id": "matrix.left",
            "matrix_kind": "version_trap",
            "matrix_condition": "static_brief",
        },
    )
    ExperimentRunner(session).run_shell_condition(
        condition_id="condition.001-drizzle-brief-assisted",
        command="echo 'npm test failed'; echo 'npm test passed'",
        workdir=tmp_path,
        timeout_seconds=30,
        run_metadata={
            "matrix_id": "matrix.right",
            "matrix_kind": "version_trap",
            "matrix_condition": "static_brief",
        },
    )

    comparison = DashboardReadService(session).matrix_comparison(
        "experiment.001-drizzle-brief",
        left_matrix_id="matrix.left",
        right_matrix_id="matrix.right",
    )

    condition = comparison["comparison"]["conditions"]["static_brief"]
    assert condition["quality_signal_deltas"]["red_green_churn_mean"]["right"] == 1


def test_dashboard_exposes_churn_drill_down(session, tmp_path):
    result = ExperimentRunner(session).run_shell_condition(
        condition_id="condition.001-drizzle-brief-assisted",
        command="echo 'npm test failed'; echo 'npm test passed'",
        workdir=tmp_path,
        timeout_seconds=30,
        run_metadata={
            "matrix_id": "matrix.churn",
            "matrix_kind": "version_trap",
            "matrix_condition": "static_brief",
        },
    )
    run_id = result["run"]["run_id"]

    dashboard = DashboardReadService(session)
    run_churn = dashboard.run_churn(run_id)
    experiment_churn = dashboard.experiment_churn(
        "experiment.001-drizzle-brief",
        matrix_id="matrix.churn",
    )

    assert run_churn["churn"]["has_churn"] is True
    assert run_churn["churn"]["recovered"] is True
    assert run_churn["churn"]["failed_verifications"]
    assert experiment_churn["matrices"][0]["conditions"]["static_brief"]["runs"][0]["needs_review"] is True
    assert any(surface["id"] == "ChurnDrillDown" for surface in dashboard.ui_contract()["surfaces"])
