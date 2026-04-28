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


def test_review_promotes_claim_to_policy_and_intervention(session):
    claim = WikiPageInput(
        id="claim.test.policy-signal",
        type="claim",
        title="Version-specific migration signal",
        status="draft",
        confidence="low",
        summary="Check local Drizzle versions before applying beta issue knowledge.",
        metadata={
            "claim_type": "version_note",
            "source_page_id": "source.test",
            "source_url": "https://example.com/issue",
        },
    )
    WikiRepository(session).upsert_page(claim)

    service = ReviewService(session)
    policy = service.promote_claim_to_policy(
        "claim.test.policy-signal",
        applies_to={"library": "drizzle"},
    )
    intervention = service.promote_claim_to_intervention(
        "claim.test.policy-signal",
        mitigates=["failure.tool-call-syntax-drift"],
    )

    assert policy["type"] == "policy"
    assert policy["status"] == "draft"
    assert policy["metadata"]["appliesTo"]["library"] == "drizzle"
    assert intervention["type"] == "intervention"
    assert intervention["metadata"]["mitigates"] == ["failure.tool-call-syntax-drift"]


def test_review_queue_includes_policy_candidates(session):
    WikiRepository(session).upsert_page(
        WikiPageInput(
            id="policy.candidate.review",
            type="policy",
            title="Reviewable policy",
            status="draft",
            confidence="medium",
            summary="A generated policy candidate.",
            metadata={"review_required": True},
        )
    )

    queue = ReviewService(session).review_queue()

    assert any(item["id"] == "policy.candidate.review" for item in queue)


def test_review_status_records_rationale_and_clears_review_required(session):
    WikiRepository(session).upsert_page(
        WikiPageInput(
            id="policy.candidate.status",
            type="policy",
            title="Status policy",
            status="draft",
            confidence="medium",
            summary="A policy candidate.",
            metadata={"review_required": True},
        )
    )

    page = ReviewService(session).set_status(
        "policy.candidate.status",
        "accepted",
        rationale="Repeated matrix evidence supports this policy.",
        reviewer="maintainer",
        evidence_ids=["matrix.test", "run.test"],
    )

    assert page["status"] == "accepted"
    assert page["metadata"]["review_required"] is False
    assert page["metadata"]["review"]["rationale"] == (
        "Repeated matrix evidence supports this policy."
    )
    assert page["metadata"]["review"]["reviewer"] == "maintainer"
    assert page["metadata"]["review"]["evidence_ids"] == ["matrix.test", "run.test"]
