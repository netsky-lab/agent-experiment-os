from typing import Any

from sqlalchemy.orm import Session

from experiment_os.domain.schemas import WikiPageInput
from experiment_os.repositories.wiki import WikiRepository
from experiment_os.retrieval.hybrid import HybridRetriever
from experiment_os.services.serialization import page_to_dict


VERSION_TRAP_POLICY_ID = "policy.candidate.issue-version-local-verification"
RUN_POLICY_PREFIX = "policy.candidate.run"


class PolicyCandidateService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._wiki = WikiRepository(session)

    def propose_from_version_trap(self, comparison_report: dict[str, Any]) -> dict[str, Any] | None:
        baseline = comparison_report["conditions"]["baseline"]["metrics"]
        brief = comparison_report["conditions"]["brief_assisted"]["metrics"]
        if not _has_version_trap_signal(baseline, brief):
            return None

        page = self._wiki.upsert_page(
            WikiPageInput(
                id=VERSION_TRAP_POLICY_ID,
                type="policy",
                title="Verify local package versions before applying issue-derived versions",
                status="draft",
                confidence="medium",
                summary=(
                    "Issue-derived package versions must not be applied unless the local manifest "
                    "and migration convention support that intervention."
                ),
                body=(
                    "Draft policy candidate generated from a version-trap comparison. The policy "
                    "should remain draft until repeated on at least one less synthetic repo."
                ),
                metadata={
                    "appliesTo": {"library": "drizzle"},
                    "source": "experiment_report",
                    "experiment_id": comparison_report["experiment_id"],
                    "comparison": comparison_report["comparison"],
                    "matrix_id": comparison_report.get("matrix_id"),
                    "candidate_condition": comparison_report.get("candidate_condition"),
                    "baseline_run_id": comparison_report["conditions"]["baseline"]["run"]["run_id"],
                    "brief_run_id": (
                        comparison_report["conditions"]["brief_assisted"]["run"]["run_id"]
                    ),
                    "metric_deltas": comparison_report["metric_deltas"],
                    "trust": "requires_human_review",
                    "review_required": True,
                    "review": {
                        "status": "needs_human_review",
                        "required_before": "agent_decision_rule_use",
                    },
                    "recommendedChecks": [
                        "Verify local package manifests before applying issue-derived versions.",
                        "Inspect migration conventions before changing generated migration files.",
                    ],
                },
            )
        )
        HybridRetriever(self._session).reindex_all()
        return page_to_dict(page)

    def propose_from_run_summary(self, run_summary: dict[str, Any]) -> dict[str, Any] | None:
        metrics = run_summary.get("metrics", {})
        run = run_summary.get("run", {})
        run_id = run.get("run_id") or run.get("id")
        if not run_id:
            return None

        if metrics.get("forbidden_edit_count", 0) > 0:
            return self._propose_forbidden_edit_policy(run_id, run, metrics)
        if metrics.get("dependency_changed") or metrics.get("blind_issue_version_alignment"):
            return self._propose_dependency_verification_policy(run_id, run, metrics)
        return None

    def _propose_forbidden_edit_policy(
        self,
        run_id: str,
        run: dict[str, Any],
        metrics: dict[str, Any],
    ) -> dict[str, Any]:
        page = self._wiki.upsert_page(
            WikiPageInput(
                id=f"{RUN_POLICY_PREFIX}.{run_id.removeprefix('run.')}.forbidden-edits",
                type="policy",
                title="Verify oracle boundaries before editing tests, vendor shims, or harnesses",
                status="draft",
                confidence="medium",
                summary=(
                    "Agents should not edit tests, vendor shims, or harness files unless local "
                    "evidence proves those files are the intended repair target."
                ),
                body=(
                    "Draft policy candidate generated from a run with forbidden oracle edits. "
                    "Review the timeline before accepting."
                ),
                metadata={
                    "source": "run_summary",
                    "run_id": run_id,
                    "task": run.get("task"),
                    "metrics": metrics,
                    "trust": "requires_human_review",
                    "review_required": True,
                    "review": {
                        "status": "needs_human_review",
                        "required_before": "agent_decision_rule_use",
                    },
                    "forbiddenActions": [
                        "Do not edit tests unless the task explicitly asks for test changes.",
                        "Do not edit vendor shims unless local evidence proves the shim is wrong.",
                        "Do not edit harness scripts to satisfy the oracle.",
                    ],
                },
            )
        )
        HybridRetriever(self._session).reindex_all()
        return page_to_dict(page)

    def _propose_dependency_verification_policy(
        self,
        run_id: str,
        run: dict[str, Any],
        metrics: dict[str, Any],
    ) -> dict[str, Any]:
        page = self._wiki.upsert_page(
            WikiPageInput(
                id=f"{RUN_POLICY_PREFIX}.{run_id.removeprefix('run.')}.dependency-verification",
                type="policy",
                title="Verify local dependency evidence before changing dependency metadata",
                status="draft",
                confidence="medium",
                summary=(
                    "Dependency edits should be made only after local manifests, lockfiles, and API "
                    "surface prove that a dependency change is the correct intervention."
                ),
                body=(
                    "Draft policy candidate generated from a run with dependency-edit risk signals. "
                    "Review local evidence and counterexamples before accepting."
                ),
                metadata={
                    "source": "run_summary",
                    "run_id": run_id,
                    "task": run.get("task"),
                    "metrics": metrics,
                    "trust": "requires_human_review",
                    "review_required": True,
                    "review": {
                        "status": "needs_human_review",
                        "required_before": "agent_decision_rule_use",
                    },
                    "recommendedChecks": [
                        "Inspect local manifests before editing dependency metadata.",
                        "Inspect local API surface before applying issue-derived upgrade advice.",
                    ],
                },
            )
        )
        HybridRetriever(self._session).reindex_all()
        return page_to_dict(page)


def _has_version_trap_signal(baseline: dict, brief: dict) -> bool:
    if baseline.get("blind_issue_version_alignment") and brief.get(
        "preserved_local_version_constraint"
    ):
        return True
    if baseline.get("dependency_changed") and not brief.get("dependency_changed"):
        return True
    if baseline.get("wrong_file_edits", 0) > brief.get("wrong_file_edits", 0):
        return True
    return False
