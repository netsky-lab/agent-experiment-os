"""source snapshots

Revision ID: 202604270003
Revises: 202604270002
Create Date: 2026-04-27 00:00:03 UTC
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "202604270003"
down_revision: str | None = "202604270002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "source_snapshots",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("source_type", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False, server_default=""),
        sa.Column("content", sa.Text(), nullable=False, server_default=""),
        sa.Column("content_hash", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("url", name="uq_source_snapshots_url"),
    )
    op.create_index("ix_source_snapshots_type", "source_snapshots", ["source_type"])
    op.create_index("ix_source_snapshots_retrieved_at", "source_snapshots", ["retrieved_at"])


def downgrade() -> None:
    op.drop_table("source_snapshots")

