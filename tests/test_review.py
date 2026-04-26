from experiment_os.domain.schemas import WikiPageInput
from experiment_os.repositories.wiki import WikiRepository
from experiment_os.services.review import ReviewService


def test_review_promotes_claim_to_draft_card(session):
    claim = WikiPageInput(
        id="claim.test.promote",
        type="claim",
        title="Test claim",
        status="draft",
        confidence="low",
        summary="A test claim summary",
        metadata={"claim_type": "problem", "source_page_id": "source.test"},
    )
    WikiRepository(session).upsert_page(claim)

    page = ReviewService(session).promote_claim("claim.test.promote")

    assert page["id"] == "knowledge.promoted.test.promote"
    assert page["type"] == "knowledge_card"
    assert page["status"] == "draft"

