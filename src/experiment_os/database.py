from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from experiment_os.config import get_settings


def sqlalchemy_url(url: str) -> str:
    if url.startswith("postgresql+psycopg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def create_db_engine() -> Engine:
    settings = get_settings()
    return create_engine(sqlalchemy_url(settings.database_url), pool_pre_ping=True)


engine = create_db_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def session_scope() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def check_database() -> dict[str, str]:
    settings = get_settings()

    with psycopg.connect(settings.database_url, connect_timeout=5) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    current_database(),
                    current_user,
                    current_setting('server_version'),
                    extversion
                FROM pg_extension
                WHERE extname = 'vector'
                """
            )
            row = cur.fetchone()

    if row is None:
        raise RuntimeError("pgvector extension is not installed in the connected database")

    database, user, server_version, vector_version = row
    return {
        "database": database,
        "user": user,
        "server_version": server_version,
        "vector_version": vector_version,
    }
