from sqlalchemy.orm import Session

from experiment_os.domain.schemas import PageEdge, WikiPageInput
from experiment_os.repositories.wiki import WikiRepository
from experiment_os.retrieval.hybrid import HybridRetriever
from experiment_os.services.serialization import page_to_dict


class ReviewService:
    def __init__(self, session: Session) -> None:
        self._wiki = WikiRepository(session)
        self._retriever = HybridRetriever(session)

    def list_pages(
        self,
        *,
        status: str | None = None,
        page_type: str | None = None,
    ) -> list[dict]:
        return [
            page_to_dict(page)
            for page in self._wiki.list_pages_filtered(status=status, page_type=page_type)
        ]

    def review_queue(self, *, limit: int = 50) -> list[dict]:
        pages = self._wiki.list_pages_filtered(status="draft")
        queued = [
            page
            for page in pages
            if page.type in {"claim", "knowledge_card", "policy", "intervention"}
            and page.page_metadata.get("review_required", True)
        ]
        return [page_to_dict(page) for page in queued[:limit]]

    def set_status(
        self,
        page_id: str,
        status: str,
        *,
        rationale: str | None = None,
        reviewer: str | None = None,
    ) -> dict:
        page = self._wiki.set_status(page_id, status)
        metadata = dict(page.page_metadata)
        metadata["review"] = {
            **metadata.get("review", {}),
            "status": status,
            "rationale": rationale,
            "reviewer": reviewer,
        }
        if status in {"accepted", "rejected", "deprecated"}:
            metadata["review_required"] = False
        page.page_metadata = metadata
        self._retriever.reindex_all()
        return page_to_dict(page)

    def promote_claim(self, claim_id: str, *, title: str | None = None) -> dict:
        claim = self._claim_page(claim_id)

        card_id = f"knowledge.promoted.{claim_id.removeprefix('claim.')}"
        card = WikiPageInput(
            id=card_id,
            type="knowledge_card",
            title=title or claim.title,
            status="draft",
            confidence=claim.confidence,
            summary=claim.summary,
            body=(
                "Draft card promoted from a claim. Review source provenance and affected versions "
                "before accepting."
            ),
            metadata={
                "promoted_from": claim.id,
                "claim_type": claim.page_metadata.get("claim_type"),
                "source_page_id": claim.page_metadata.get("source_page_id"),
                "trust": "requires_human_review",
                "review_required": True,
            },
        )
        page = self._wiki.upsert_page(card)
        self._wiki.upsert_edge(PageEdge(source_page_id=page.id, target_page_id=claim.id))
        self._retriever.reindex_all()
        return page_to_dict(page)

    def promote_claim_to_policy(
        self,
        claim_id: str,
        *,
        title: str | None = None,
        applies_to: dict | None = None,
    ) -> dict:
        claim = self._claim_page(claim_id)
        policy = WikiPageInput(
            id=f"policy.promoted.{claim.id.removeprefix('claim.')}",
            type="policy",
            title=title or claim.title,
            status="draft",
            confidence=claim.confidence,
            summary=claim.summary,
            body=(
                "Draft policy promoted from issue evidence. Accept only after verifying source "
                "relevance, local applicability, and counterexamples."
            ),
            metadata={
                **_promotion_metadata(claim),
                "appliesTo": applies_to or claim.page_metadata.get("appliesTo", {}),
                "review": {
                    "status": "needs_human_review",
                    "required_before": "agent_decision_rule_use",
                },
            },
        )
        page = self._wiki.upsert_page(policy)
        self._wiki.upsert_edge(PageEdge(source_page_id=page.id, target_page_id=claim.id))
        self._retriever.reindex_all()
        return page_to_dict(page)

    def promote_claim_to_intervention(
        self,
        claim_id: str,
        *,
        title: str | None = None,
        mitigates: list[str] | None = None,
    ) -> dict:
        claim = self._claim_page(claim_id)
        intervention = WikiPageInput(
            id=f"intervention.promoted.{claim.id.removeprefix('claim.')}",
            type="intervention",
            title=title or claim.title,
            status="draft",
            confidence=claim.confidence,
            summary=claim.summary,
            body=(
                "Draft intervention promoted from issue evidence. Accept only after verifying "
                "that it mitigates a named failure mode without introducing larger risk."
            ),
            metadata={
                **_promotion_metadata(claim),
                "mitigates": mitigates or [],
                "review": {
                    "status": "needs_human_review",
                    "required_before": "agent_intervention_use",
                },
            },
        )
        page = self._wiki.upsert_page(intervention)
        self._wiki.upsert_edge(PageEdge(source_page_id=page.id, target_page_id=claim.id))
        for failure_id in mitigates or []:
            self._wiki.upsert_edge(
                PageEdge(
                    source_page_id=page.id,
                    target_page_id=failure_id,
                    edge_type="mitigates",
                )
            )
        self._retriever.reindex_all()
        return page_to_dict(page)

    def _claim_page(self, claim_id: str):
        claim = self._wiki.get_page(claim_id)
        if claim is None:
            raise ValueError(f"Unknown claim_id: {claim_id}")
        if claim.type != "claim":
            raise ValueError(f"Page is not a claim: {claim_id}")
        return claim


def _promotion_metadata(claim) -> dict:
    return {
        "promoted_from": claim.id,
        "claim_type": claim.page_metadata.get("claim_type"),
        "source_page_id": claim.page_metadata.get("source_page_id"),
        "source_url": claim.page_metadata.get("source_url"),
        "trust": "requires_human_review",
        "review_required": True,
        "promotion_method": "human_requested.v1",
    }
