from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import get_current_user, require_roles
from apps.db.session import get_db
from apps.models.user import User, UserRole
from apps.repositories.inventory import (
    InsufficientStockError,
    create_stock_movement,
    get_inventory_level,
    list_inventory_levels,
    list_stock_movements,
    update_inventory_level,
)
from apps.repositories.work_orders import get_work_order
from apps.schemas.inventory import (
    InventoryLevelRead,
    InventoryLevelUpdate,
    StockMovementCreate,
    StockMovementRead,
)

router = APIRouter()


@router.get("", response_model=list[InventoryLevelRead])
def read_inventory(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    warehouse_id: str | None = None,
    search: Annotated[str | None, Query(max_length=180)] = None,
    low_stock_only: bool = False,
    limit: Annotated[int, Query(ge=1, le=2000)] = 500,
) -> list[InventoryLevelRead]:
    return [
        InventoryLevelRead.from_entity(level)
        for level in list_inventory_levels(
            db,
            warehouse_id=warehouse_id,
            search=search,
            low_stock_only=low_stock_only,
            limit=limit,
        )
    ]


@router.patch("/{level_id}", response_model=InventoryLevelRead)
def change_inventory_level(
    level_id: str,
    payload: InventoryLevelUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> InventoryLevelRead:
    level = get_inventory_level(db, level_id)
    if level is None:
        raise HTTPException(status_code=404, detail="Registro de inventario no encontrado")
    updated = update_inventory_level(db, level, payload)
    refreshed = get_inventory_level(db, updated.id)
    return InventoryLevelRead.from_entity(refreshed or updated)


@router.get("/movements", response_model=list[StockMovementRead])
def read_movements(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    catalog_item_id: str | None = None,
    warehouse_id: str | None = None,
    work_order_id: str | None = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 200,
) -> list[StockMovementRead]:
    return [
        StockMovementRead.from_entity(item)
        for item in list_stock_movements(
            db,
            catalog_item_id=catalog_item_id,
            warehouse_id=warehouse_id,
            work_order_id=work_order_id,
            limit=limit,
        )
    ]


@router.post("/movements", response_model=StockMovementRead, status_code=status.HTTP_201_CREATED)
def add_movement(
    payload: StockMovementCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> StockMovementRead:
    if payload.work_order_id is not None and get_work_order(db, payload.work_order_id) is None:
        raise HTTPException(status_code=422, detail="El trabajo indicado no existe")
    try:
        movement = create_stock_movement(db, payload, created_by_id=current_user.id)
    except InsufficientStockError as exc:
        raise HTTPException(status_code=409, detail="No hay stock suficiente") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return StockMovementRead.from_entity(movement)
