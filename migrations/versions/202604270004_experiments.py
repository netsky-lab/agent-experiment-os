"""experiments

Revision ID: 202604270004
Revises: 202604270003
Create Date: 2026-04-27 00:00:04 UTC
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "202604270004"
down_revision: str | None = "202604270003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "experiments",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("hypothesis", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="draft"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "experiment_conditions",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("experiment_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("experiment_id", "name", name="uq_experiment_conditions_name"),
    )

    op.create_table(
        "experiment_run_results",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("experiment_id", sa.Text(), nullable=False),
        sa.Column("condition_id", sa.Text(), nullable=False),
        sa.Column("run_id", sa.Text(), nullable=False),
        sa.Column("metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("report", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["experiment_id"], ["experiments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["condition_id"], ["experiment_conditions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["run_id"], ["runs.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_experiment_run_results_experiment", "experiment_run_results", ["experiment_id"])
    op.create_index("ix_experiment_run_results_condition", "experiment_run_results", ["condition_id"])


def downgrade() -> None:
    op.drop_table("experiment_run_results")
    op.drop_table("experiment_conditions")
    op.drop_table("experiments")

