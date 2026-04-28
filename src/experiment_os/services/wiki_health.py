from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from experiment_os.repositories.wiki import WikiRepository
from experiment_os.services.serialization import page_to_dict


class WikiHealthService:
    def __init__(self, session: Session) -> None:
        self._wiki = WikiRepository(session)

    def graph(self, *, status: str | None = None, page_type: str | None = None) -> dict[str, Any]:
        pages = self._wiki.list_pages_filtered(status=status, page_type=page_type)
        ids = {page.id for page in pages}
        edges = [
            edge
            for edge in self._wiki.list_edges_from_many(ids)
            if edge.target_page_id in ids
        ]
        return {
            "nodes": [page_to_dict(page) for page in pages],
            "edges": [
                {
                    "source": edge.source_page_id,
                    "target": edge.target_page_id,
                    "type": edge.edge_type,
                    "metadata": edge.edge_metadata,
                }
                for edge in edges
            ],
        }

    def stale_pages(self) -> dict[str, Any]:
        items = []
        for page in self._wiki.list_pages():
            freshness = _freshness(page.page_metadata)
            if freshness["stale"]:
                items.append({"page": page_to_dict(page), "freshness": freshness})
        return {"items": items}

    def duplicate_candidates(self) -> dict[str, Any]:
        buckets: dict[tuple[str, str], list] = {}
        for page in self._wiki.list_pages():
            key = (page.type, _normalize(page.title or page.summary))
            if key[1]:
                buckets.setdefault(key, []).append(page)
        groups = [
            {
                "type": page_type,
                "fingerprint": fingerprint,
                "pages": [page_to_dict(page) for page in pages],
            }
            for (page_type, fingerprint), pages in sorted(buckets.items())
            if len(pages) > 1
        ]
        return {"items": groups}


def _freshness(metadata: dict[str, Any]) -> dict[str, Any]:
    source_updated_at = _parse_time(metadata.get("source_updated_at"))
    retrieved_at = _parse_time(metadata.get("retrieved_at"))
    stale = bool(source_updated_at and retrieved_at and source_updated_at > retrieved_at)
    return {
        "stale": stale,
        "source_updated_at": source_updated_at.isoformat() if source_updated_at else None,
        "retrieved_at": retrieved_at.isoformat() if retrieved_at else None,
        "allowed_use": metadata.get("allowed_use") or metadata.get("trust"),
    }


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _normalize(value: str) -> str:
    return " ".join(value.lower().split())[:160]
