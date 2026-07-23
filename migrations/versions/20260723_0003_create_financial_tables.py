"""Create quotes, invoices and payments.

Revision ID: 20260723_0003
Revises: 20260723_0002
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260723_0003"
down_revision: str | None = "20260723_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "quotes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("number", sa.String(length=40), nullable=False),
        sa.Column("client_id", sa.String(length=36), nullable=False),
        sa.Column("work_order_id", sa.String(length=36), nullable=True),
        sa.Column("created_by_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("subtotal", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("tax_total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("number"),
    )
    op.create_index(op.f("ix_quotes_client_id"), "quotes", ["client_id"])
    op.create_index(op.f("ix_quotes_created_by_id"), "quotes", ["created_by_id"])
    op.create_index(op.f("ix_quotes_number"), "quotes", ["number"])
    op.create_index(op.f("ix_quotes_status"), "quotes", ["status"])
    op.create_index(op.f("ix_quotes_work_order_id"), "quotes", ["work_order_id"])

    op.create_table(
        "quote_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("quote_id", sa.String(length=36), nullable=False),
        sa.Column("description", sa.String(length=300), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("tax_rate", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("line_subtotal", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("line_tax", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("line_total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["quote_id"], ["quotes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quote_items_quote_id"), "quote_items", ["quote_id"])

    op.create_table(
        "invoices",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("number", sa.String(length=40), nullable=False),
        sa.Column("client_id", sa.String(length=36), nullable=False),
        sa.Column("work_order_id", sa.String(length=36), nullable=True),
        sa.Column("source_quote_id", sa.String(length=36), nullable=True),
        sa.Column("created_by_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("subtotal", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("tax_total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("paid_total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["source_quote_id"], ["quotes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("number"),
        sa.UniqueConstraint("source_quote_id"),
    )
    op.create_index(op.f("ix_invoices_client_id"), "invoices", ["client_id"])
    op.create_index(op.f("ix_invoices_created_by_id"), "invoices", ["created_by_id"])
    op.create_index(op.f("ix_invoices_number"), "invoices", ["number"])
    op.create_index(op.f("ix_invoices_source_quote_id"), "invoices", ["source_quote_id"])
    op.create_index(op.f("ix_invoices_status"), "invoices", ["status"])
    op.create_index(op.f("ix_invoices_work_order_id"), "invoices", ["work_order_id"])

    op.create_table(
        "invoice_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("invoice_id", sa.String(length=36), nullable=False),
        sa.Column("description", sa.String(length=300), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("tax_rate", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("line_subtotal", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("line_tax", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("line_total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invoice_items_invoice_id"), "invoice_items", ["invoice_id"])

    op.create_table(
        "payments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("invoice_id", sa.String(length=36), nullable=False),
        sa.Column("recorded_by_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("method", sa.String(length=30), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reference", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recorded_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payments_invoice_id"), "payments", ["invoice_id"])
    op.create_index(op.f("ix_payments_recorded_by_id"), "payments", ["recorded_by_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_payments_recorded_by_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_invoice_id"), table_name="payments")
    op.drop_table("payments")
    op.drop_index(op.f("ix_invoice_items_invoice_id"), table_name="invoice_items")
    op.drop_table("invoice_items")
    op.drop_index(op.f("ix_invoices_work_order_id"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_status"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_source_quote_id"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_number"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_created_by_id"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_client_id"), table_name="invoices")
    op.drop_table("invoices")
    op.drop_index(op.f("ix_quote_items_quote_id"), table_name="quote_items")
    op.drop_table("quote_items")
    op.drop_index(op.f("ix_quotes_work_order_id"), table_name="quotes")
    op.drop_index(op.f("ix_quotes_status"), table_name="quotes")
    op.drop_index(op.f("ix_quotes_number"), table_name="quotes")
    op.drop_index(op.f("ix_quotes_created_by_id"), table_name="quotes")
    op.drop_index(op.f("ix_quotes_client_id"), table_name="quotes")
    op.drop_table("quotes")
