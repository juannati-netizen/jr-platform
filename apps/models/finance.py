from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.db.base import Base

if TYPE_CHECKING:
    from apps.models.client import Client
    from apps.models.user import User
    from apps.models.work_order import WorkOrder


MONEY = Numeric(12, 2)
QUANTITY = Numeric(10, 2)
PERCENTAGE = Numeric(5, 2)


class QuoteStatus(StrEnum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class InvoiceStatus(StrEnum):
    ISSUED = "issued"
    PARTIAL = "partial"
    PAID = "paid"
    CANCELLED = "cancelled"


class PaymentMethod(StrEnum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CARD = "card"
    DIRECT_DEBIT = "direct_debit"
    OTHER = "other"


def utc_now() -> datetime:
    return datetime.now(UTC)


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    client_id: Mapped[str] = mapped_column(
        ForeignKey("clients.id", ondelete="RESTRICT"), index=True
    )
    work_order_id: Mapped[str | None] = mapped_column(
        ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), default=QuoteStatus.DRAFT.value, index=True)
    issue_date: Mapped[date] = mapped_column(Date, default=date.today)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    subtotal: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0.00"))
    tax_total: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0.00"))
    total: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0.00"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    client: Mapped[Client] = relationship()
    work_order: Mapped[WorkOrder | None] = relationship()
    created_by: Mapped[User] = relationship()
    items: Mapped[list[QuoteItem]] = relationship(
        back_populates="quote",
        cascade="all, delete-orphan",
        order_by="QuoteItem.position",
    )
    invoice: Mapped[Invoice | None] = relationship(back_populates="source_quote", uselist=False)


class QuoteItem(Base):
    __tablename__ = "quote_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    quote_id: Mapped[str] = mapped_column(ForeignKey("quotes.id", ondelete="CASCADE"), index=True)
    description: Mapped[str] = mapped_column(String(300))
    quantity: Mapped[Decimal] = mapped_column(QUANTITY)
    unit_price: Mapped[Decimal] = mapped_column(MONEY)
    tax_rate: Mapped[Decimal] = mapped_column(PERCENTAGE)
    line_subtotal: Mapped[Decimal] = mapped_column(MONEY)
    line_tax: Mapped[Decimal] = mapped_column(MONEY)
    line_total: Mapped[Decimal] = mapped_column(MONEY)
    position: Mapped[int] = mapped_column(Integer, default=0)

    quote: Mapped[Quote] = relationship(back_populates="items")


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    client_id: Mapped[str] = mapped_column(
        ForeignKey("clients.id", ondelete="RESTRICT"), index=True
    )
    work_order_id: Mapped[str | None] = mapped_column(
        ForeignKey("work_orders.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source_quote_id: Mapped[str | None] = mapped_column(
        ForeignKey("quotes.id", ondelete="SET NULL"), nullable=True, unique=True, index=True
    )
    created_by_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), default=InvoiceStatus.ISSUED.value, index=True)
    issue_date: Mapped[date] = mapped_column(Date, default=date.today)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    subtotal: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0.00"))
    tax_total: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0.00"))
    total: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0.00"))
    paid_total: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0.00"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    client: Mapped[Client] = relationship()
    work_order: Mapped[WorkOrder | None] = relationship()
    source_quote: Mapped[Quote | None] = relationship(back_populates="invoice")
    created_by: Mapped[User] = relationship()
    items: Mapped[list[InvoiceItem]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan",
        order_by="InvoiceItem.position",
    )
    payments: Mapped[list[Payment]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan",
        order_by="Payment.paid_at",
    )


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    invoice_id: Mapped[str] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"), index=True
    )
    description: Mapped[str] = mapped_column(String(300))
    quantity: Mapped[Decimal] = mapped_column(QUANTITY)
    unit_price: Mapped[Decimal] = mapped_column(MONEY)
    tax_rate: Mapped[Decimal] = mapped_column(PERCENTAGE)
    line_subtotal: Mapped[Decimal] = mapped_column(MONEY)
    line_tax: Mapped[Decimal] = mapped_column(MONEY)
    line_total: Mapped[Decimal] = mapped_column(MONEY)
    position: Mapped[int] = mapped_column(Integer, default=0)

    invoice: Mapped[Invoice] = relationship(back_populates="items")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    invoice_id: Mapped[str] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"), index=True
    )
    recorded_by_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    amount: Mapped[Decimal] = mapped_column(MONEY)
    method: Mapped[str] = mapped_column(String(30), default=PaymentMethod.BANK_TRANSFER.value)
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    invoice: Mapped[Invoice] = relationship(back_populates="payments")
    recorded_by: Mapped[User] = relationship()
