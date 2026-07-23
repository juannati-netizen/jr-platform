from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.db.base import Base

if TYPE_CHECKING:
    from apps.models.user import User
    from apps.models.work_order import WorkOrder


MONEY = Numeric(12, 2)
PERCENTAGE = Numeric(5, 2)


class ExpenseCategory(StrEnum):
    MATERIALS = "materials"
    SUBCONTRACTING = "subcontracting"
    TRAVEL = "travel"
    TOOLS = "tools"
    SERVICES = "services"
    TAXES = "taxes"
    OTHER = "other"


class ExpenseStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


def utc_now() -> datetime:
    return datetime.now(UTC)


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(180), index=True)
    tax_id: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    supplier_id: Mapped[str | None] = mapped_column(
        ForeignKey("suppliers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    work_order_id: Mapped[str | None] = mapped_column(
        ForeignKey("work_orders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
    )
    description: Mapped[str] = mapped_column(String(300), index=True)
    category: Mapped[str] = mapped_column(
        String(30),
        default=ExpenseCategory.OTHER.value,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=ExpenseStatus.PENDING.value,
        index=True,
    )
    expense_date: Mapped[date] = mapped_column(Date, default=date.today, index=True)
    subtotal: Mapped[Decimal] = mapped_column(MONEY)
    tax_rate: Mapped[Decimal] = mapped_column(PERCENTAGE, default=Decimal("7.00"))
    tax_total: Mapped[Decimal] = mapped_column(MONEY)
    total: Mapped[Decimal] = mapped_column(MONEY)
    reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    supplier: Mapped[Supplier | None] = relationship()
    work_order: Mapped[WorkOrder | None] = relationship()
    created_by: Mapped[User] = relationship()
