"""Create CRM, projects and project document tables.

Revision ID: 20260723_0006
Revises: 20260723_0005
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260723_0006"
down_revision: str | None = "20260723_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "crm_leads",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("company", sa.String(length=180), nullable=True),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("source", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("owner_id", sa.String(length=36), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("converted_client_id", sa.String(length=36), nullable=True),
        sa.Column("converted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("converted_by_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["converted_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["converted_client_id"], ["clients.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("converted_client_id"),
    )
    for column in ("company", "email", "name", "owner_id", "source", "status"):
        op.create_index(op.f(f"ix_crm_leads_{column}"), "crm_leads", [column])

    op.create_table(
        "crm_opportunities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("lead_id", sa.String(length=36), nullable=True),
        sa.Column("client_id", sa.String(length=36), nullable=True),
        sa.Column("owner_id", sa.String(length=36), nullable=True),
        sa.Column("stage", sa.String(length=30), nullable=False),
        sa.Column("estimated_value", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("probability", sa.Integer(), nullable=False),
        sa.Column("expected_close", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("quote_id", sa.String(length=36), nullable=True),
        sa.Column("converted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("converted_by_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["converted_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["lead_id"], ["crm_leads.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["quote_id"], ["quotes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("quote_id"),
    )
    for column in ("client_id", "expected_close", "lead_id", "owner_id", "stage", "title"):
        op.create_index(
            op.f(f"ix_crm_opportunities_{column}"),
            "crm_opportunities",
            [column],
        )

    op.create_table(
        "crm_activities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("opportunity_id", sa.String(length=36), nullable=True),
        sa.Column("lead_id", sa.String(length=36), nullable=True),
        sa.Column("assigned_to_id", sa.String(length=36), nullable=True),
        sa.Column("created_by_id", sa.String(length=36), nullable=False),
        sa.Column("activity_type", sa.String(length=30), nullable=False),
        sa.Column("subject", sa.String(length=220), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assigned_to_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["lead_id"], ["crm_leads.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["opportunity_id"], ["crm_opportunities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "activity_type",
        "assigned_to_id",
        "completed",
        "created_by_id",
        "due_at",
        "lead_id",
        "opportunity_id",
        "subject",
    ):
        op.create_index(op.f(f"ix_crm_activities_{column}"), "crm_activities", [column])

    op.create_table(
        "crm_opportunity_stage_history",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("opportunity_id", sa.String(length=36), nullable=False),
        sa.Column("previous_stage", sa.String(length=30), nullable=True),
        sa.Column("new_stage", sa.String(length=30), nullable=False),
        sa.Column("changed_by_id", sa.String(length=36), nullable=True),
        sa.Column("change_source", sa.String(length=40), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["changed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["opportunity_id"], ["crm_opportunities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_crm_opportunity_stage_history_opportunity_id"),
        "crm_opportunity_stage_history",
        ["opportunity_id"],
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=220), nullable=False),
        sa.Column("client_id", sa.String(length=36), nullable=False),
        sa.Column("opportunity_id", sa.String(length=36), nullable=True),
        sa.Column("work_order_id", sa.String(length=36), nullable=True),
        sa.Column("manager_id", sa.String(length=36), nullable=True),
        sa.Column("created_by_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("location", sa.String(length=300), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("planned_start", sa.Date(), nullable=True),
        sa.Column("planned_end", sa.Date(), nullable=True),
        sa.Column("actual_end", sa.Date(), nullable=True),
        sa.Column("budget", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["manager_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["opportunity_id"], ["crm_opportunities.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("work_order_id"),
    )
    for column in (
        "client_id",
        "code",
        "created_by_id",
        "manager_id",
        "name",
        "opportunity_id",
        "status",
    ):
        op.create_index(op.f(f"ix_projects_{column}"), "projects", [column])

    op.create_table(
        "project_documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("uploaded_by_id", sa.String(length=36), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=150), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_documents_category"), "project_documents", ["category"])
    op.create_index(op.f("ix_project_documents_project_id"), "project_documents", ["project_id"])
    op.create_index(
        op.f("ix_project_documents_uploaded_by_id"),
        "project_documents",
        ["uploaded_by_id"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_project_documents_uploaded_by_id"), table_name="project_documents")
    op.drop_index(op.f("ix_project_documents_project_id"), table_name="project_documents")
    op.drop_index(op.f("ix_project_documents_category"), table_name="project_documents")
    op.drop_table("project_documents")
    for column in (
        "status",
        "opportunity_id",
        "name",
        "manager_id",
        "created_by_id",
        "code",
        "client_id",
    ):
        op.drop_index(op.f(f"ix_projects_{column}"), table_name="projects")
    op.drop_table("projects")
    op.drop_index(
        op.f("ix_crm_opportunity_stage_history_opportunity_id"),
        table_name="crm_opportunity_stage_history",
    )
    op.drop_table("crm_opportunity_stage_history")
    for column in (
        "subject",
        "opportunity_id",
        "lead_id",
        "due_at",
        "created_by_id",
        "completed",
        "assigned_to_id",
        "activity_type",
    ):
        op.drop_index(op.f(f"ix_crm_activities_{column}"), table_name="crm_activities")
    op.drop_table("crm_activities")
    for column in ("title", "stage", "owner_id", "lead_id", "expected_close", "client_id"):
        op.drop_index(op.f(f"ix_crm_opportunities_{column}"), table_name="crm_opportunities")
    op.drop_table("crm_opportunities")
    for column in ("status", "source", "owner_id", "name", "email", "company"):
        op.drop_index(op.f(f"ix_crm_leads_{column}"), table_name="crm_leads")
    op.drop_table("crm_leads")
