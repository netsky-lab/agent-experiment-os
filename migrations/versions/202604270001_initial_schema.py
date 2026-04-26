"""initial schema

Revision ID: 202604270001
Revises:
Create Date: 2026-04-27 00:00:01 UTC
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "202604270001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "wiki_pages",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="draft"),
        sa.Column("confidence", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("body", sa.Text(), nullable=False, server_default=""),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_wiki_pages_type", "wiki_pages", ["type"])
    op.create_index("ix_wiki_pages_status", "wiki_pages", ["status"])
    op.execute(
        """
        ALTER TABLE wiki_pages
        ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
          setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
          setweight(to_tsvector('english', coalesce(summary, '')), 'B') ||
          setweight(to_tsvector('english', coalesce(body, '')), 'C')
        ) STORED
        """
    )
    op.execute("CREATE INDEX ix_wiki_pages_search ON wiki_pages USING GIN (search_vector)")

    op.create_table(
        "wiki_edges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_page_id", sa.Text(), nullable=False),
        sa.Column("target_page_id", sa.Text(), nullable=False),
        sa.Column("edge_type", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["source_page_id"], ["wiki_pages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_page_id"], ["wiki_pages.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("source_page_id", "target_page_id", "edge_type", name="uq_wiki_edges_unique"),
    )
    op.create_index("ix_wiki_edges_source", "wiki_edges", ["source_page_id"])
    op.create_index("ix_wiki_edges_target", "wiki_edges", ["target_page_id"])
    op.create_index("ix_wiki_edges_type", "wiki_edges", ["edge_type"])

    op.create_table(
        "briefs",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("task", sa.Text(), nullable=False),
        sa.Column("repo", sa.Text(), nullable=True),
        sa.Column("libraries", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("agent", sa.Text(), nullable=True),
        sa.Column("model", sa.Text(), nullable=True),
        sa.Column("toolchain", sa.Text(), nullable=True),
        sa.Column("token_budget", sa.Integer(), nullable=False, server_default="2000"),
        sa.Column("required_pages", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("recommended_pages", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_briefs_created_at", "briefs", ["created_at"])

    op.create_table(
        "runs",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("task", sa.Text(), nullable=False),
        sa.Column("repo", sa.Text(), nullable=True),
        sa.Column("agent", sa.Text(), nullable=True),
        sa.Column("model", sa.Text(), nullable=True),
        sa.Column("toolchain", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="running"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_runs_status", "runs", ["status"])
    op.create_index("ix_runs_started_at", "runs", ["started_at"])

    op.create_table(
        "run_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("run_id", sa.Text(), nullable=False),
        sa.Column("step_index", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("run_id", "step_index", name="uq_run_events_step"),
    )
    op.create_index("ix_run_events_run_id", "run_events", ["run_id"])
    op.create_index("ix_run_events_type", "run_events", ["event_type"])


def downgrade() -> None:
    op.drop_table("run_events")
    op.drop_table("runs")
    op.drop_table("briefs")
    op.drop_table("wiki_edges")
    op.drop_index("ix_wiki_pages_search", table_name="wiki_pages")
    op.drop_table("wiki_pages")

