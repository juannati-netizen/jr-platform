from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import get_current_user
from apps.db.session import get_db
from apps.models.user import User
from apps.models.work_order import WorkOrderStatus
from apps.repositories.clients import get_client
from apps.repositories.users import get_user_by_id
from apps.repositories.work_orders import (
    add_note,
    create_work_order,
    get_work_order,
    list_work_orders,
    update_work_order,
)
from apps.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderNoteCreate,
    WorkOrderNoteRead,
    WorkOrderRead,
    WorkOrderUpdate,
)

router = APIRouter()


def validate_references(
    db: Session,
    *,
    client_id: str | None,
    assignee_id: str | None,
) -> None:
    if client_id is not None:
        client = get_client(db, client_id)
        if client is None or not client.is_active:
            raise HTTPException(status_code=422, detail="El cliente indicado no está disponible")
    if assignee_id is not None:
        assignee = get_user_by_id(db, assignee_id)
        if assignee is None or not assignee.is_active:
            raise HTTPException(
                status_code=422,
                detail="El responsable indicado no está disponible",
            )


@router.get("", response_model=list[WorkOrderRead])
def read_work_orders(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    work_status: Annotated[WorkOrderStatus | None, Query(alias="status")] = None,
    client_id: str | None = None,
    assigned_to_me: bool = False,
) -> list[WorkOrderRead]:
    assignee_id = current_user.id if assigned_to_me else None
    return [
        WorkOrderRead.from_entity(item)
        for item in list_work_orders(
            db,
            status=work_status,
            client_id=client_id,
            assignee_id=assignee_id,
        )
    ]


@router.post("", response_model=WorkOrderRead, status_code=status.HTTP_201_CREATED)
def add_work_order(
    payload: WorkOrderCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> WorkOrderRead:
    validate_references(db, client_id=payload.client_id, assignee_id=payload.assignee_id)
    item = create_work_order(db, payload, created_by_id=current_user.id)
    return WorkOrderRead.from_entity(item)


@router.get("/{work_order_id}", response_model=WorkOrderRead)
def read_work_order(
    work_order_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> WorkOrderRead:
    item = get_work_order(db, work_order_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    return WorkOrderRead.from_entity(item)


@router.patch("/{work_order_id}", response_model=WorkOrderRead)
def change_work_order(
    work_order_id: str,
    payload: WorkOrderUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> WorkOrderRead:
    item = get_work_order(db, work_order_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    changes = payload.model_dump(exclude_unset=True)
    validate_references(
        db,
        client_id=payload.client_id if "client_id" in changes else None,
        assignee_id=payload.assignee_id if "assignee_id" in changes else None,
    )
    updated = update_work_order(db, item, payload)
    return WorkOrderRead.from_entity(updated)


@router.get("/{work_order_id}/notes", response_model=list[WorkOrderNoteRead])
def read_notes(
    work_order_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[WorkOrderNoteRead]:
    item = get_work_order(db, work_order_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    return [WorkOrderNoteRead.from_entity(note) for note in item.notes]


@router.post(
    "/{work_order_id}/notes",
    response_model=WorkOrderNoteRead,
    status_code=status.HTTP_201_CREATED,
)
def create_note(
    work_order_id: str,
    payload: WorkOrderNoteCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> WorkOrderNoteRead:
    item = get_work_order(db, work_order_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    note = add_note(db, item, author_id=current_user.id, content=payload.content)
    return WorkOrderNoteRead.from_entity(note)
