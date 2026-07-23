from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import get_current_user, require_roles
from apps.core.config import settings
from apps.db.session import get_db
from apps.models.user import User, UserRole
from apps.repositories.inventory import (
    DuplicateCatalogCodeError,
    LegacyImportFileError,
    create_catalog_item,
    get_catalog_item,
    import_legacy_tariff_csv,
    list_catalog_families,
    list_catalog_items,
    update_catalog_item,
)
from apps.schemas.inventory import (
    CatalogItemCreate,
    CatalogItemRead,
    CatalogItemUpdate,
    LegacyTariffImportResult,
)

router = APIRouter()


@router.get("", response_model=list[CatalogItemRead])
def read_catalog(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    search: Annotated[str | None, Query(max_length=180)] = None,
    family: Annotated[str | None, Query(max_length=120)] = None,
    active_only: bool = False,
    limit: Annotated[int, Query(ge=1, le=2000)] = 500,
) -> list[CatalogItemRead]:
    return [
        CatalogItemRead.model_validate(item)
        for item in list_catalog_items(
            db,
            search=search,
            family=family,
            active_only=active_only,
            limit=limit,
        )
    ]


@router.get("/families", response_model=list[str])
def read_families(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[str]:
    return list_catalog_families(db)


@router.post("", response_model=CatalogItemRead, status_code=status.HTTP_201_CREATED)
def add_catalog_item(
    payload: CatalogItemCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> CatalogItemRead:
    try:
        item = create_catalog_item(db, payload)
    except DuplicateCatalogCodeError as exc:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un artículo con ese código",
        ) from exc
    return CatalogItemRead.model_validate(item)


@router.post("/import-legacy", response_model=LegacyTariffImportResult)
def import_legacy_catalog(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> LegacyTariffImportResult:
    try:
        return import_legacy_tariff_csv(db, settings.legacy_tariff_csv_path)
    except LegacyImportFileError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{item_id}", response_model=CatalogItemRead)
def read_catalog_item(
    item_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> CatalogItemRead:
    item = get_catalog_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    return CatalogItemRead.model_validate(item)


@router.patch("/{item_id}", response_model=CatalogItemRead)
def change_catalog_item(
    item_id: str,
    payload: CatalogItemUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> CatalogItemRead:
    item = get_catalog_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    try:
        updated = update_catalog_item(db, item, payload)
    except DuplicateCatalogCodeError as exc:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un artículo con ese código",
        ) from exc
    return CatalogItemRead.model_validate(updated)
