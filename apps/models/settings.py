from __future__ import annotations

from datetime import UTC, date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.db.base import Base

if TYPE_CHECKING:
    from apps.models.user import User


def utc_now() -> datetime:
    return datetime.now(UTC)


class FiscalYearStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"


class VerifactuMode(StrEnum):
    DISABLED = "disabled"
    PREPARATION = "preparation"
    TEST = "test"


class AiProvider(StrEnum):
    DISABLED = "disabled"
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    LOCAL = "local"
    CUSTOM = "custom"


class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    legal_name: Mapped[str] = mapped_column(String(220), default="")
    trade_name: Mapped[str | None] = mapped_column(String(220), nullable=True)
    tax_id: Mapped[str] = mapped_column(String(32), default="")
    legal_form: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tax_regime: Mapped[str | None] = mapped_column(String(180), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    province: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str] = mapped_column(String(120), default="España")
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    website: Mapped[str | None] = mapped_column(String(300), nullable=True)
    iban: Mapped[str | None] = mapped_column(String(50), nullable=True)
    invoice_prefix: Mapped[str] = mapped_column(String(20), default="F")
    quote_prefix: Mapped[str] = mapped_column(String(20), default="P")
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    timezone: Mapped[str] = mapped_column(String(80), default="Europe/Madrid")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class FiscalYear(Base):
    __tablename__ = "fiscal_years"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    year: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default=FiscalYearStatus.OPEN.value, index=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    opened_by_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_by_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    opened_by: Mapped[User | None] = relationship(foreign_keys=[opened_by_id])
    closed_by: Mapped[User | None] = relationship(foreign_keys=[closed_by_id])


class VerifactuConfiguration(Base):
    __tablename__ = "verifactu_configurations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    mode: Mapped[str] = mapped_column(String(30), default=VerifactuMode.DISABLED.value)
    system_name: Mapped[str] = mapped_column(String(180), default="JR Platform")
    system_version: Mapped[str] = mapped_column(String(60), default="0.10.0")
    producer_name: Mapped[str | None] = mapped_column(String(220), nullable=True)
    producer_tax_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    qr_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    hash_chain_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    event_log_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    aeat_transmission_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    responsible_declaration_signed: Mapped[bool] = mapped_column(Boolean, default=False)
    certificate_alias: Mapped[str | None] = mapped_column(String(180), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class AiConfiguration(Base):
    __tablename__ = "ai_configurations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    provider: Mapped[str] = mapped_column(String(40), default=AiProvider.DISABLED.value)
    model: Mapped[str | None] = mapped_column(String(180), nullable=True)
    assistant_name: Mapped[str] = mapped_column(String(120), default="Asistente JR")
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    allow_customer_data: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_financial_data: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_document_content: Mapped[bool] = mapped_column(Boolean, default=False)
    human_review_required: Mapped[bool] = mapped_column(Boolean, default=True)
    retention_days: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class ConfigurationEvent(Base):
    __tablename__ = "configuration_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    category: Mapped[str] = mapped_column(String(40), index=True)
    action: Mapped[str] = mapped_column(String(80), index=True)
    summary: Mapped[str] = mapped_column(String(500))
    actor_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    actor: Mapped[User | None] = relationship()
