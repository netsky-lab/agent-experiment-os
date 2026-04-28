from experiment_os.domain.schemas import PageEdge, WikiPageInput
from experiment_os.repositories.wiki import WikiRepository
from experiment_os.services.provenance import ProvenanceService
from experiment_os.services.wiki_health import WikiHealthService


def test_wiki_health_detects_stale_and_duplicate_pages(session):
    wiki = WikiRepository(session)
    for page_id in ["source.test.dup-a", "source.test.dup-b"]:
        wiki.upsert_page(
            WikiPageInput(
                id=page_id,
                type="source",
                title="Duplicate source",
                status="accepted",
                summary="same",
                metadata={
                    "allowed_use": "evidence_only",
                    "source_updated_at": "2026-04-28T00:00:00+00:00",
                    "retrieved_at": "2026-04-27T00:00:00+00:00",
                },
            )
        )

    service = WikiHealthService(session)
    stale = service.stale_pages()
    duplicates = service.duplicate_candidates()

    assert any(item["page"]["id"] == "source.test.dup-a" for item in stale["items"])
    assert any(len(item["pages"]) == 2 for item in duplicates["items"])


def test_provenance_includes_inbound_references(session):
    wiki = WikiRepository(session)
    wiki.upsert_page(
        WikiPageInput(
            id="source.test.inbound",
            type="source",
            title="Inbound source",
            status="accepted",
            summary="source",
        )
    )
    wiki.upsert_page(
        WikiPageInput(
            id="claim.test.inbound",
            type="claim",
            title="Inbound claim",
            status="draft",
            summary="claim",
        )
    )
    wiki.upsert_edge(
        PageEdge(
            source_page_id="claim.test.inbound",
            target_page_id="source.test.inbound",
            edge_type="derivedFrom",
        )
    )

    provenance = ProvenanceService(session).page_provenance("source.test.inbound")

    assert provenance["referenced_by"][0]["id"] == "claim.test.inbound"
    assert provenance["inbound_edges"][0]["type"] == "derivedFrom"
