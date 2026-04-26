from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from experiment_os.db.models import SourceSnapshot


class SourceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert(self, snapshot: SourceSnapshot) -> SourceSnapshot:
        stmt = (
            insert(SourceSnapshot)
            .values(
                id=snapshot.id,
                source_type=snapshot.source_type,
                url=snapshot.url,
                title=snapshot.title,
                content=snapshot.content,
                content_hash=snapshot.content_hash,
                source_metadata=snapshot.source_metadata,
            )
            .on_conflict_do_update(
                constraint="uq_source_snapshots_url",
                set_={
                    "title": snapshot.title,
                    "content": snapshot.content,
                    "content_hash": snapshot.content_hash,
                    "metadata": snapshot.source_metadata,
                },
            )
            .returning(SourceSnapshot)
        )
        return self._session.execute(stmt).scalar_one()
