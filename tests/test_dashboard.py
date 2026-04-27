from experiment_os.services.dashboard import DashboardReadService
from experiment_os.services.experiments import ExperimentRunner


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
