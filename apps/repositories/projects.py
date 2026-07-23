from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql import Select

from apps.models.crm import Project, ProjectDocument, ProjectStatus
from apps.models.finance import Invoice, InvoiceStatus, Quote
from apps.models.inventory import StockMovement
from apps.models.procurement import Expense, ExpenseStatus
from apps.schemas.project import ProjectCreate, ProjectUpdate


class ProjectWorkOrderConflictError(Exception):
    pass


def project_statement() -> Select[tuple[Project]]:
    return select(Project).options(
        selectinload(Project.client),
        selectinload(Project.manager),
        selectinload(Project.created_by),
        selectinload(Project.opportunity),
        selectinload(Project.work_order),
        selectinload(Project.documents).selectinload(ProjectDocument.uploaded_by),
    )


def next_project_code(db: Session) -> str:
    year = date.today().year
    count = (
        db.scalar(
            select(func.count()).select_from(Project).where(Project.code.like(f"OBR-{year}-%"))
        )
        or 0
    )
    return f"OBR-{year}-{count + 1:04d}"


def list_projects(
    db: Session,
    *,
    status: ProjectStatus | None = None,
    client_id: str | None = None,
) -> list[Project]:
    statement = project_statement()
    if status is not None:
        statement = statement.where(Project.status == status.value)
    if client_id is not None:
        statement = statement.where(Project.client_id == client_id)
    statement = statement.order_by(Project.updated_at.desc())
    return list(db.scalars(statement).unique().all())


def get_project(db: Session, project_id: str) -> Project | None:
    return db.scalar(project_statement().where(Project.id == project_id))


def create_project(
    db: Session,
    payload: ProjectCreate,
    *,
    created_by_id: str,
) -> Project:
    if payload.work_order_id is not None:
        existing = db.scalar(select(Project).where(Project.work_order_id == payload.work_order_id))
        if existing is not None:
            raise ProjectWorkOrderConflictError
    project = Project(
        code=next_project_code(db),
        name=payload.name.strip(),
        client_id=payload.client_id,
        opportunity_id=payload.opportunity_id,
        work_order_id=payload.work_order_id,
        manager_id=payload.manager_id,
        created_by_id=created_by_id,
        status=payload.status.value,
        location=payload.location.strip() if payload.location else None,
        description=payload.description.strip() if payload.description else None,
        planned_start=payload.planned_start,
        planned_end=payload.planned_end,
        budget=payload.budget,
        notes=payload.notes.strip() if payload.notes else None,
    )
    db.add(project)
    db.commit()
    return get_project(db, project.id) or project


def update_project(db: Session, project: Project, payload: ProjectUpdate) -> Project:
    changes = payload.model_dump(exclude_unset=True)
    if "work_order_id" in changes and payload.work_order_id is not None:
        existing = db.scalar(
            select(Project).where(
                Project.work_order_id == payload.work_order_id,
                Project.id != project.id,
            )
        )
        if existing is not None:
            raise ProjectWorkOrderConflictError
    if "name" in changes and payload.name is not None:
        project.name = payload.name.strip()
    if "client_id" in changes and payload.client_id is not None:
        project.client_id = payload.client_id
    if "opportunity_id" in changes:
        project.opportunity_id = payload.opportunity_id
    if "work_order_id" in changes:
        project.work_order_id = payload.work_order_id
    if "manager_id" in changes:
        project.manager_id = payload.manager_id
    if "status" in changes and payload.status is not None:
        project.status = payload.status.value
    if "location" in changes:
        project.location = payload.location.strip() if payload.location else None
    if "description" in changes:
        project.description = payload.description.strip() if payload.description else None
    if "planned_start" in changes:
        project.planned_start = payload.planned_start
    if "planned_end" in changes:
        project.planned_end = payload.planned_end
    if "actual_end" in changes:
        project.actual_end = payload.actual_end
    if "budget" in changes and payload.budget is not None:
        project.budget = payload.budget
    if "notes" in changes:
        project.notes = payload.notes.strip() if payload.notes else None
    db.commit()
    return get_project(db, project.id) or project


def add_project_document(
    db: Session,
    project: Project,
    *,
    uploaded_by_id: str,
    filename: str,
    content_type: str,
    category: str,
    notes: str | None,
    content: bytes,
) -> ProjectDocument:
    document = ProjectDocument(
        project_id=project.id,
        uploaded_by_id=uploaded_by_id,
        filename=filename,
        content_type=content_type,
        size_bytes=len(content),
        category=category.strip() or "General",
        notes=notes.strip() if notes else None,
        content=content,
    )
    db.add(document)
    db.commit()
    return get_project_document(db, document.id) or document


def get_project_document(db: Session, document_id: str) -> ProjectDocument | None:
    return db.scalar(
        select(ProjectDocument)
        .options(selectinload(ProjectDocument.uploaded_by))
        .where(ProjectDocument.id == document_id)
    )


def delete_project_document(db: Session, document: ProjectDocument) -> None:
    db.delete(document)
    db.commit()


def project_financial_values(
    db: Session,
    work_order_id: str | None,
) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]:
    if work_order_id is None:
        zero = Decimal("0.00")
        return zero, zero, zero, zero, zero, zero
    quoted = db.scalar(
        select(func.sum(Quote.total)).where(Quote.work_order_id == work_order_id)
    ) or Decimal("0.00")
    invoiced = db.scalar(
        select(func.sum(Invoice.total)).where(
            Invoice.work_order_id == work_order_id,
            Invoice.status != InvoiceStatus.CANCELLED.value,
        )
    ) or Decimal("0.00")
    collected = db.scalar(
        select(func.sum(Invoice.paid_total)).where(
            Invoice.work_order_id == work_order_id,
            Invoice.status != InvoiceStatus.CANCELLED.value,
        )
    ) or Decimal("0.00")
    expenses = db.scalar(
        select(func.sum(Expense.total)).where(
            Expense.work_order_id == work_order_id,
            Expense.status != ExpenseStatus.CANCELLED.value,
        )
    ) or Decimal("0.00")
    material_costs = db.scalar(
        select(func.sum(StockMovement.quantity * StockMovement.unit_cost)).where(
            StockMovement.work_order_id == work_order_id,
            StockMovement.movement_type == "assignment",
        )
    ) or Decimal("0.00")
    return (
        quoted,
        invoiced,
        collected,
        expenses,
        material_costs,
        invoiced - expenses - material_costs,
    )
