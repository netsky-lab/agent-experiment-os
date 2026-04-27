from collections import deque
from typing import Any

from sqlalchemy.orm import Session

from experiment_os.domain.schemas import DependencyGraph
from experiment_os.repositories.wiki import WikiRepository
from experiment_os.services.serialization import page_to_dict


class DependencyResolver:
    def __init__(self, session: Session) -> None:
        self._wiki = WikiRepository(session)

    def resolve(
        self,
        page_ids: list[str],
        *,
        depth: int = 2,
        token_budget: int = 2000,
    ) -> DependencyGraph:
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque((page_id, 0) for page_id in page_ids)
        pages: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        truncated = False
        estimated_tokens = 0

        while queue:
            page_id, current_depth = queue.popleft()
            if page_id in visited:
                continue
            visited.add(page_id)

            page = self._wiki.get_page(page_id)
            if page is None:
                pages.append({"id": page_id, "missing": True, "dependsOn": []})
                continue

            outgoing_edges = self._wiki.list_edges_from(page.id, edge_type="dependsOn")
            depends_on = [edge.target_page_id for edge in outgoing_edges]
            edges.extend(
                {
                    "source": page.id,
                    "target": edge.target_page_id,
                    "type": edge.edge_type,
                    "metadata": edge.edge_metadata,
                }
                for edge in outgoing_edges
            )
            serialized = page_to_dict(page, include_body=False)
            serialized["dependsOn"] = depends_on
            pages.append(serialized)

            estimated_tokens += max(1, len(page.summary.split()) + len(page.title.split()))
            if estimated_tokens > token_budget:
                truncated = True
                break

            if current_depth < depth:
                for target_page_id in depends_on:
                    if target_page_id not in visited:
                        queue.append((target_page_id, current_depth + 1))

        return DependencyGraph(root_pages=page_ids, pages=pages, edges=edges, truncated=truncated)
