from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.orm import Session

from experiment_os.database import session_scope
from experiment_os.services.seed import SeedService


@pytest.fixture(scope="session", autouse=True)
def migrated_database() -> None:
    command.upgrade(Config("alembic.ini"), "head")


@pytest.fixture()
def session() -> Iterator[Session]:
    with session_scope() as active_session:
        SeedService(active_session).seed()
        yield active_session

