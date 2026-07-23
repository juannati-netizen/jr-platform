"""Create catalog and inventory tables.

Revision ID: 20260723_0005
Revises: 20260723_0004
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260723_0005"
down_revision: str | None = "20260723_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "catalog_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("legacy_id", sa.Integer(), nullable=True),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("family", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("unit", sa.String(length=20), nullable=False),
        sa.Column("purchase_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("sale_price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("labor_hours", sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column("supplier_name", sa.String(length=180), nullable=True),
        sa.Column("tax_rate", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("legacy_id"),
    )
    op.create_index(op.f("ix_catalog_items_code"), "catalog_items", ["code"])
    op.create_index(op.f("ix_catalog_items_description"), "catalog_items", ["description"])
    op.create_index(op.f("ix_catalog_items_family"), "catalog_items", ["family"])
    op.create_index(op.f("ix_catalog_items_is_active"), "catalog_items", ["is_active"])

    op.create_table(
        "warehouses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("kind", sa.String(length=60), nullable=False),
        sa.Column("location", sa.String(length=300), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_warehouses_is_active"), "warehouses", ["is_active"])
    op.create_index(op.f("ix_warehouses_name"), "warehouses", ["name"])

    op.create_table(
        "inventory_levels",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("catalog_item_id", sa.String(length=36), nullable=False),
        sa.Column("warehouse_id", sa.String(length=36), nullable=False),
        sa.Column("stock", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("reserved", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("min_stock", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("shelf", sa.String(length=80), nullable=True),
        sa.Column("barcode", sa.String(length=120), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["catalog_item_id"], ["catalog_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "catalog_item_id",
            "warehouse_id",
            name="uq_inventory_item_warehouse",
        ),
    )
    op.create_index(op.f("ix_inventory_levels_barcode"), "inventory_levels", ["barcode"])
    op.create_index(
        op.f("ix_inventory_levels_catalog_item_id"),
        "inventory_levels",
        ["catalog_item_id"],
    )
    op.create_index(
        op.f("ix_inventory_levels_warehouse_id"),
        "inventory_levels",
        ["warehouse_id"],
    )

    op.create_table(
        "stock_movements",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("catalog_item_id", sa.String(length=36), nullable=False),
        sa.Column("warehouse_id", sa.String(length=36), nullable=False),
        sa.Column("work_order_id", sa.String(length=36), nullable=True),
        sa.Column("created_by_id", sa.String(length=36), nullable=False),
        sa.Column("movement_type", sa.String(length=30), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("unit_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("reference", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("movement_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["catalog_item_id"], ["catalog_items.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_stock_movements_catalog_item_id"),
        "stock_movements",
        ["catalog_item_id"],
    )
    op.create_index(
        op.f("ix_stock_movements_created_by_id"),
        "stock_movements",
        ["created_by_id"],
    )
    op.create_index(
        op.f("ix_stock_movements_movement_date"),
        "stock_movements",
        ["movement_date"],
    )
    op.create_index(
        op.f("ix_stock_movements_movement_type"),
        "stock_movements",
        ["movement_type"],
    )
    op.create_index(
        op.f("ix_stock_movements_warehouse_id"),
        "stock_movements",
        ["warehouse_id"],
    )
    op.create_index(
        op.f("ix_stock_movements_work_order_id"),
        "stock_movements",
        ["work_order_id"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_stock_movements_work_order_id"), table_name="stock_movements")
    op.drop_index(op.f("ix_stock_movements_warehouse_id"), table_name="stock_movements")
    op.drop_index(op.f("ix_stock_movements_movement_type"), table_name="stock_movements")
    op.drop_index(op.f("ix_stock_movements_movement_date"), table_name="stock_movements")
    op.drop_index(op.f("ix_stock_movements_created_by_id"), table_name="stock_movements")
    op.drop_index(op.f("ix_stock_movements_catalog_item_id"), table_name="stock_movements")
    op.drop_table("stock_movements")
    op.drop_index(op.f("ix_inventory_levels_warehouse_id"), table_name="inventory_levels")
    op.drop_index(op.f("ix_inventory_levels_catalog_item_id"), table_name="inventory_levels")
    op.drop_index(op.f("ix_inventory_levels_barcode"), table_name="inventory_levels")
    op.drop_table("inventory_levels")
    op.drop_index(op.f("ix_warehouses_name"), table_name="warehouses")
    op.drop_index(op.f("ix_warehouses_is_active"), table_name="warehouses")
    op.drop_table("warehouses")
    op.drop_index(op.f("ix_catalog_items_is_active"), table_name="catalog_items")
    op.drop_index(op.f("ix_catalog_items_family"), table_name="catalog_items")
    op.drop_index(op.f("ix_catalog_items_description"), table_name="catalog_items")
    op.drop_index(op.f("ix_catalog_items_code"), table_name="catalog_items")
    op.drop_table("catalog_items")
