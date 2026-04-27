from experiment_os.services.experiment_reports import ExperimentReportGenerator


def test_experiment_report_v2_recommends_harder_fixture_when_no_delta():
    report = {
        "condition": "baseline",
        "run": {"run_id": "run.base"},
        "metrics": {
            "inspected_package_versions_before_edit": True,
            "wrong_file_edits": 0,
            "failure_count": 0,
        },
        "execution": {"exit_code": 0},
    }

    result = ExperimentReportGenerator().comparison(
        experiment_id="experiment.test",
        hypothesis="Briefs improve behavior.",
        baseline=report,
        candidate={**report, "condition": "brief-assisted", "run": {"run_id": "run.brief"}},
        metric_deltas={"failure_count": 0},
        interpretation="No strong signal.",
    )

    assert result.data["schema"] == "experiment_report.v2"
    assert result.data["next_experiment"]["title"].startswith("Add a harder fixture")
    assert "# Experiment Report" in result.markdown
