from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.db.base import Base

if TYPE_CHECKING:
    from apps.models.user import User


MONEY = Numeric(12, 2)
PERCENTAGE = Numeric(5, 2)


def utc_now() -> datetime:
    return datetime.now(UTC)


class TaxSystem(StrEnum):
    IGIC = "igic"
    IVA = "iva"


class TaxFilingModel(StrEnum):
    MODEL_420 = "420"


class TaxPeriodStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"


class TaxAdjustmentDirection(StrEnum):
    OUTPUT = "output"
    INPUT = "input"


class TaxConfiguration(Base):
    __tablename__ = "tax_configurations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tax_system: Mapped[str] = mapped_column(String(20), default=TaxSystem.IGIC.value)
    filing_model: Mapped[str] = mapped_column(String(20), default=TaxFilingModel.MODEL_420.value)
    filing_frequency: Mapped[str] = mapped_column(String(20), default="quarterly")
    monthly_tracking_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    default_tax_rate: Mapped[Decimal] = mapped_column(PERCENTAGE, default=Decimal("7.00"))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )


class TaxPeriod(Base):
    __tablename__ = "tax_periods"
    __table_args__ = (UniqueConstraint("year", "month", name="uq_tax_period_year_month"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    year: Mapped[int] = mapped_column(Integer, index=True)
    month: Mapped[int] = mapped_column(Integer, index=True)
    status: Mapped[str] = mapped_column(String(20), default=TaxPeriodStatus.OPEN.value)
    snapshot_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_by_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    closed_by: Mapped[User | None] = relationship()


class TaxAdjustment(Base):
    __tablename__ = "tax_adjustments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    year: Mapped[int] = mapped_column(Integer, index=True)
    month: Mapped[int] = mapped_column(Integer, index=True)
    direction: Mapped[str] = mapped_column(String(20), index=True)
    amount: Mapped[Decimal] = mapped_column(MONEY)
    description: Mapped[str] = mapped_column(String(500))
    created_by_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    created_by: Mapped[User] = relationship()
