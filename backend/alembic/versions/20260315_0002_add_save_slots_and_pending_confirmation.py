"""add save slots and pending confirmation columns

Revision ID: 20260315_0002
Revises: 20260302_0001
Create Date: 2026-03-15 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260315_0002"
down_revision = "20260302_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("adventure_sessions") as batch_op:
        batch_op.add_column(sa.Column("pending_action", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("pending_slot_name", sa.String(length=255), nullable=True))

    op.create_table(
        "adventure_save_slots",
        sa.Column("session_id", sa.String(length=255), primary_key=True),
        sa.Column("slot_name", sa.String(length=255), primary_key=True),
        sa.Column("save_data", sa.String(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("adventure_save_slots")
    with op.batch_alter_table("adventure_sessions") as batch_op:
        batch_op.drop_column("pending_slot_name")
        batch_op.drop_column("pending_action")
