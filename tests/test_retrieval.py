from experiment_os.retrieval.embeddings import DeterministicEmbeddingProvider
from experiment_os.retrieval.hybrid import HybridRetriever


def test_deterministic_embedding_is_stable_and_normalized():
    provider = DeterministicEmbeddingProvider(dimensions=8)

    first = provider.embed("drizzle migration default")
    second = provider.embed("drizzle migration default")

    assert first == second
    assert len(first) == 8
    assert any(value != 0 for value in first)


def test_hybrid_search_returns_seed_knowledge(session):
    results = HybridRetriever(session).search("drizzle migration default", limit=5)
    result_ids = {result["id"] for result in results}

    assert "knowledge.drizzle-migration-defaults" in result_ids


def test_hybrid_search_can_filter_by_library_and_page_type(session):
    results = HybridRetriever(session).search(
        "api drift upgrade advice",
        limit=5,
        libraries=["example-llm-sdk"],
        page_types=["knowledge_card", "source"],
    )

    assert results
    assert {result["type"] for result in results} <= {"knowledge_card", "source"}
    assert any(result["id"] == "knowledge.python-api-drift-local-shim" for result in results)


def test_hybrid_search_can_include_draft_issue_claims(session):
    results = HybridRetriever(session).search(
        "example llm sdk upgrade advice",
        limit=20,
        libraries=["example-llm-sdk"],
        page_types=["claim"],
        status=None,
    )

    assert any(result["id"] == "claim.issue.example-llm-sdk.upgrade-advice" for result in results)
