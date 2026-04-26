from experiment_os.services.experiments import ExperimentRunner


def test_drizzle_fixture_produces_baseline_and_brief_metrics(session):
    result = ExperimentRunner(session).run_drizzle_fixture()
    by_condition = {item["condition"]: item for item in result["results"]}

    assert by_condition["baseline"]["metrics"]["stale_api_usage_count"] == 1
    assert by_condition["baseline"]["metrics"]["inspected_package_versions_before_edit"] is False
    assert by_condition["brief-assisted"]["metrics"]["inspected_package_versions_before_edit"] is True
    assert by_condition["brief-assisted"]["metrics"]["tests_passing"] is True


def test_shell_condition_captures_artifacts_and_metrics(session, tmp_path):
    result = ExperimentRunner(session).run_shell_condition(
        condition_id="condition.001-drizzle-brief-assisted",
        command=(
            "printf 'brief=%s\\n' \"$EXPERIMENT_OS_BRIEF_PATH\"; "
            "echo 'drizzle-orm@1.0.0-beta.22'; "
            "echo 'rg migration drizzle/migrations'; "
            "echo 'modified src/db/schema.ts'; "
            "echo 'npm run db:generate passed'"
        ),
        workdir=tmp_path,
    )

    assert result["execution"]["exit_code"] == 0
    assert result["metrics"]["inspected_package_versions_before_edit"] is True
    assert result["metrics"]["tests_passing"] is True
    assert result["artifacts"]["transcript"].endswith("transcript.md")
