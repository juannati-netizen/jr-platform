from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import get_current_user, require_roles
from apps.db.session import get_db
from apps.models.finance import QuoteStatus
from apps.models.user import User, UserRole
from apps.repositories.clients import get_client
from apps.repositories.finance import (
    QuoteAlreadyInvoicedError,
    QuoteNotAcceptedError,
    convert_quote_to_invoice,
    create_quote,
    get_quote,
    list_quotes,
    update_quote,
)
from apps.repositories.work_orders import get_work_order
from apps.schemas.finance import InvoiceRead, QuoteCreate, QuoteRead, QuoteUpdate

router = APIRouter()


def validate_quote_references(db: Session, client_id: str, work_order_id: str | None) -> None:
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


@router.get("", response_model=list[QuoteRead])
def read_quotes(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    quote_status: Annotated[QuoteStatus | None, Query(alias="status")] = None,
    client_id: str | None = None,
) -> list[QuoteRead]:
    return [
        QuoteRead.from_entity(item)
        for item in list_quotes(db, status=quote_status, client_id=client_id)
    ]


@router.post("", response_model=QuoteRead, status_code=status.HTTP_201_CREATED)
def add_quote(
    payload: QuoteCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> QuoteRead:
    validate_quote_references(db, payload.client_id, payload.work_order_id)
    return QuoteRead.from_entity(create_quote(db, payload, created_by_id=current_user.id))


@router.get("/{quote_id}", response_model=QuoteRead)
def read_quote(
    quote_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> QuoteRead:
    quote = get_quote(db, quote_id)
    if quote is None:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    return QuoteRead.from_entity(quote)


@router.patch("/{quote_id}", response_model=QuoteRead)
def change_quote(
    quote_id: str,
    payload: QuoteUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> QuoteRead:
    quote = get_quote(db, quote_id)
    if quote is None:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    if quote.invoice is not None and payload.items is not None:
        raise HTTPException(status_code=409, detail="El presupuesto ya fue facturado")
    return QuoteRead.from_entity(update_quote(db, quote, payload))


@router.post("/{quote_id}/convert-to-invoice", response_model=InvoiceRead)
def convert_quote(
    quote_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    due_date: date | None = None,
) -> InvoiceRead:
    quote = get_quote(db, quote_id)
    if quote is None:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    try:
        invoice = convert_quote_to_invoice(
            db,
            quote,
            created_by_id=current_user.id,
            due_date=due_date,
        )
    except QuoteAlreadyInvoicedError as exc:
        raise HTTPException(status_code=409, detail="El presupuesto ya fue facturado") from exc
    except QuoteNotAcceptedError as exc:
        raise HTTPException(
            status_code=409,
            detail="Solo se pueden facturar presupuestos aceptados",
        ) from exc
    return InvoiceRead.from_entity(invoice)
