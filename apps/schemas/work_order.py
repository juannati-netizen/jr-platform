from datetime import datetime

from pydantic import BaseModel, Field

from apps.models.work_order import (
    WorkOrder,
    WorkOrderNote,
    WorkOrderPriority,
    WorkOrderStatus,
)
from apps.schemas.client import ClientReference


class UserReference(BaseModel):
    id: str
    full_name: str
    email: str


class WorkOrderCreate(BaseModel):
    client_id: str
    title: str = Field(min_length=3, max_length=180)
    description: str | None = Field(default=None, max_length=8000)
    status: WorkOrderStatus = WorkOrderStatus.DRAFT
    priority: WorkOrderPriority = WorkOrderPriority.NORMAL
    assignee_id: str | None = None
    scheduled_for: datetime | None = None


class WorkOrderUpdate(BaseModel):
    client_id: str | None = None
    title: str | None = Field(default=None, min_length=3, max_length=180)
    description: str | None = Field(default=None, max_length=8000)
    status: WorkOrderStatus | None = None
    priority: WorkOrderPriority | None = None
    assignee_id: str | None = None
    scheduled_for: datetime | None = None


class WorkOrderNoteCreate(BaseModel):
    content: str = Field(min_length=2, max_length=4000)


class WorkOrderNoteRead(BaseModel):
    id: str
    content: str
    created_at: datetime
    author: UserReference

    @classmethod
    def from_entity(cls, note: WorkOrderNote) -> "WorkOrderNoteRead":
        return cls(
            id=note.id,
            content=note.content,
            created_at=note.created_at,
            author=UserReference(
                id=note.author.id,
                full_name=note.author.full_name,
                email=note.author.email,
            ),
        )


class WorkOrderRead(BaseModel):
    id: str
    title: str
    description: str | None
    status: WorkOrderStatus
    priority: WorkOrderPriority
    scheduled_for: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    client: ClientReference
    assignee: UserReference | None
    created_by: UserReference
    notes_count: int

    @classmethod
    def from_entity(cls, item: WorkOrder) -> "WorkOrderRead":
        assignee = None
        if item.assignee is not None:
            assignee = UserReference(
                id=item.assignee.id,
                full_name=item.assignee.full_name,
                email=item.assignee.email,
            )

        return cls(
            id=item.id,
            title=item.title,
            description=item.description,
            status=WorkOrderStatus(item.status),
            priority=WorkOrderPriority(item.priority),
            scheduled_for=item.scheduled_for,
            completed_at=item.completed_at,
            created_at=item.created_at,
            updated_at=item.updated_at,
            client=ClientReference.model_validate(item.client),
            assignee=assignee,
            created_by=UserReference(
                id=item.created_by.id,
                full_name=item.created_by.full_name,
                email=item.created_by.email,
            ),
            notes_count=len(item.notes),
        )
