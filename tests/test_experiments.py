from experiment_os.services.experiments import ExperimentRunner


def test_drizzle_fixture_produces_baseline_and_brief_metrics(session):
    result = ExperimentRunner(session).run_drizzle_fixture()
    by_condition = {item["condition"]: item for item in result["results"]}

    assert by_condition["baseline"]["metrics"]["stale_api_usage_count"] == 1
    assert by_condition["baseline"]["metrics"]["inspected_package_versions_before_edit"] is False
    assert by_condition["brief-assisted"]["metrics"]["inspected_package_versions_before_edit"] is True
    assert by_condition["brief-assisted"]["metrics"]["tests_passing"] is True

