"""create adventure sessions table

Revision ID: 20260302_0001
Revises:
Create Date: 2026-03-02 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260302_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "adventure_sessions",
        sa.Column("session_id", sa.String(length=255), primary_key=True),
        sa.Column("save_data", sa.String(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("adventure_sessions")
