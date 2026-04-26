"""wiki embeddings

Revision ID: 202604270002
Revises: 202604270001
Create Date: 2026-04-27 00:00:02 UTC
"""

from collections.abc import Sequence

from alembic import op

revision: str = "202604270002"
down_revision: str | None = "202604270001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE wiki_pages ADD COLUMN embedding vector(64)")
    op.execute(
        """
        CREATE INDEX ix_wiki_pages_embedding
        ON wiki_pages
        USING hnsw (embedding vector_cosine_ops)
        WHERE embedding IS NOT NULL
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_wiki_pages_embedding")
    op.execute("ALTER TABLE wiki_pages DROP COLUMN IF EXISTS embedding")

