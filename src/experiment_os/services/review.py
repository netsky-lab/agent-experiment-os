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
            if page.type in {"claim", "knowledge_card"}
            and page.page_metadata.get("review_required", True)
        ]
        return [page_to_dict(page) for page in queued[:limit]]

    def set_status(self, page_id: str, status: str) -> dict:
        page = self._wiki.set_status(page_id, status)
        self._retriever.reindex_all()
        return page_to_dict(page)

    def promote_claim(self, claim_id: str, *, title: str | None = None) -> dict:
        claim = self._wiki.get_page(claim_id)
        if claim is None:
            raise ValueError(f"Unknown claim_id: {claim_id}")
        if claim.type != "claim":
            raise ValueError(f"Page is not a claim: {claim_id}")

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
