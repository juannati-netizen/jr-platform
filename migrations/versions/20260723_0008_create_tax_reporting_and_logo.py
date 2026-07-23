"""Create tax reporting and company branding.

Revision ID: 20260723_0008
Revises: 20260723_0007
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260723_0008"
down_revision: str | None = "20260723_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("company_profiles") as batch_op:
        batch_op.add_column(sa.Column("logo_data_url", sa.Text(), nullable=True))
        batch_op.add_column(
            sa.Column("brand_color", sa.String(length=7), nullable=False, server_default="#1976d2")
        )
        batch_op.add_column(sa.Column("document_footer", sa.String(length=500), nullable=True))

    op.create_table(
        "tax_configurations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tax_system", sa.String(length=20), nullable=False),
        sa.Column("filing_model", sa.String(length=20), nullable=False),
        sa.Column("filing_frequency", sa.String(length=20), nullable=False),
        sa.Column("monthly_tracking_enabled", sa.Boolean(), nullable=False),
        sa.Column("default_tax_rate", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "tax_periods",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("snapshot_json", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_by_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["closed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("year", "month", name="uq_tax_period_year_month"),
    )
    op.create_index(op.f("ix_tax_periods_month"), "tax_periods", ["month"])
    op.create_index(op.f("ix_tax_periods_year"), "tax_periods", ["year"])

    op.create_table(
        "tax_adjustments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("created_by_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tax_adjustments_created_by_id"), "tax_adjustments", ["created_by_id"])
    op.create_index(op.f("ix_tax_adjustments_direction"), "tax_adjustments", ["direction"])
    op.create_index(op.f("ix_tax_adjustments_month"), "tax_adjustments", ["month"])
    op.create_index(op.f("ix_tax_adjustments_year"), "tax_adjustments", ["year"])


def downgrade() -> None:
    op.drop_index(op.f("ix_tax_adjustments_year"), table_name="tax_adjustments")
    op.drop_index(op.f("ix_tax_adjustments_month"), table_name="tax_adjustments")
    op.drop_index(op.f("ix_tax_adjustments_direction"), table_name="tax_adjustments")
    op.drop_index(op.f("ix_tax_adjustments_created_by_id"), table_name="tax_adjustments")
    op.drop_table("tax_adjustments")
    op.drop_index(op.f("ix_tax_periods_year"), table_name="tax_periods")
    op.drop_index(op.f("ix_tax_periods_month"), table_name="tax_periods")
    op.drop_table("tax_periods")
    op.drop_table("tax_configurations")

    with op.batch_alter_table("company_profiles") as batch_op:
        batch_op.drop_column("document_footer")
        batch_op.drop_column("brand_color")
        batch_op.drop_column("logo_data_url")
