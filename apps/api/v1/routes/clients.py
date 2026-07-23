from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import get_current_user
from apps.db.session import get_db
from apps.models.user import User
from apps.repositories.clients import (
    DuplicateTaxIdError,
    create_client,
    get_client,
    list_clients,
    update_client,
)
from apps.schemas.client import ClientCreate, ClientRead, ClientUpdate

router = APIRouter()


@router.get("", response_model=list[ClientRead])
def read_clients(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    search: Annotated[str | None, Query(max_length=180)] = None,
    active_only: bool = False,
) -> list[ClientRead]:
    return [
        ClientRead.model_validate(client)
        for client in list_clients(db, search=search, active_only=active_only)
    ]


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def add_client(
    payload: ClientCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> ClientRead:
    try:
        client = create_client(db, payload)
    except DuplicateTaxIdError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un cliente con ese identificador fiscal",
        ) from exc
    return ClientRead.model_validate(client)


@router.get("/{client_id}", response_model=ClientRead)
def read_client(
    client_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> ClientRead:
    client = get_client(db, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return ClientRead.model_validate(client)


@router.patch("/{client_id}", response_model=ClientRead)
def change_client(
    client_id: str,
    payload: ClientUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> ClientRead:
    client = get_client(db, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    try:
        updated = update_client(db, client, payload)
    except DuplicateTaxIdError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un cliente con ese identificador fiscal",
        ) from exc
    return ClientRead.model_validate(updated)
