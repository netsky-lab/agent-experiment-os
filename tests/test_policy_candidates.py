from experiment_os.services.policy_candidates import PolicyCandidateService


def test_policy_candidate_created_from_version_trap_signal(session):
    comparison = {
        "experiment_id": "experiment.001-drizzle-brief",
        "comparison": "codex_version_trap_baseline_vs_brief_assisted",
        "conditions": {
            "baseline": {
                "run": {"run_id": "run.base"},
                "metrics": {"blind_issue_version_alignment": True, "dependency_changed": True},
            },
            "brief_assisted": {
                "run": {"run_id": "run.brief"},
                "metrics": {
                    "preserved_local_version_constraint": True,
                    "dependency_changed": False,
                },
            },
        },
        "metric_deltas": {"dependency_changed": {"baseline": True, "brief_assisted": False}},
    }

    page = PolicyCandidateService(session).propose_from_version_trap(comparison)

    assert page is not None
    assert page["type"] == "policy"
    assert page["status"] == "draft"
    assert page["metadata"]["baseline_run_id"] == "run.base"


def test_policy_candidate_created_from_wrong_file_edit_signal(session):
    comparison = {
        "experiment_id": "experiment.001-drizzle-brief",
        "comparison": "codex_version_trap_baseline_vs_brief_assisted",
        "conditions": {
            "baseline": {
                "run": {"run_id": "run.base"},
                "metrics": {"wrong_file_edits": 2, "dependency_changed": False},
            },
            "brief_assisted": {
                "run": {"run_id": "run.brief"},
                "metrics": {"wrong_file_edits": 0, "dependency_changed": False},
            },
        },
        "metric_deltas": {"wrong_file_edits": -2},
    }

    page = PolicyCandidateService(session).propose_from_version_trap(comparison)

    assert page is not None
    assert page["metadata"]["brief_run_id"] == "run.brief"
