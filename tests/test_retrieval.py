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

