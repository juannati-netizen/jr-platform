from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import require_roles
from apps.db.session import get_db
from apps.models.procurement import ExpenseCategory, ExpenseStatus
from apps.models.user import User, UserRole
from apps.repositories.procurement import (
    create_expense,
    get_expense,
    get_supplier,
    list_expenses,
    update_expense,
)
from apps.repositories.work_orders import get_work_order
from apps.schemas.procurement import ExpenseCreate, ExpenseRead, ExpenseUpdate

router = APIRouter()


def validate_expense_references(
    db: Session,
    *,
    supplier_id: str | None,
    work_order_id: str | None,
) -> None:
    if supplier_id is not None:
        supplier = get_supplier(db, supplier_id)
        if supplier is None or not supplier.is_active:
            raise HTTPException(status_code=422, detail="El proveedor indicado no está disponible")
    if work_order_id is not None and get_work_order(db, work_order_id) is None:
        raise HTTPException(status_code=422, detail="El trabajo indicado no existe")


@router.get("", response_model=list[ExpenseRead])
def read_expenses(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    supplier_id: str | None = None,
    work_order_id: str | None = None,
    category: ExpenseCategory | None = None,
    expense_status: Annotated[ExpenseStatus | None, Query(alias="status")] = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[ExpenseRead]:
    return [
        ExpenseRead.from_entity(item)
        for item in list_expenses(
            db,
            supplier_id=supplier_id,
            work_order_id=work_order_id,
            category=category,
            status=expense_status,
            date_from=date_from,
            date_to=date_to,
        )
    ]


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def add_expense(
    payload: ExpenseCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> ExpenseRead:
    validate_expense_references(
        db,
        supplier_id=payload.supplier_id,
        work_order_id=payload.work_order_id,
    )
    expense = create_expense(db, payload, created_by_id=current_user.id)
    return ExpenseRead.from_entity(expense)


@router.get("/{expense_id}", response_model=ExpenseRead)
def read_expense(
    expense_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> ExpenseRead:
    expense = get_expense(db, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    return ExpenseRead.from_entity(expense)


@router.patch("/{expense_id}", response_model=ExpenseRead)
def change_expense(
    expense_id: str,
    payload: ExpenseUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> ExpenseRead:
    expense = get_expense(db, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    changes = payload.model_dump(exclude_unset=True)
    validate_expense_references(
        db,
        supplier_id=payload.supplier_id if "supplier_id" in changes else None,
        work_order_id=payload.work_order_id if "work_order_id" in changes else None,
    )
    return ExpenseRead.from_entity(update_expense(db, expense, payload))
