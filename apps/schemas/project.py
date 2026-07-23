from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from apps.models.crm import Project, ProjectDocument, ProjectStatus
from apps.schemas.client import ClientReference
from apps.schemas.finance import InvoiceRead, QuoteRead
from apps.schemas.inventory import StockMovementRead
from apps.schemas.procurement import ExpenseRead
from apps.schemas.work_order import UserReference, WorkOrderRead


class ProjectCreate(BaseModel):
    name: str = Field(min_length=3, max_length=220)
    client_id: str
    opportunity_id: str | None = None
    work_order_id: str | None = None
    manager_id: str | None = None
    status: ProjectStatus = ProjectStatus.PLANNED
    location: str | None = Field(default=None, max_length=300)
    description: str | None = Field(default=None, max_length=8000)
    planned_start: date | None = None
    planned_end: date | None = None
    budget: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    notes: str | None = Field(default=None, max_length=5000)

    @model_validator(mode="after")
    def validate_dates(self) -> "ProjectCreate":
        if (
            self.planned_start is not None
            and self.planned_end is not None
            and self.planned_end < self.planned_start
        ):
            raise ValueError("La fecha final no puede ser anterior al inicio")
        return self


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=220)
    client_id: str | None = None
    opportunity_id: str | None = None
    work_order_id: str | None = None
    manager_id: str | None = None
    status: ProjectStatus | None = None
    location: str | None = Field(default=None, max_length=300)
    description: str | None = Field(default=None, max_length=8000)
    planned_start: date | None = None
    planned_end: date | None = None
    actual_end: date | None = None
    budget: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    notes: str | None = Field(default=None, max_length=5000)


class ProjectDocumentRead(BaseModel):
    id: str
    filename: str
    content_type: str
    size_bytes: int
    category: str
    notes: str | None
    uploaded_by: UserReference
    created_at: datetime

    @classmethod
    def from_entity(cls, document: ProjectDocument) -> "ProjectDocumentRead":
        return cls(
            id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            size_bytes=document.size_bytes,
            category=document.category,
            notes=document.notes,
            uploaded_by=UserReference(
                id=document.uploaded_by.id,
                full_name=document.uploaded_by.full_name,
                email=document.uploaded_by.email,
            ),
            created_at=document.created_at,
        )


class ProjectRead(BaseModel):
    id: str
    code: str
    name: str
    client: ClientReference
    opportunity_id: str | None
    work_order_id: str | None
    manager: UserReference | None
    created_by: UserReference
    status: ProjectStatus
    location: str | None
    description: str | None
    planned_start: date | None
    planned_end: date | None
    actual_end: date | None
    budget: Decimal
    notes: str | None
    documents_count: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, project: Project) -> "ProjectRead":
        manager = None
        if project.manager is not None:
            manager = UserReference(
                id=project.manager.id,
                full_name=project.manager.full_name,
                email=project.manager.email,
            )
        return cls(
            id=project.id,
            code=project.code,
            name=project.name,
            client=ClientReference.model_validate(project.client),
            opportunity_id=project.opportunity_id,
            work_order_id=project.work_order_id,
            manager=manager,
            created_by=UserReference(
                id=project.created_by.id,
                full_name=project.created_by.full_name,
                email=project.created_by.email,
            ),
            status=ProjectStatus(project.status),
            location=project.location,
            description=project.description,
            planned_start=project.planned_start,
            planned_end=project.planned_end,
            actual_end=project.actual_end,
            budget=project.budget,
            notes=project.notes,
            documents_count=len(project.documents),
            created_at=project.created_at,
            updated_at=project.updated_at,
        )


class ProjectFinancialSummary(BaseModel):
    quoted_total: Decimal
    invoiced_total: Decimal
    collected_total: Decimal
    expenses_total: Decimal
    material_costs: Decimal
    gross_margin: Decimal


class ProjectFileRead(BaseModel):
    project: ProjectRead
    work_order: WorkOrderRead | None
    quotes: list[QuoteRead]
    invoices: list[InvoiceRead]
    expenses: list[ExpenseRead]
    stock_movements: list[StockMovementRead]
    documents: list[ProjectDocumentRead]
    financial: ProjectFinancialSummary
