from __future__ import annotations

import csv
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql import Select

from apps.models.inventory import (
    CatalogItem,
    InventoryLevel,
    StockMovement,
    StockMovementType,
    Warehouse,
)
from apps.schemas.inventory import (
    CatalogItemCreate,
    CatalogItemUpdate,
    InventoryLevelUpdate,
    LegacyTariffImportResult,
    StockMovementCreate,
    WarehouseCreate,
    WarehouseUpdate,
)


TWOPLACES = Decimal("0.01")
THREEPLACES = Decimal("0.001")


class DuplicateCatalogCodeError(Exception):
    pass


class DuplicateWarehouseNameError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


class LegacyImportFileError(Exception):
    pass


def money(value: Decimal) -> Decimal:
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def quantity(value: Decimal) -> Decimal:
    return value.quantize(THREEPLACES, rounding=ROUND_HALF_UP)


def get_catalog_item(db: Session, item_id: str) -> CatalogItem | None:
    return db.get(CatalogItem, item_id)


def get_catalog_item_by_code(db: Session, code: str) -> CatalogItem | None:
    return db.scalar(select(CatalogItem).where(CatalogItem.code == code.strip().upper()))


def list_catalog_items(
    db: Session,
    *,
    search: str | None = None,
    family: str | None = None,
    active_only: bool = False,
    limit: int = 500,
) -> list[CatalogItem]:
    statement = select(CatalogItem)
    if active_only:
        statement = statement.where(CatalogItem.is_active.is_(True))
    if family:
        statement = statement.where(CatalogItem.family == family)
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                CatalogItem.code.ilike(pattern),
                CatalogItem.description.ilike(pattern),
                CatalogItem.family.ilike(pattern),
            )
        )
    statement = statement.order_by(CatalogItem.family, CatalogItem.code).limit(limit)
    return list(db.scalars(statement).all())


def list_catalog_families(db: Session) -> list[str]:
    rows = db.scalars(select(CatalogItem.family).distinct().order_by(CatalogItem.family)).all()
    return [str(value) for value in rows]


def create_catalog_item(db: Session, payload: CatalogItemCreate) -> CatalogItem:
    item = CatalogItem(
        code=payload.code.upper(),
        family=payload.family,
        description=payload.description,
        unit=payload.unit,
        purchase_price=money(payload.purchase_price),
        sale_price=money(payload.sale_price),
        labor_hours=money(payload.labor_hours),
        supplier_name=payload.supplier_name.strip() if payload.supplier_name else None,
        tax_rate=money(payload.tax_rate),
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateCatalogCodeError from exc
    db.refresh(item)
    return item


def update_catalog_item(
    db: Session,
    item: CatalogItem,
    payload: CatalogItemUpdate,
) -> CatalogItem:
    changes = payload.model_dump(exclude_unset=True)
    if "code" in changes and payload.code is not None:
        item.code = payload.code.upper()
    if "family" in changes and payload.family is not None:
        item.family = payload.family
    if "description" in changes and payload.description is not None:
        item.description = payload.description
    if "unit" in changes and payload.unit is not None:
        item.unit = payload.unit
    if "purchase_price" in changes and payload.purchase_price is not None:
        item.purchase_price = money(payload.purchase_price)
    if "sale_price" in changes and payload.sale_price is not None:
        item.sale_price = money(payload.sale_price)
    if "labor_hours" in changes and payload.labor_hours is not None:
        item.labor_hours = money(payload.labor_hours)
    if "supplier_name" in changes:
        item.supplier_name = payload.supplier_name.strip() if payload.supplier_name else None
    if "tax_rate" in changes and payload.tax_rate is not None:
        item.tax_rate = money(payload.tax_rate)
    if "is_active" in changes and payload.is_active is not None:
        item.is_active = payload.is_active

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateCatalogCodeError from exc
    db.refresh(item)
    return item


def get_warehouse(db: Session, warehouse_id: str) -> Warehouse | None:
    return db.get(Warehouse, warehouse_id)


def get_warehouse_by_name(db: Session, name: str) -> Warehouse | None:
    return db.scalar(select(Warehouse).where(Warehouse.name == name.strip()))


def list_warehouses(db: Session, *, active_only: bool = False) -> list[Warehouse]:
    statement = select(Warehouse)
    if active_only:
        statement = statement.where(Warehouse.is_active.is_(True))
    return list(db.scalars(statement.order_by(Warehouse.name)).all())


def create_warehouse(db: Session, payload: WarehouseCreate) -> Warehouse:
    warehouse = Warehouse(
        name=payload.name,
        kind=payload.kind,
        location=payload.location.strip() if payload.location else None,
    )
    db.add(warehouse)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateWarehouseNameError from exc
    db.refresh(warehouse)
    return warehouse


def update_warehouse(
    db: Session,
    warehouse: Warehouse,
    payload: WarehouseUpdate,
) -> Warehouse:
    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes and payload.name is not None:
        warehouse.name = payload.name
    if "kind" in changes and payload.kind is not None:
        warehouse.kind = payload.kind
    if "location" in changes:
        warehouse.location = payload.location.strip() if payload.location else None
    if "is_active" in changes and payload.is_active is not None:
        warehouse.is_active = payload.is_active
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateWarehouseNameError from exc
    db.refresh(warehouse)
    return warehouse


def inventory_statement() -> Select[tuple[InventoryLevel]]:
    return select(InventoryLevel).options(
        selectinload(InventoryLevel.catalog_item),
        selectinload(InventoryLevel.warehouse),
    )


def get_inventory_level(db: Session, level_id: str) -> InventoryLevel | None:
    return db.scalar(inventory_statement().where(InventoryLevel.id == level_id))


def get_inventory_level_for_item(
    db: Session,
    *,
    catalog_item_id: str,
    warehouse_id: str,
) -> InventoryLevel | None:
    return db.scalar(
        inventory_statement().where(
            InventoryLevel.catalog_item_id == catalog_item_id,
            InventoryLevel.warehouse_id == warehouse_id,
        )
    )


def ensure_inventory_level(
    db: Session,
    *,
    catalog_item_id: str,
    warehouse_id: str,
) -> InventoryLevel:
    level = get_inventory_level_for_item(
        db,
        catalog_item_id=catalog_item_id,
        warehouse_id=warehouse_id,
    )
    if level is not None:
        return level
    level = InventoryLevel(
        catalog_item_id=catalog_item_id,
        warehouse_id=warehouse_id,
        stock=Decimal("0.000"),
        reserved=Decimal("0.000"),
        min_stock=Decimal("0.000"),
    )
    db.add(level)
    db.flush()
    return level


def list_inventory_levels(
    db: Session,
    *,
    warehouse_id: str | None = None,
    search: str | None = None,
    low_stock_only: bool = False,
    limit: int = 500,
) -> list[InventoryLevel]:
    statement = inventory_statement().join(InventoryLevel.catalog_item)
    if warehouse_id:
        statement = statement.where(InventoryLevel.warehouse_id == warehouse_id)
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                CatalogItem.code.ilike(pattern),
                CatalogItem.description.ilike(pattern),
                CatalogItem.family.ilike(pattern),
                InventoryLevel.barcode.ilike(pattern),
            )
        )
    if low_stock_only:
        statement = statement.where(
            InventoryLevel.min_stock > 0,
            InventoryLevel.stock - InventoryLevel.reserved <= InventoryLevel.min_stock,
        )
    statement = statement.order_by(CatalogItem.family, CatalogItem.code).limit(limit)
    return list(db.scalars(statement).unique().all())


def update_inventory_level(
    db: Session,
    level: InventoryLevel,
    payload: InventoryLevelUpdate,
) -> InventoryLevel:
    changes = payload.model_dump(exclude_unset=True)
    if "min_stock" in changes and payload.min_stock is not None:
        level.min_stock = quantity(payload.min_stock)
    if "shelf" in changes:
        level.shelf = payload.shelf.strip() if payload.shelf else None
    if "barcode" in changes:
        level.barcode = payload.barcode.strip() if payload.barcode else None
    db.commit()
    db.refresh(level)
    return level


def movement_statement() -> Select[tuple[StockMovement]]:
    return select(StockMovement).options(
        selectinload(StockMovement.catalog_item),
        selectinload(StockMovement.warehouse),
        selectinload(StockMovement.created_by),
    )


def list_stock_movements(
    db: Session,
    *,
    catalog_item_id: str | None = None,
    warehouse_id: str | None = None,
    work_order_id: str | None = None,
    limit: int = 200,
) -> list[StockMovement]:
    statement = movement_statement()
    if catalog_item_id:
        statement = statement.where(StockMovement.catalog_item_id == catalog_item_id)
    if warehouse_id:
        statement = statement.where(StockMovement.warehouse_id == warehouse_id)
    if work_order_id:
        statement = statement.where(StockMovement.work_order_id == work_order_id)
    statement = statement.order_by(StockMovement.movement_date.desc()).limit(limit)
    return list(db.scalars(statement).all())


def movement_delta(movement_type: StockMovementType, raw_quantity: Decimal) -> Decimal:
    normalized = quantity(raw_quantity)
    if movement_type in (StockMovementType.ENTRY, StockMovementType.RETURN):
        return abs(normalized)
    if movement_type in (StockMovementType.EXIT, StockMovementType.ASSIGNMENT):
        return -abs(normalized)
    return normalized


def create_stock_movement(
    db: Session,
    payload: StockMovementCreate,
    *,
    created_by_id: str,
) -> StockMovement:
    item = get_catalog_item(db, payload.catalog_item_id)
    warehouse = get_warehouse(db, payload.warehouse_id)
    if item is None or warehouse is None:
        raise ValueError("Artículo o almacén no disponible")

    level = ensure_inventory_level(
        db,
        catalog_item_id=item.id,
        warehouse_id=warehouse.id,
    )
    delta = movement_delta(payload.movement_type, payload.quantity)
    new_stock = quantity(level.stock + delta)
    if new_stock < 0:
        db.rollback()
        raise InsufficientStockError

    level.stock = new_stock
    movement = StockMovement(
        catalog_item_id=item.id,
        warehouse_id=warehouse.id,
        work_order_id=payload.work_order_id,
        created_by_id=created_by_id,
        movement_type=payload.movement_type.value,
        quantity=delta,
        unit_cost=money(
            payload.unit_cost if payload.unit_cost is not None else item.purchase_price
        ),
        reference=payload.reference.strip() if payload.reference else None,
        notes=payload.notes.strip() if payload.notes else None,
        movement_date=payload.movement_date or datetime.now(UTC),
    )
    db.add(movement)
    db.commit()
    return db.scalar(movement_statement().where(StockMovement.id == movement.id)) or movement


def decimal_from_csv(value: str | None, default: str = "0") -> Decimal:
    if value is None or not value.strip():
        return Decimal(default)
    normalized = value.strip().replace(",", ".")
    try:
        return Decimal(normalized)
    except InvalidOperation as exc:
        raise ValueError(f"Valor decimal no válido: {value}") from exc


def import_legacy_tariff_csv(
    db: Session,
    source_path: str,
) -> LegacyTariffImportResult:
    path = Path(source_path)
    if not path.exists() or not path.is_file():
        raise LegacyImportFileError(f"No se encontró el archivo {path}")

    warehouse_created = False
    warehouse = get_warehouse_by_name(db, "Almacén principal")
    if warehouse is None:
        warehouse = Warehouse(
            name="Almacén principal",
            kind="Almacén",
            location="Sede JR Energy Solutions",
        )
        db.add(warehouse)
        db.flush()
        warehouse_created = True

    created = 0
    updated = 0
    skipped = 0
    total_rows = 0

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"id", "code", "family", "description", "unit"}
        if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
            raise LegacyImportFileError("El CSV no contiene las columnas esperadas")

        for row in reader:
            total_rows += 1
            code = (row.get("code") or "").strip().upper()
            description = (row.get("description") or "").strip()
            if not code or not description:
                skipped += 1
                continue

            legacy_id = int(row["id"]) if row.get("id") else None
            match_conditions = [CatalogItem.code == code]
            if legacy_id is not None:
                match_conditions.append(CatalogItem.legacy_id == legacy_id)
            item = db.scalar(select(CatalogItem).where(or_(*match_conditions)))
            values = {
                "legacy_id": legacy_id,
                "code": code,
                "family": (row.get("family") or "General").strip() or "General",
                "description": description,
                "unit": (row.get("unit") or "ud").strip() or "ud",
                "purchase_price": money(decimal_from_csv(row.get("purchase_price"))),
                "sale_price": money(decimal_from_csv(row.get("sale_price"))),
                "labor_hours": money(decimal_from_csv(row.get("labor_hours"))),
                "supplier_name": (row.get("supplier") or "").strip() or None,
                "tax_rate": money(decimal_from_csv(row.get("igic_percent"), "7")),
                "is_active": (row.get("active") or "1").strip() not in {"0", "false", "False"},
            }
            if item is None:
                item = CatalogItem(**values)
                db.add(item)
                db.flush()
                created += 1
            else:
                for field, value in values.items():
                    setattr(item, field, value)
                updated += 1

            ensure_inventory_level(
                db,
                catalog_item_id=item.id,
                warehouse_id=warehouse.id,
            )

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise LegacyImportFileError("El tarifario contiene códigos duplicados") from exc

    return LegacyTariffImportResult(
        source_file=path.name,
        created=created,
        updated=updated,
        skipped=skipped,
        total_rows=total_rows,
        warehouse_created=warehouse_created,
    )
