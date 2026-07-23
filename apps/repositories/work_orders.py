from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from apps.models.work_order import WorkOrder, WorkOrderNote, WorkOrderStatus
from apps.schemas.work_order import WorkOrderCreate, WorkOrderUpdate


def _with_details() -> tuple[Any, ...]:
    return (
        joinedload(WorkOrder.client),
        joinedload(WorkOrder.assignee),
        joinedload(WorkOrder.created_by),
        selectinload(WorkOrder.notes).joinedload(WorkOrderNote.author),
    )


def get_work_order(db: Session, work_order_id: str) -> WorkOrder | None:
    statement = select(WorkOrder).where(WorkOrder.id == work_order_id).options(*_with_details())
    return db.scalar(statement)


def list_work_orders(
    db: Session,
    *,
    status: WorkOrderStatus | None = None,
    client_id: str | None = None,
    assignee_id: str | None = None,
) -> list[WorkOrder]:
    statement = select(WorkOrder).options(*_with_details())
    if status is not None:
        statement = statement.where(WorkOrder.status == status.value)
    if client_id is not None:
        statement = statement.where(WorkOrder.client_id == client_id)
    if assignee_id is not None:
        statement = statement.where(WorkOrder.assignee_id == assignee_id)
    statement = statement.order_by(WorkOrder.created_at.desc())
    return list(db.scalars(statement).unique().all())


def create_work_order(
    db: Session,
    payload: WorkOrderCreate,
    *,
    created_by_id: str,
) -> WorkOrder:
    completed_at = datetime.now(UTC) if payload.status is WorkOrderStatus.COMPLETED else None
    item = WorkOrder(
        client_id=payload.client_id,
        assignee_id=payload.assignee_id,
        created_by_id=created_by_id,
        title=payload.title.strip(),
        description=payload.description.strip() if payload.description else None,
        status=payload.status.value,
        priority=payload.priority.value,
        scheduled_for=payload.scheduled_for,
        completed_at=completed_at,
    )
    db.add(item)
    db.commit()
    return get_work_order(db, item.id) or item


def update_work_order(
    db: Session,
    item: WorkOrder,
    payload: WorkOrderUpdate,
) -> WorkOrder:
    changes = payload.model_dump(exclude_unset=True)
    if "client_id" in changes and payload.client_id is not None:
        item.client_id = payload.client_id
    if "title" in changes and payload.title is not None:
        item.title = payload.title.strip()
    if "description" in changes:
        item.description = payload.description.strip() if payload.description else None
    if "status" in changes and payload.status is not None:
        item.status = payload.status.value
        item.completed_at = (
            datetime.now(UTC) if payload.status is WorkOrderStatus.COMPLETED else None
        )
    if "priority" in changes and payload.priority is not None:
        item.priority = payload.priority.value
    if "assignee_id" in changes:
        item.assignee_id = payload.assignee_id
    if "scheduled_for" in changes:
        item.scheduled_for = payload.scheduled_for

    db.add(item)
    db.commit()
    return get_work_order(db, item.id) or item


def add_note(
    db: Session,
    item: WorkOrder,
    *,
    author_id: str,
    content: str,
) -> WorkOrderNote:
    note = WorkOrderNote(
        work_order_id=item.id,
        author_id=author_id,
        content=content.strip(),
    )
    db.add(note)
    db.commit()
    statement = (
        select(WorkOrderNote)
        .where(WorkOrderNote.id == note.id)
        .options(joinedload(WorkOrderNote.author))
    )
    return db.scalar(statement) or note
