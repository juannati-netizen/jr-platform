from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import require_roles
from apps.db.session import get_db
from apps.models.user import User, UserRole
from apps.repositories.procurement import (
    DuplicateSupplierTaxIdError,
    create_supplier,
    get_supplier,
    list_suppliers,
    update_supplier,
)
from apps.schemas.procurement import SupplierCreate, SupplierRead, SupplierUpdate

router = APIRouter()


@router.get("", response_model=list[SupplierRead])
def read_suppliers(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    search: Annotated[str | None, Query(max_length=180)] = None,
    active_only: bool = False,
) -> list[SupplierRead]:
    return [
        SupplierRead.model_validate(item)
        for item in list_suppliers(db, search=search, active_only=active_only)
    ]


@router.post("", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
def add_supplier(
    payload: SupplierCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> SupplierRead:
    try:
        supplier = create_supplier(db, payload)
    except DuplicateSupplierTaxIdError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un proveedor con ese identificador fiscal",
        ) from exc
    return SupplierRead.model_validate(supplier)


@router.get("/{supplier_id}", response_model=SupplierRead)
def read_supplier(
    supplier_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> SupplierRead:
    supplier = get_supplier(db, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return SupplierRead.model_validate(supplier)


@router.patch("/{supplier_id}", response_model=SupplierRead)
def change_supplier(
    supplier_id: str,
    payload: SupplierUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> SupplierRead:
    supplier = get_supplier(db, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    try:
        updated = update_supplier(db, supplier, payload)
    except DuplicateSupplierTaxIdError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un proveedor con ese identificador fiscal",
        ) from exc
    return SupplierRead.model_validate(updated)
