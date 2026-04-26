from collections.abc import Iterable
from uuid import uuid4

from sqlalchemy import Select, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from experiment_os.db.models import WikiEdge, WikiPage
from experiment_os.domain.schemas import PageEdge, WikiPageInput


class WikiRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert_page(self, page: WikiPageInput) -> WikiPage:
        stmt = (
            insert(WikiPage)
            .values(
                id=page.id,
                type=page.type,
                title=page.title,
                status=page.status,
                confidence=page.confidence,
                summary=page.summary,
                body=page.body,
                page_metadata=page.metadata,
            )
            .on_conflict_do_update(
                index_elements=[WikiPage.id],
                set_={
                    "type": page.type,
                    "title": page.title,
                    "status": page.status,
                    "confidence": page.confidence,
                    "summary": page.summary,
                    "body": page.body,
                    "metadata": page.metadata,
                },
            )
            .returning(WikiPage)
        )
        return self._session.execute(stmt).scalar_one()

    def upsert_edge(self, edge: PageEdge) -> None:
        stmt = (
            insert(WikiEdge)
            .values(
                id=uuid4(),
                source_page_id=edge.source_page_id,
                target_page_id=edge.target_page_id,
                edge_type=edge.edge_type,
                edge_metadata=edge.metadata,
            )
            .on_conflict_do_nothing(
                constraint="uq_wiki_edges_unique",
            )
        )
        self._session.execute(stmt)

    def get_page(self, page_id: str) -> WikiPage | None:
        return self._session.get(WikiPage, page_id)

    def get_pages(self, page_ids: Iterable[str]) -> list[WikiPage]:
        ids = list(dict.fromkeys(page_ids))
        if not ids:
            return []
        pages = self._session.scalars(select(WikiPage).where(WikiPage.id.in_(ids))).all()
        by_id = {page.id: page for page in pages}
        return [by_id[page_id] for page_id in ids if page_id in by_id]

    def list_pages(self) -> list[WikiPage]:
        return self._session.scalars(select(WikiPage).order_by(WikiPage.id)).all()

    def list_pages_filtered(
        self,
        *,
        status: str | None = None,
        page_type: str | None = None,
    ) -> list[WikiPage]:
        stmt: Select[tuple[WikiPage]] = select(WikiPage)
        if status:
            stmt = stmt.where(WikiPage.status == status)
        if page_type:
            stmt = stmt.where(WikiPage.type == page_type)
        return self._session.scalars(stmt.order_by(WikiPage.id)).all()

    def set_status(self, page_id: str, status: str) -> WikiPage:
        page = self.get_page(page_id)
        if page is None:
            raise ValueError(f"Unknown page_id: {page_id}")
        page.status = status
        self._session.flush()
        return page

    def list_edges_from(self, page_id: str, edge_type: str | None = None) -> list[WikiEdge]:
        stmt: Select[tuple[WikiEdge]] = select(WikiEdge).where(WikiEdge.source_page_id == page_id)
        if edge_type:
            stmt = stmt.where(WikiEdge.edge_type == edge_type)
        return self._session.scalars(stmt.order_by(WikiEdge.target_page_id)).all()

    def list_edges_from_many(
        self,
        page_ids: Iterable[str],
        edge_type: str | None = None,
    ) -> list[WikiEdge]:
        ids = list(dict.fromkeys(page_ids))
        if not ids:
            return []
        stmt: Select[tuple[WikiEdge]] = select(WikiEdge).where(WikiEdge.source_page_id.in_(ids))
        if edge_type:
            stmt = stmt.where(WikiEdge.edge_type == edge_type)
        return self._session.scalars(stmt.order_by(WikiEdge.source_page_id, WikiEdge.target_page_id)).all()

    def find_candidate_pages(
        self,
        *,
        libraries: list[str],
        agent: str | None,
        model: str | None,
        toolchain: str | None,
    ) -> list[WikiPage]:
        pages = self._session.scalars(
            select(WikiPage).where(WikiPage.status == "accepted").order_by(WikiPage.id)
        ).all()
        return [
            page
            for page in pages
            if _matches_applicability(page, libraries, agent, model, toolchain)
        ]


def _matches_applicability(
    page: WikiPage,
    libraries: list[str],
    agent: str | None,
    model: str | None,
    toolchain: str | None,
) -> bool:
    applies_to = page.page_metadata.get("appliesTo", {})
    if not applies_to:
        if page.type == "source" and libraries:
            haystack = " ".join([page.id, page.title, page.summary, page.body]).lower()
            return any(library.lower() in haystack for library in libraries)
        return True

    if applies_to.get("agent") and agent and applies_to["agent"] != agent:
        return False
    if applies_to.get("model") and model and applies_to["model"] != model:
        return False
    if applies_to.get("toolchain") and toolchain and applies_to["toolchain"] != toolchain:
        return False

    repo_type = applies_to.get("repo_type")
    if repo_type:
        # Repo type detection is not implemented yet. Keep repo_type-specific
        # policies eligible so they can appear with their applicability metadata.
        return True

    library = applies_to.get("library")
    if library and libraries:
        normalized = {item.lower() for item in libraries}
        return str(library).lower() in normalized

    return True
