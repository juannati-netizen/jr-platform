from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from apps.models.inventory import (
    InventoryLevel,
    StockMovement,
    StockMovementType,
)
from apps.schemas.work_order import UserReference


class CatalogItemCreate(BaseModel):
    code: str = Field(min_length=1, max_length=80)
    family: str = Field(default="General", min_length=1, max_length=120)
    description: str = Field(min_length=2, max_length=500)
    unit: str = Field(default="ud", min_length=1, max_length=20)
    purchase_price: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    sale_price: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    labor_hours: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    supplier_name: str | None = Field(default=None, max_length=180)
    tax_rate: Decimal = Field(default=Decimal("21.00"), ge=0, le=100, decimal_places=2)

    @field_validator("code", "family", "description", "unit")
    @classmethod
    def strip_required(cls, value: str) -> str:
        return value.strip()

    @field_validator("supplier_name", mode="before")
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class CatalogItemUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=80)
    family: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, min_length=2, max_length=500)
    unit: str | None = Field(default=None, min_length=1, max_length=20)
    purchase_price: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    sale_price: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    labor_hours: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    supplier_name: str | None = Field(default=None, max_length=180)
    tax_rate: Decimal | None = Field(default=None, ge=0, le=100, decimal_places=2)
    is_active: bool | None = None

    @field_validator("code", "family", "description", "unit")
    @classmethod
    def strip_optional(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @field_validator("supplier_name", mode="before")
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class CatalogItemRead(BaseModel):
    id: str
    legacy_id: int | None
    code: str
    family: str
    description: str
    unit: str
    purchase_price: Decimal
    sale_price: Decimal
    labor_hours: Decimal
    supplier_name: str | None
    tax_rate: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CatalogItemReference(BaseModel):
    id: str
    code: str
    description: str
    unit: str
    purchase_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class WarehouseCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    kind: str = Field(default="Almacén", min_length=2, max_length=60)
    location: str | None = Field(default=None, max_length=300)

    @field_validator("name", "kind")
    @classmethod
    def strip_required(cls, value: str) -> str:
        return value.strip()

    @field_validator("location", mode="before")
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class WarehouseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    kind: str | None = Field(default=None, min_length=2, max_length=60)
    location: str | None = Field(default=None, max_length=300)
    is_active: bool | None = None

    @field_validator("name", "kind")
    @classmethod
    def strip_optional(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @field_validator("location", mode="before")
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class WarehouseRead(BaseModel):
    id: str
    name: str
    kind: str
    location: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WarehouseReference(BaseModel):
    id: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class InventoryLevelRead(BaseModel):
    id: str
    catalog_item: CatalogItemReference
    warehouse: WarehouseReference
    stock: Decimal
    reserved: Decimal
    available: Decimal
    min_stock: Decimal
    low_stock: bool
    shelf: str | None
    barcode: str | None
    inventory_value: Decimal
    updated_at: datetime

    @classmethod
    def from_entity(cls, level: InventoryLevel) -> "InventoryLevelRead":
        available = level.stock - level.reserved
        return cls(
            id=level.id,
            catalog_item=CatalogItemReference.model_validate(level.catalog_item),
            warehouse=WarehouseReference.model_validate(level.warehouse),
            stock=level.stock,
            reserved=level.reserved,
            available=available,
            min_stock=level.min_stock,
            low_stock=level.min_stock > 0 and available <= level.min_stock,
            shelf=level.shelf,
            barcode=level.barcode,
            inventory_value=(level.stock * level.catalog_item.purchase_price).quantize(
                Decimal("0.01")
            ),
            updated_at=level.updated_at,
        )


class InventoryLevelUpdate(BaseModel):
    min_stock: Decimal | None = Field(default=None, ge=0, decimal_places=3)
    shelf: str | None = Field(default=None, max_length=80)
    barcode: str | None = Field(default=None, max_length=120)

    @field_validator("shelf", "barcode", mode="before")
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class StockMovementCreate(BaseModel):
    catalog_item_id: str
    warehouse_id: str
    work_order_id: str | None = None
    movement_type: StockMovementType
    quantity: Decimal = Field(decimal_places=3)
    unit_cost: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    reference: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=2000)
    movement_date: datetime | None = None

    @field_validator("work_order_id", "reference", "notes", mode="before")
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @model_validator(mode="after")
    def validate_quantity_and_assignment(self) -> "StockMovementCreate":
        if self.quantity == 0:
            raise ValueError("La cantidad no puede ser cero")
        if self.movement_type != StockMovementType.ADJUSTMENT and self.quantity < 0:
            raise ValueError("La cantidad debe ser positiva para este tipo de movimiento")
        if self.movement_type == StockMovementType.ASSIGNMENT and self.work_order_id is None:
            raise ValueError("La asignación de material requiere un trabajo")
        return self


class StockMovementRead(BaseModel):
    id: str
    catalog_item: CatalogItemReference
    warehouse: WarehouseReference
    work_order_id: str | None
    created_by: UserReference
    movement_type: StockMovementType
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    reference: str | None
    notes: str | None
    movement_date: datetime
    created_at: datetime

    @classmethod
    def from_entity(cls, movement: StockMovement) -> "StockMovementRead":
        return cls(
            id=movement.id,
            catalog_item=CatalogItemReference.model_validate(movement.catalog_item),
            warehouse=WarehouseReference.model_validate(movement.warehouse),
            work_order_id=movement.work_order_id,
            created_by=UserReference(
                id=movement.created_by.id,
                full_name=movement.created_by.full_name,
                email=movement.created_by.email,
            ),
            movement_type=StockMovementType(movement.movement_type),
            quantity=movement.quantity,
            unit_cost=movement.unit_cost,
            total_cost=(abs(movement.quantity) * movement.unit_cost).quantize(Decimal("0.01")),
            reference=movement.reference,
            notes=movement.notes,
            movement_date=movement.movement_date,
            created_at=movement.created_at,
        )


class LegacyTariffImportResult(BaseModel):
    source_file: str
    created: int
    updated: int
    skipped: int
    total_rows: int
    warehouse_created: bool
