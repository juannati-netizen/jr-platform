"""Create company, fiscal year, VERI*FACTU and AI settings.

Revision ID: 20260723_0007
Revises: 20260723_0006
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260723_0007"
down_revision: str | None = "20260723_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "company_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("legal_name", sa.String(length=220), nullable=False),
        sa.Column("trade_name", sa.String(length=220), nullable=True),
        sa.Column("tax_id", sa.String(length=32), nullable=False),
        sa.Column("legal_form", sa.String(length=120), nullable=True),
        sa.Column("tax_regime", sa.String(length=180), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("postal_code", sa.String(length=20), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("province", sa.String(length=120), nullable=True),
        sa.Column("country", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("website", sa.String(length=300), nullable=True),
        sa.Column("iban", sa.String(length=50), nullable=True),
        sa.Column("invoice_prefix", sa.String(length=20), nullable=False),
        sa.Column("quote_prefix", sa.String(length=20), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("timezone", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "fiscal_years",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("opened_by_id", sa.String(length=36), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_by_id", sa.String(length=36), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["closed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["opened_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("year"),
    )
    op.create_index(op.f("ix_fiscal_years_status"), "fiscal_years", ["status"])
    op.create_index(op.f("ix_fiscal_years_year"), "fiscal_years", ["year"])

    op.create_table(
        "verifactu_configurations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("mode", sa.String(length=30), nullable=False),
        sa.Column("system_name", sa.String(length=180), nullable=False),
        sa.Column("system_version", sa.String(length=60), nullable=False),
        sa.Column("producer_name", sa.String(length=220), nullable=True),
        sa.Column("producer_tax_id", sa.String(length=32), nullable=True),
        sa.Column("qr_enabled", sa.Boolean(), nullable=False),
        sa.Column("hash_chain_enabled", sa.Boolean(), nullable=False),
        sa.Column("event_log_enabled", sa.Boolean(), nullable=False),
        sa.Column("aeat_transmission_enabled", sa.Boolean(), nullable=False),
        sa.Column("responsible_declaration_signed", sa.Boolean(), nullable=False),
        sa.Column("certificate_alias", sa.String(length=180), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "ai_configurations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("model", sa.String(length=180), nullable=True),
        sa.Column("assistant_name", sa.String(length=120), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=True),
        sa.Column("allow_customer_data", sa.Boolean(), nullable=False),
        sa.Column("allow_financial_data", sa.Boolean(), nullable=False),
        sa.Column("allow_document_content", sa.Boolean(), nullable=False),
        sa.Column("human_review_required", sa.Boolean(), nullable=False),
        sa.Column("retention_days", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "configuration_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("summary", sa.String(length=500), nullable=False),
        sa.Column("actor_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_configuration_events_action"), "configuration_events", ["action"])
    op.create_index(op.f("ix_configuration_events_actor_id"), "configuration_events", ["actor_id"])
    op.create_index(
        op.f("ix_configuration_events_category"), "configuration_events", ["category"]
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_configuration_events_category"), table_name="configuration_events"
    )
    op.drop_index(op.f("ix_configuration_events_actor_id"), table_name="configuration_events")
    op.drop_index(op.f("ix_configuration_events_action"), table_name="configuration_events")
    op.drop_table("configuration_events")
    op.drop_table("ai_configurations")
    op.drop_table("verifactu_configurations")
    op.drop_index(op.f("ix_fiscal_years_year"), table_name="fiscal_years")
    op.drop_index(op.f("ix_fiscal_years_status"), table_name="fiscal_years")
    op.drop_table("fiscal_years")
    op.drop_table("company_profiles")
