from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import get_current_user, require_roles
from apps.db.session import get_db
from apps.models.crm import ProjectStatus
from apps.models.user import User, UserRole
from apps.repositories.clients import get_client
from apps.repositories.crm import get_opportunity
from apps.repositories.finance import list_invoices, list_quotes
from apps.repositories.inventory import list_stock_movements
from apps.repositories.procurement import list_expenses
from apps.repositories.projects import (
    ProjectWorkOrderConflictError,
    add_project_document,
    create_project,
    delete_project_document,
    get_project,
    get_project_document,
    list_projects,
    project_financial_values,
    update_project,
)
from apps.repositories.users import get_user_by_id
from apps.repositories.work_orders import get_work_order
from apps.schemas.finance import InvoiceRead, QuoteRead
from apps.schemas.inventory import StockMovementRead
from apps.schemas.procurement import ExpenseRead
from apps.schemas.project import (
    ProjectCreate,
    ProjectDocumentRead,
    ProjectFileRead,
    ProjectFinancialSummary,
    ProjectRead,
    ProjectUpdate,
)
from apps.schemas.work_order import WorkOrderRead

router = APIRouter()
MAX_DOCUMENT_BYTES = 5 * 1024 * 1024


def validate_project_references(
    db: Session,
    *,
    client_id: str,
    opportunity_id: str | None,
    work_order_id: str | None,
    manager_id: str | None,
) -> None:
    client = get_client(db, client_id)
    if client is None or not client.is_active:
        raise HTTPException(status_code=422, detail="El cliente indicado no está disponible")
    if opportunity_id is not None:
        opportunity = get_opportunity(db, opportunity_id)
        if opportunity is None or (
            opportunity.client_id is not None and opportunity.client_id != client_id
        ):
            raise HTTPException(status_code=422, detail="La oportunidad no pertenece al cliente")
    if work_order_id is not None:
        work_order = get_work_order(db, work_order_id)
        if work_order is None or work_order.client_id != client_id:
            raise HTTPException(status_code=422, detail="El trabajo no pertenece al cliente")
    if manager_id is not None:
        manager = get_user_by_id(db, manager_id)
        if manager is None or not manager.is_active:
            raise HTTPException(status_code=422, detail="El responsable no está disponible")


@router.get("", response_model=list[ProjectRead])
def read_projects(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    project_status: ProjectStatus | None = None,
    client_id: str | None = None,
) -> list[ProjectRead]:
    return [
        ProjectRead.from_entity(item)
        for item in list_projects(db, status=project_status, client_id=client_id)
    ]


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def add_project(
    payload: ProjectCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectRead:
    validate_project_references(
        db,
        client_id=payload.client_id,
        opportunity_id=payload.opportunity_id,
        work_order_id=payload.work_order_id,
        manager_id=payload.manager_id,
    )
    try:
        project = create_project(db, payload, created_by_id=current_user.id)
    except ProjectWorkOrderConflictError as exc:
        raise HTTPException(status_code=409, detail="El trabajo ya pertenece a otra obra") from exc
    return ProjectRead.from_entity(project)


@router.get("/{project_id}", response_model=ProjectRead)
def read_project(
    project_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> ProjectRead:
    project = get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Obra no encontrada")
    return ProjectRead.from_entity(project)


@router.patch("/{project_id}", response_model=ProjectRead)
def change_project(
    project_id: str,
    payload: ProjectUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> ProjectRead:
    project = get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Obra no encontrada")
    changes = payload.model_dump(exclude_unset=True)
    client_id = (
        payload.client_id if "client_id" in changes and payload.client_id else project.client_id
    )
    validate_project_references(
        db,
        client_id=client_id,
        opportunity_id=(
            payload.opportunity_id if "opportunity_id" in changes else project.opportunity_id
        ),
        work_order_id=(
            payload.work_order_id if "work_order_id" in changes else project.work_order_id
        ),
        manager_id=payload.manager_id if "manager_id" in changes else project.manager_id,
    )
    try:
        updated = update_project(db, project, payload)
    except ProjectWorkOrderConflictError as exc:
        raise HTTPException(status_code=409, detail="El trabajo ya pertenece a otra obra") from exc
    return ProjectRead.from_entity(updated)


@router.get("/{project_id}/file", response_model=ProjectFileRead)
def read_project_file(
    project_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> ProjectFileRead:
    project = get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Obra no encontrada")
    work_order = get_work_order(db, project.work_order_id) if project.work_order_id else None
    quotes = list_quotes(db, client_id=project.client_id)
    invoices = list_invoices(db, client_id=project.client_id)
    expenses = (
        list_expenses(db, work_order_id=project.work_order_id) if project.work_order_id else []
    )
    movements = (
        list_stock_movements(db, work_order_id=project.work_order_id, limit=500)
        if project.work_order_id
        else []
    )
    if project.work_order_id is not None:
        quotes = [item for item in quotes if item.work_order_id == project.work_order_id]
        invoices = [item for item in invoices if item.work_order_id == project.work_order_id]
    else:
        quotes = []
        invoices = []
    quoted, invoiced, collected, expense_total, materials, gross = project_financial_values(
        db, project.work_order_id
    )
    return ProjectFileRead(
        project=ProjectRead.from_entity(project),
        work_order=WorkOrderRead.from_entity(work_order) if work_order else None,
        quotes=[QuoteRead.from_entity(item) for item in quotes],
        invoices=[InvoiceRead.from_entity(item) for item in invoices],
        expenses=[ExpenseRead.from_entity(item) for item in expenses],
        stock_movements=[StockMovementRead.from_entity(item) for item in movements],
        documents=[ProjectDocumentRead.from_entity(item) for item in project.documents],
        financial=ProjectFinancialSummary(
            quoted_total=quoted,
            invoiced_total=invoiced,
            collected_total=collected,
            expenses_total=expense_total,
            material_costs=materials,
            gross_margin=gross,
        ),
    )


@router.post(
    "/{project_id}/documents",
    response_model=ProjectDocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_project_document(
    project_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    file: Annotated[UploadFile, File()],
    category: Annotated[str, Form(max_length=80)] = "General",
    notes: Annotated[str | None, Form(max_length=2000)] = None,
) -> ProjectDocumentRead:
    project = get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Obra no encontrada")
    content = await file.read(MAX_DOCUMENT_BYTES + 1)
    if len(content) > MAX_DOCUMENT_BYTES:
        raise HTTPException(status_code=413, detail="El documento supera el límite de 5 MB")
    if not content:
        raise HTTPException(status_code=422, detail="El documento está vacío")
    document = add_project_document(
        db,
        project,
        uploaded_by_id=current_user.id,
        filename=file.filename or "documento",
        content_type=file.content_type or "application/octet-stream",
        category=category,
        notes=notes,
        content=content,
    )
    return ProjectDocumentRead.from_entity(document)


@router.get("/documents/{document_id}/download")
def download_project_document(
    document_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> Response:
    document = get_project_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    encoded_filename = quote(document.filename)
    return Response(
        content=document.content,
        media_type=document.content_type,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
    )


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project_document(
    document_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> Response:
    document = get_project_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    delete_project_document(db, document)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
