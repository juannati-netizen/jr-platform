"""Create clients, work orders and notes.

Revision ID: 20260723_0002
Revises: 20260722_0001
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260723_0002"
down_revision: str | None = "20260722_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("tax_id", sa.String(length=32), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tax_id"),
    )
    op.create_index(op.f("ix_clients_name"), "clients", ["name"], unique=False)

    op.create_table(
        "work_orders",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("client_id", sa.String(length=36), nullable=False),
        sa.Column("assignee_id", sa.String(length=36), nullable=True),
        sa.Column("created_by_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assignee_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_work_orders_assignee_id"), "work_orders", ["assignee_id"])
    op.create_index(op.f("ix_work_orders_client_id"), "work_orders", ["client_id"])
    op.create_index(op.f("ix_work_orders_created_by_id"), "work_orders", ["created_by_id"])
    op.create_index(op.f("ix_work_orders_priority"), "work_orders", ["priority"])
    op.create_index(op.f("ix_work_orders_status"), "work_orders", ["status"])
    op.create_index(op.f("ix_work_orders_title"), "work_orders", ["title"])

    op.create_table(
        "work_order_notes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("work_order_id", sa.String(length=36), nullable=False),
        sa.Column("author_id", sa.String(length=36), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_work_order_notes_author_id"), "work_order_notes", ["author_id"])
    op.create_index(
        op.f("ix_work_order_notes_work_order_id"),
        "work_order_notes",
        ["work_order_id"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_work_order_notes_work_order_id"), table_name="work_order_notes")
    op.drop_index(op.f("ix_work_order_notes_author_id"), table_name="work_order_notes")
    op.drop_table("work_order_notes")
    op.drop_index(op.f("ix_work_orders_title"), table_name="work_orders")
    op.drop_index(op.f("ix_work_orders_status"), table_name="work_orders")
    op.drop_index(op.f("ix_work_orders_priority"), table_name="work_orders")
    op.drop_index(op.f("ix_work_orders_created_by_id"), table_name="work_orders")
    op.drop_index(op.f("ix_work_orders_client_id"), table_name="work_orders")
    op.drop_index(op.f("ix_work_orders_assignee_id"), table_name="work_orders")
    op.drop_table("work_orders")
    op.drop_index(op.f("ix_clients_name"), table_name="clients")
    op.drop_table("clients")
