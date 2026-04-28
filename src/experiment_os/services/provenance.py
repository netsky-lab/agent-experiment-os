from typing import Any

from sqlalchemy.orm import Session

from experiment_os.repositories.wiki import WikiRepository
from experiment_os.services.serialization import page_to_dict


class ProvenanceService:
    def __init__(self, session: Session) -> None:
        self._wiki = WikiRepository(session)

    def page_provenance(self, page_id: str) -> dict[str, Any]:
        page = self._wiki.get_page(page_id)
        if page is None:
            raise ValueError(f"Unknown page_id: {page_id}")
        outgoing = self._wiki.list_edges_from(page_id)
        targets = self._wiki.get_pages(edge.target_page_id for edge in outgoing)
        target_by_id = {target.id: target for target in targets}
        return {
            "page": page_to_dict(page, include_body=True),
            "edges": [
                {
                    "source": edge.source_page_id,
                    "target": edge.target_page_id,
                    "type": edge.edge_type,
                    "metadata": edge.edge_metadata,
                }
                for edge in outgoing
            ],
            "dependencies": [
                page_to_dict(target_by_id[edge.target_page_id])
                for edge in outgoing
                if edge.target_page_id in target_by_id
            ],
            "freshness": _freshness(page.page_metadata),
        }


def _freshness(metadata: dict[str, Any]) -> dict[str, Any]:
    updated_at = metadata.get("source_updated_at")
    retrieved_at = metadata.get("retrieved_at")
    return {
        "source_updated_at": updated_at,
        "retrieved_at": retrieved_at,
        "stale_warning": bool(updated_at and retrieved_at and updated_at > retrieved_at),
        "allowed_use": metadata.get("allowed_use") or metadata.get("trust"),
    }
