from sqlalchemy.orm import Session

from experiment_os.db.models import Brief


class BriefRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, brief: Brief) -> Brief:
        self._session.add(brief)
        self._session.flush()
        return brief

    def get(self, brief_id: str) -> Brief | None:
        return self._session.get(Brief, brief_id)

