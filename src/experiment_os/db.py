from dataclasses import dataclass

import psycopg

from experiment_os.config import get_settings


@dataclass(frozen=True)
class DatabaseStatus:
    database: str
    user: str
    server_version: str
    vector_version: str


def check_database() -> DatabaseStatus:
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
    return DatabaseStatus(
        database=database,
        user=user,
        server_version=server_version,
        vector_version=vector_version,
    )
