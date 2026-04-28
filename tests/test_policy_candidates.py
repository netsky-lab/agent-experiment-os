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


def test_policy_candidate_created_from_run_forbidden_edit_signal(session):
    summary = {
        "run": {"run_id": "run.forbidden", "task": "Fix API drift"},
        "metrics": {
            "forbidden_edit_count": 2,
            "test_edit_count": 1,
            "vendor_edit_count": 1,
        },
    }

    page = PolicyCandidateService(session).propose_from_run_summary(summary)

    assert page is not None
    assert page["id"] == "policy.candidate.run.forbidden.forbidden-edits"
    assert page["status"] == "draft"
    assert page["metadata"]["run_id"] == "run.forbidden"
    assert "Do not edit tests" in page["metadata"]["forbiddenActions"][0]


def test_policy_candidate_created_from_run_dependency_edit_signal(session):
    summary = {
        "run": {"run_id": "run.deps", "task": "Fix API drift"},
        "metrics": {"dependency_changed": True},
    }

    page = PolicyCandidateService(session).propose_from_run_summary(summary)

    assert page is not None
    assert page["id"] == "policy.candidate.run.deps.dependency-verification"
    assert page["metadata"]["review_required"] is True


def test_policy_candidate_created_from_run_red_green_churn_signal(session):
    summary = {
        "run": {"run_id": "run.churn", "task": "Fix API drift"},
        "metrics": {"test_failure_count": 1, "tests_passing": True},
    }

    page = PolicyCandidateService(session).propose_from_run_summary(summary)

    assert page is not None
    assert page["id"] == "policy.candidate.run.churn.red-green-churn"
    assert page["metadata"]["review_required"] is True


def test_policy_candidate_created_from_mcp_protocol_gap(session):
    matrix_report = {
        "matrix_id": "matrix.api-drift.test",
        "experiment_id": "experiment.002-python-api-drift",
        "matrix_kind": "api_drift",
        "summary": {
            "mcp_brief": {
                "metrics": {
                    "mcp_pre_work_protocol_called": {
                        "true_count": 0,
                        "false_count": 3,
                        "rate": 0,
                    },
                    "mcp_tool_call_count": {"mean": 0.67, "min": 0, "max": 2},
                }
            }
        },
    }

    page = PolicyCandidateService(session).propose_from_mcp_protocol_gap(matrix_report)

    assert page is not None
    assert page["id"] == "policy.candidate.matrix.matrix-api-drift-test.mcp-prework-gate"
    assert page["status"] == "draft"
    assert page["metadata"]["mcp_pre_work_rate"] == 0
    assert "Block or mark" in page["metadata"]["recommendedControls"][1]
