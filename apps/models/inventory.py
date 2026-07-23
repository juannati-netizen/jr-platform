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
    from apps.models.work_order import WorkOrder


QUANTITY = Numeric(14, 3)
MONEY = Numeric(12, 2)
PERCENTAGE = Numeric(5, 2)
HOURS = Numeric(8, 2)


class StockMovementType(StrEnum):
    ENTRY = "entry"
    EXIT = "exit"
    ASSIGNMENT = "assignment"
    RETURN = "return"
    ADJUSTMENT = "adjustment"


def utc_now() -> datetime:
    return datetime.now(UTC)


class CatalogItem(Base):
    __tablename__ = "catalog_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    legacy_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    family: Mapped[str] = mapped_column(String(120), default="General", index=True)
    description: Mapped[str] = mapped_column(String(500), index=True)
    unit: Mapped[str] = mapped_column(String(20), default="ud")
    purchase_price: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0.00"))
    sale_price: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0.00"))
    labor_hours: Mapped[Decimal] = mapped_column(HOURS, default=Decimal("0.00"))
    supplier_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    tax_rate: Mapped[Decimal] = mapped_column(PERCENTAGE, default=Decimal("7.00"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    inventory_levels: Mapped[list[InventoryLevel]] = relationship(
        back_populates="catalog_item",
        cascade="all, delete-orphan",
    )


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    kind: Mapped[str] = mapped_column(String(60), default="Almacén")
    location: Mapped[str | None] = mapped_column(String(300), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    inventory_levels: Mapped[list[InventoryLevel]] = relationship(
        back_populates="warehouse",
        cascade="all, delete-orphan",
    )


class InventoryLevel(Base):
    __tablename__ = "inventory_levels"
    __table_args__ = (
        UniqueConstraint("catalog_item_id", "warehouse_id", name="uq_inventory_item_warehouse"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    catalog_item_id: Mapped[str] = mapped_column(
        ForeignKey("catalog_items.id", ondelete="CASCADE"),
        index=True,
    )
    warehouse_id: Mapped[str] = mapped_column(
        ForeignKey("warehouses.id", ondelete="CASCADE"),
        index=True,
    )
    stock: Mapped[Decimal] = mapped_column(QUANTITY, default=Decimal("0.000"))
    reserved: Mapped[Decimal] = mapped_column(QUANTITY, default=Decimal("0.000"))
    min_stock: Mapped[Decimal] = mapped_column(QUANTITY, default=Decimal("0.000"))
    shelf: Mapped[str | None] = mapped_column(String(80), nullable=True)
    barcode: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    catalog_item: Mapped[CatalogItem] = relationship(back_populates="inventory_levels")
    warehouse: Mapped[Warehouse] = relationship(back_populates="inventory_levels")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    catalog_item_id: Mapped[str] = mapped_column(
        ForeignKey("catalog_items.id", ondelete="RESTRICT"),
        index=True,
    )
    warehouse_id: Mapped[str] = mapped_column(
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
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
    movement_type: Mapped[str] = mapped_column(String(30), index=True)
    quantity: Mapped[Decimal] = mapped_column(QUANTITY)
    unit_cost: Mapped[Decimal] = mapped_column(MONEY, default=Decimal("0.00"))
    reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    movement_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    catalog_item: Mapped[CatalogItem] = relationship()
    warehouse: Mapped[Warehouse] = relationship()
    work_order: Mapped[WorkOrder | None] = relationship()
    created_by: Mapped[User] = relationship()
