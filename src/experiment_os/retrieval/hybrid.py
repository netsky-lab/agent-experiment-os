from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from experiment_os.retrieval.embeddings import DeterministicEmbeddingProvider, vector_literal


class HybridRetriever:
    def __init__(
        self,
        session: Session,
        embedding_provider: DeterministicEmbeddingProvider | None = None,
    ) -> None:
        self._session = session
        self._embeddings = embedding_provider or DeterministicEmbeddingProvider()

    def reindex_all(self) -> dict[str, int]:
        rows = self._session.execute(
            text(
                """
                SELECT id, title, summary, body
                FROM wiki_pages
                ORDER BY id
                """
            )
        ).mappings()
        count = 0
        for row in rows:
            content = f"{row['title']}\n{row['summary']}\n{row['body']}"
            embedding = vector_literal(self._embeddings.embed(content))
            self._session.execute(
                text("UPDATE wiki_pages SET embedding = CAST(:embedding AS vector) WHERE id = :id"),
                {"id": row["id"], "embedding": embedding},
            )
            count += 1
        return {"embedded_pages": count}

    def search(
        self,
        query: str,
        *,
        limit: int = 8,
        libraries: list[str] | None = None,
        page_types: list[str] | None = None,
        status: str | None = "accepted",
    ) -> list[dict[str, Any]]:
        if not query.strip():
            return []
        embedding = vector_literal(self._embeddings.embed(query))
        rows = self._session.execute(
            text(
                """
                WITH q AS (
                  SELECT
                    plainto_tsquery('english', :query) AS tsq,
                    CAST(:embedding AS vector) AS embedding
                ),
                scored AS (
                  SELECT
                    p.id,
                    p.type,
                    p.title,
                    p.status,
                    p.confidence,
                    p.summary,
                    p.metadata,
                    ts_rank_cd(p.search_vector, q.tsq) AS text_score,
                    CASE
                      WHEN p.embedding IS NULL THEN 0
                      ELSE 1 - (p.embedding <=> q.embedding)
                    END AS semantic_score,
                    (
                      0.65 * ts_rank_cd(p.search_vector, q.tsq) +
                      0.35 * CASE
                        WHEN p.embedding IS NULL THEN 0
                        ELSE 1 - (p.embedding <=> q.embedding)
                      END
                    ) AS score
                  FROM wiki_pages p, q
                  WHERE (CAST(:status AS text) IS NULL OR p.status = CAST(:status AS text))
                    AND (
                      p.search_vector @@ q.tsq
                      OR p.embedding IS NOT NULL
                    )
                )
                SELECT
                  id, type, title, status, confidence, summary, metadata,
                  text_score, semantic_score, score
                FROM scored
                WHERE score > -1
                ORDER BY score DESC, id
                LIMIT :limit
                """
            ),
            {
                "query": query,
                "embedding": embedding,
                "limit": max(limit * 12, 64) if libraries or page_types else limit,
                "status": status,
            },
        ).mappings()

        results = [
            {
                "id": row["id"],
                "type": row["type"],
                "title": row["title"],
                "status": row["status"],
                "confidence": row["confidence"],
                "summary": row["summary"],
                "metadata": row["metadata"],
                "text_score": float(row["text_score"] or 0),
                "semantic_score": float(row["semantic_score"] or 0),
                "score": float(row["score"] or 0),
            }
            for row in rows
        ]
        filtered = [
            result
            for result in results
            if _matches_filters(result, libraries=libraries or [], page_types=page_types or [])
        ]
        return filtered[:limit]


def _matches_filters(
    result: dict[str, Any],
    *,
    libraries: list[str],
    page_types: list[str],
) -> bool:
    if page_types and result["type"] not in set(page_types):
        return False
    if not libraries:
        return True

    metadata = result.get("metadata") or {}
    applies_to = metadata.get("appliesTo") or {}
    library = str(applies_to.get("library", "")).lower()
    normalized = {item.lower() for item in libraries}
    if library and library in normalized:
        return True

    haystack = " ".join(
        [
            result.get("id", ""),
            result.get("title", ""),
            result.get("summary", ""),
            str(metadata.get("repo", "")),
            str(metadata.get("library", "")),
        ]
    ).lower()
    return any(item in haystack for item in normalized)
