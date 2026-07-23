from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.db.base import Base

if TYPE_CHECKING:
    from apps.models.client import Client
    from apps.models.finance import Quote
    from apps.models.user import User
    from apps.models.work_order import WorkOrder


MONEY = Numeric(14, 2)


class LeadSource(StrEnum):
    WEB = "web"
    REFERRAL = "referral"
    CAMPAIGN = "campaign"
    CALL = "call"
    EVENT = "event"
    OTHER = "other"


class LeadStatus(StrEnum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    DISCARDED = "discarded"


class OpportunityStage(StrEnum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class CrmActivityType(StrEnum):
    TASK = "task"
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    FOLLOW_UP = "follow_up"


class ProjectStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


def utc_now() -> datetime:
    return datetime.now(UTC)


class Lead(Base):
    __tablename__ = "crm_leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(180), index=True)
    company: Mapped[str | None] = mapped_column(String(180), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(30), default=LeadSource.OTHER.value, index=True)
    status: Mapped[str] = mapped_column(String(30), default=LeadStatus.NEW.value, index=True)
    owner_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    converted_client_id: Mapped[str | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, unique=True
    )
    converted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    converted_by_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    owner: Mapped[User | None] = relationship(foreign_keys=[owner_id])
    converted_client: Mapped[Client | None] = relationship(foreign_keys=[converted_client_id])
    converted_by: Mapped[User | None] = relationship(foreign_keys=[converted_by_id])
    opportunities: Mapped[list[Opportunity]] = relationship(back_populates="lead")
    activities: Mapped[list[CrmActivity]] = relationship(back_populates="lead")


class Opportunity(Base):
    __tablename__ = "crm_opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(220), index=True)
    lead_id: Mapped[str | None] = mapped_column(
        ForeignKey("crm_leads.id", ondelete="SET NULL"), nullable=True, index=True
    )
    client_id: Mapped[str | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True
    )
    owner_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    stage: Mapped[str] = mapped_column(
        String(30), default=OpportunityStage.PROSPECTING.value, index=True
    )
    estimated_value: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0.00"))
    probability: Mapped[int] = mapped_column(Integer, default=10)
    expected_close: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    quote_id: Mapped[str | None] = mapped_column(
        ForeignKey("quotes.id", ondelete="SET NULL"), nullable=True, unique=True
    )
    converted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    converted_by_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    lead: Mapped[Lead | None] = relationship(back_populates="opportunities")
    client: Mapped[Client | None] = relationship(foreign_keys=[client_id])
    owner: Mapped[User | None] = relationship(foreign_keys=[owner_id])
    quote: Mapped[Quote | None] = relationship(foreign_keys=[quote_id])
    converted_by: Mapped[User | None] = relationship(foreign_keys=[converted_by_id])
    activities: Mapped[list[CrmActivity]] = relationship(back_populates="opportunity")
    stage_history: Mapped[list[OpportunityStageHistory]] = relationship(
        back_populates="opportunity",
        cascade="all, delete-orphan",
        order_by="OpportunityStageHistory.changed_at",
    )
    projects: Mapped[list[Project]] = relationship(back_populates="opportunity")


class CrmActivity(Base):
    __tablename__ = "crm_activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    opportunity_id: Mapped[str | None] = mapped_column(
        ForeignKey("crm_opportunities.id", ondelete="CASCADE"), nullable=True, index=True
    )
    lead_id: Mapped[str | None] = mapped_column(
        ForeignKey("crm_leads.id", ondelete="CASCADE"), nullable=True, index=True
    )
    assigned_to_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    activity_type: Mapped[str] = mapped_column(
        String(30), default=CrmActivityType.TASK.value, index=True
    )
    subject: Mapped[str] = mapped_column(String(220), index=True)
    due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    completed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    opportunity: Mapped[Opportunity | None] = relationship(back_populates="activities")
    lead: Mapped[Lead | None] = relationship(back_populates="activities")
    assigned_to: Mapped[User | None] = relationship(foreign_keys=[assigned_to_id])
    created_by: Mapped[User] = relationship(foreign_keys=[created_by_id])


class OpportunityStageHistory(Base):
    __tablename__ = "crm_opportunity_stage_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    opportunity_id: Mapped[str] = mapped_column(
        ForeignKey("crm_opportunities.id", ondelete="CASCADE"), index=True
    )
    previous_stage: Mapped[str | None] = mapped_column(String(30), nullable=True)
    new_stage: Mapped[str] = mapped_column(String(30))
    changed_by_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    change_source: Mapped[str] = mapped_column(String(40), default="ui")
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    opportunity: Mapped[Opportunity] = relationship(back_populates="stage_history")
    changed_by: Mapped[User | None] = relationship()


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(220), index=True)
    client_id: Mapped[str] = mapped_column(
        ForeignKey("clients.id", ondelete="RESTRICT"), index=True
    )
    opportunity_id: Mapped[str | None] = mapped_column(
        ForeignKey("crm_opportunities.id", ondelete="SET NULL"), nullable=True, index=True
    )
    work_order_id: Mapped[str | None] = mapped_column(
        ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True, unique=True
    )
    manager_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    status: Mapped[str] = mapped_column(String(30), default=ProjectStatus.PLANNED.value, index=True)
    location: Mapped[str | None] = mapped_column(String(300), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    planned_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    planned_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    budget: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0.00"))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    client: Mapped[Client] = relationship()
    opportunity: Mapped[Opportunity | None] = relationship(back_populates="projects")
    work_order: Mapped[WorkOrder | None] = relationship()
    manager: Mapped[User | None] = relationship(foreign_keys=[manager_id])
    created_by: Mapped[User] = relationship(foreign_keys=[created_by_id])
    documents: Mapped[list[ProjectDocument]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectDocument.created_at.desc()",
    )


class ProjectDocument(Base):
    __tablename__ = "project_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    uploaded_by_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(150), default="application/octet-stream")
    size_bytes: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(String(80), default="General", index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    project: Mapped[Project] = relationship(back_populates="documents")
    uploaded_by: Mapped[User] = relationship()
