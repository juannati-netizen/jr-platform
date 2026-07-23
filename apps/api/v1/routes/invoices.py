from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import get_current_user, require_roles
from apps.db.session import get_db
from apps.models.finance import InvoiceStatus
from apps.models.user import User, UserRole
from apps.repositories.clients import get_client
from apps.repositories.finance import (
    PaymentExceedsPendingError,
    add_payment,
    create_invoice,
    get_invoice,
    list_invoices,
    update_invoice,
)
from apps.repositories.work_orders import get_work_order
from apps.schemas.finance import (
    InvoiceCreate,
    InvoiceRead,
    InvoiceUpdate,
    PaymentCreate,
)

router = APIRouter()


def validate_invoice_references(db: Session, client_id: str, work_order_id: str | None) -> None:
    client = get_client(db, client_id)
    if client is None or not client.is_active:
        raise HTTPException(status_code=422, detail="El cliente indicado no está disponible")
    if work_order_id is not None:
        work_order = get_work_order(db, work_order_id)
        if work_order is None or work_order.client_id != client_id:
            raise HTTPException(
                status_code=422,
                detail="El trabajo indicado no pertenece al cliente",
            )


@router.get("", response_model=list[InvoiceRead])
def read_invoices(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    invoice_status: Annotated[InvoiceStatus | None, Query(alias="status")] = None,
    client_id: str | None = None,
) -> list[InvoiceRead]:
    return [
        InvoiceRead.from_entity(item)
        for item in list_invoices(db, status=invoice_status, client_id=client_id)
    ]


@router.post("", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
def add_invoice(
    payload: InvoiceCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> InvoiceRead:
    validate_invoice_references(db, payload.client_id, payload.work_order_id)
    return InvoiceRead.from_entity(create_invoice(db, payload, created_by_id=current_user.id))


@router.get("/{invoice_id}", response_model=InvoiceRead)
def read_invoice(
    invoice_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> InvoiceRead:
    invoice = get_invoice(db, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return InvoiceRead.from_entity(invoice)


@router.patch("/{invoice_id}", response_model=InvoiceRead)
def change_invoice(
    invoice_id: str,
    payload: InvoiceUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> InvoiceRead:
    invoice = get_invoice(db, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return InvoiceRead.from_entity(update_invoice(db, invoice, payload))


@router.post("/{invoice_id}/payments", response_model=InvoiceRead)
def record_payment(
    invoice_id: str,
    payload: PaymentCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> InvoiceRead:
    invoice = get_invoice(db, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    if invoice.status == InvoiceStatus.CANCELLED.value:
        raise HTTPException(status_code=409, detail="No se puede cobrar una factura cancelada")
    try:
        updated = add_payment(db, invoice, payload, recorded_by_id=current_user.id)
    except PaymentExceedsPendingError as exc:
        raise HTTPException(
            status_code=422,
            detail="El pago supera el importe pendiente",
        ) from exc
    return InvoiceRead.from_entity(updated)
