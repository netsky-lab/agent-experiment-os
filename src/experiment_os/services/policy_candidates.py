from typing import Any

from sqlalchemy.orm import Session

from experiment_os.domain.schemas import WikiPageInput
from experiment_os.repositories.wiki import WikiRepository
from experiment_os.retrieval.hybrid import HybridRetriever
from experiment_os.services.serialization import page_to_dict


VERSION_TRAP_POLICY_ID = "policy.candidate.issue-version-local-verification"


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
