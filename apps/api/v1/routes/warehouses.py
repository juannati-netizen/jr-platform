from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import get_current_user, require_roles
from apps.db.session import get_db
from apps.models.user import User, UserRole
from apps.repositories.inventory import (
    DuplicateWarehouseNameError,
    create_warehouse,
    get_warehouse,
    list_warehouses,
    update_warehouse,
)
from apps.schemas.inventory import WarehouseCreate, WarehouseRead, WarehouseUpdate

router = APIRouter()


@router.get("", response_model=list[WarehouseRead])
def read_warehouses(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    active_only: bool = False,
) -> list[WarehouseRead]:
    return [
        WarehouseRead.model_validate(item)
        for item in list_warehouses(db, active_only=active_only)
    ]


@router.post("", response_model=WarehouseRead, status_code=status.HTTP_201_CREATED)
def add_warehouse(
    payload: WarehouseCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> WarehouseRead:
    try:
        warehouse = create_warehouse(db, payload)
    except DuplicateWarehouseNameError as exc:
        raise HTTPException(status_code=409, detail="Ya existe un almacén con ese nombre") from exc
    return WarehouseRead.model_validate(warehouse)


@router.patch("/{warehouse_id}", response_model=WarehouseRead)
def change_warehouse(
    warehouse_id: str,
    payload: WarehouseUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> WarehouseRead:
    warehouse = get_warehouse(db, warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Almacén no encontrado")
    try:
        updated = update_warehouse(db, warehouse, payload)
    except DuplicateWarehouseNameError as exc:
        raise HTTPException(status_code=409, detail="Ya existe un almacén con ese nombre") from exc
    return WarehouseRead.model_validate(updated)
