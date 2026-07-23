from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql import Select

from apps.models.client import Client
from apps.models.finance import Invoice, InvoiceStatus
from apps.models.inventory import StockMovement, StockMovementType
from apps.models.procurement import Expense, ExpenseCategory, ExpenseStatus, Supplier
from apps.models.work_order import WorkOrder
from apps.schemas.procurement import (
    ClientProfitability,
    ExpenseCreate,
    ExpenseUpdate,
    ProfitabilitySummary,
    SupplierCreate,
    SupplierUpdate,
    WorkOrderProfitability,
)


TWOPLACES = Decimal("0.01")


class DuplicateSupplierTaxIdError(Exception):
    pass


def money(value: Decimal) -> Decimal:
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def calculate_expense_values(subtotal: Decimal, tax_rate: Decimal) -> tuple[Decimal, Decimal]:
    tax_total = money(subtotal * tax_rate / Decimal("100"))
    return tax_total, money(subtotal + tax_total)


def get_supplier(db: Session, supplier_id: str) -> Supplier | None:
    return db.get(Supplier, supplier_id)


def list_suppliers(
    db: Session,
    *,
    search: str | None = None,
    active_only: bool = False,
) -> list[Supplier]:
    statement = select(Supplier)
    if active_only:
        statement = statement.where(Supplier.is_active.is_(True))
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Supplier.name.ilike(pattern),
                Supplier.tax_id.ilike(pattern),
                Supplier.email.ilike(pattern),
            )
        )
    return list(db.scalars(statement.order_by(Supplier.name)).all())


def create_supplier(db: Session, payload: SupplierCreate) -> Supplier:
    supplier = Supplier(
        name=payload.name,
        tax_id=payload.tax_id.strip().upper() if payload.tax_id else None,
        email=str(payload.email).lower() if payload.email else None,
        phone=payload.phone.strip() if payload.phone else None,
        address=payload.address.strip() if payload.address else None,
        notes=payload.notes.strip() if payload.notes else None,
    )
    db.add(supplier)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateSupplierTaxIdError from exc
    db.refresh(supplier)
    return supplier


def update_supplier(db: Session, supplier: Supplier, payload: SupplierUpdate) -> Supplier:
    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes and payload.name is not None:
        supplier.name = payload.name
    if "tax_id" in changes:
        supplier.tax_id = payload.tax_id.strip().upper() if payload.tax_id else None
    if "email" in changes:
        supplier.email = str(payload.email).lower() if payload.email else None
    if "phone" in changes:
        supplier.phone = payload.phone.strip() if payload.phone else None
    if "address" in changes:
        supplier.address = payload.address.strip() if payload.address else None
    if "notes" in changes:
        supplier.notes = payload.notes.strip() if payload.notes else None
    if "is_active" in changes and payload.is_active is not None:
        supplier.is_active = payload.is_active

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateSupplierTaxIdError from exc
    db.refresh(supplier)
    return supplier


def expense_statement() -> Select[tuple[Expense]]:
    return select(Expense).options(
        selectinload(Expense.supplier),
        selectinload(Expense.work_order).selectinload(WorkOrder.client),
        selectinload(Expense.created_by),
    )


def get_expense(db: Session, expense_id: str) -> Expense | None:
    return db.scalar(expense_statement().where(Expense.id == expense_id))


def list_expenses(
    db: Session,
    *,
    supplier_id: str | None = None,
    work_order_id: str | None = None,
    category: ExpenseCategory | None = None,
    status: ExpenseStatus | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[Expense]:
    statement = expense_statement()
    if supplier_id is not None:
        statement = statement.where(Expense.supplier_id == supplier_id)
    if work_order_id is not None:
        statement = statement.where(Expense.work_order_id == work_order_id)
    if category is not None:
        statement = statement.where(Expense.category == category.value)
    if status is not None:
        statement = statement.where(Expense.status == status.value)
    if date_from is not None:
        statement = statement.where(Expense.expense_date >= date_from)
    if date_to is not None:
        statement = statement.where(Expense.expense_date <= date_to)
    statement = statement.order_by(Expense.expense_date.desc(), Expense.created_at.desc())
    return list(db.scalars(statement).unique().all())


def create_expense(db: Session, payload: ExpenseCreate, *, created_by_id: str) -> Expense:
    tax_total, total = calculate_expense_values(payload.subtotal, payload.tax_rate)
    expense = Expense(
        supplier_id=payload.supplier_id,
        work_order_id=payload.work_order_id,
        created_by_id=created_by_id,
        description=payload.description,
        category=payload.category.value,
        status=payload.status.value,
        expense_date=payload.expense_date,
        subtotal=money(payload.subtotal),
        tax_rate=money(payload.tax_rate),
        tax_total=tax_total,
        total=total,
        reference=payload.reference.strip() if payload.reference else None,
        notes=payload.notes.strip() if payload.notes else None,
    )
    db.add(expense)
    db.commit()
    return get_expense(db, expense.id) or expense


def update_expense(db: Session, expense: Expense, payload: ExpenseUpdate) -> Expense:
    changes = payload.model_dump(exclude_unset=True)
    if "supplier_id" in changes:
        expense.supplier_id = payload.supplier_id
    if "work_order_id" in changes:
        expense.work_order_id = payload.work_order_id
    if "description" in changes and payload.description is not None:
        expense.description = payload.description
    if "category" in changes and payload.category is not None:
        expense.category = payload.category.value
    if "status" in changes and payload.status is not None:
        expense.status = payload.status.value
    if "expense_date" in changes and payload.expense_date is not None:
        expense.expense_date = payload.expense_date
    if "subtotal" in changes and payload.subtotal is not None:
        expense.subtotal = money(payload.subtotal)
    if "tax_rate" in changes and payload.tax_rate is not None:
        expense.tax_rate = money(payload.tax_rate)
    if "reference" in changes:
        expense.reference = payload.reference.strip() if payload.reference else None
    if "notes" in changes:
        expense.notes = payload.notes.strip() if payload.notes else None

    expense.tax_total, expense.total = calculate_expense_values(
        expense.subtotal,
        expense.tax_rate,
    )
    db.commit()
    return get_expense(db, expense.id) or expense


def get_profitability_summary(db: Session) -> ProfitabilitySummary:
    invoices = list(
        db.scalars(
            select(Invoice)
            .where(Invoice.status != InvoiceStatus.CANCELLED.value)
            .options(selectinload(Invoice.client), selectinload(Invoice.work_order))
        ).all()
    )
    expenses = list(
        db.scalars(
            select(Expense)
            .where(Expense.status != ExpenseStatus.CANCELLED.value)
            .options(selectinload(Expense.work_order).selectinload(WorkOrder.client))
        ).all()
    )
    material_movements = list(
        db.scalars(
            select(StockMovement)
            .where(
                StockMovement.movement_type == StockMovementType.ASSIGNMENT.value,
                StockMovement.work_order_id.is_not(None),
            )
            .options(selectinload(StockMovement.work_order).selectinload(WorkOrder.client))
        ).all()
    )
    work_orders = list(
        db.scalars(select(WorkOrder).options(selectinload(WorkOrder.client))).all()
    )
    clients = list(db.scalars(select(Client).order_by(Client.name)).all())

    work_order_values: dict[str, dict[str, Decimal]] = {
        item.id: {
            "invoiced": Decimal("0.00"),
            "collected": Decimal("0.00"),
            "expenses": Decimal("0.00"),
        }
        for item in work_orders
    }
    client_values: dict[str, dict[str, Decimal]] = {
        item.id: {
            "invoiced": Decimal("0.00"),
            "collected": Decimal("0.00"),
            "expenses": Decimal("0.00"),
        }
        for item in clients
    }

    invoiced_revenue = Decimal("0.00")
    collected_revenue = Decimal("0.00")
    for invoice in invoices:
        invoiced_revenue += invoice.total
        collected_revenue += invoice.paid_total
        client_metrics = client_values.setdefault(
            invoice.client_id,
            {
                "invoiced": Decimal("0.00"),
                "collected": Decimal("0.00"),
                "expenses": Decimal("0.00"),
            },
        )
        client_metrics["invoiced"] += invoice.total
        client_metrics["collected"] += invoice.paid_total
        if invoice.work_order_id is not None:
            metrics = work_order_values.setdefault(
                invoice.work_order_id,
                {
                "invoiced": Decimal("0.00"),
                "collected": Decimal("0.00"),
                "expenses": Decimal("0.00"),
            },
            )
            metrics["invoiced"] += invoice.total
            metrics["collected"] += invoice.paid_total

    expenses_total = Decimal("0.00")
    material_costs = Decimal("0.00")
    for expense in expenses:
        expenses_total += expense.total
        if expense.category == ExpenseCategory.MATERIALS.value:
            material_costs += expense.total
        if expense.work_order_id is not None and expense.work_order is not None:
            metrics = work_order_values.setdefault(
                expense.work_order_id,
                {
                "invoiced": Decimal("0.00"),
                "collected": Decimal("0.00"),
                "expenses": Decimal("0.00"),
            },
            )
            metrics["expenses"] += expense.total
            client_metrics = client_values.setdefault(
                expense.work_order.client_id,
                {
                "invoiced": Decimal("0.00"),
                "collected": Decimal("0.00"),
                "expenses": Decimal("0.00"),
            },
            )
            client_metrics["expenses"] += expense.total

    for movement in material_movements:
        movement_cost = abs(movement.quantity) * movement.unit_cost
        expenses_total += movement_cost
        material_costs += movement_cost
        if movement.work_order_id is not None and movement.work_order is not None:
            metrics = work_order_values.setdefault(
                movement.work_order_id,
                {
                    "invoiced": Decimal("0.00"),
                    "collected": Decimal("0.00"),
                    "expenses": Decimal("0.00"),
                },
            )
            metrics["expenses"] += movement_cost
            client_metrics = client_values.setdefault(
                movement.work_order.client_id,
                {
                    "invoiced": Decimal("0.00"),
                    "collected": Decimal("0.00"),
                    "expenses": Decimal("0.00"),
                },
            )
            client_metrics["expenses"] += movement_cost

    work_order_report = []
    for work_order in work_orders:
        values = work_order_values[work_order.id]
        work_order_report.append(
            WorkOrderProfitability(
                id=work_order.id,
                title=work_order.title,
                client_name=work_order.client.name,
                invoiced_revenue=money(values["invoiced"]),
                collected_revenue=money(values["collected"]),
                expenses_total=money(values["expenses"]),
                gross_margin=money(values["invoiced"] - values["expenses"]),
                realized_margin=money(values["collected"] - values["expenses"]),
            )
        )
    work_order_report.sort(key=lambda item: item.gross_margin, reverse=True)

    client_report = []
    for client in clients:
        values = client_values[client.id]
        client_report.append(
            ClientProfitability(
                id=client.id,
                name=client.name,
                invoiced_revenue=money(values["invoiced"]),
                collected_revenue=money(values["collected"]),
                expenses_total=money(values["expenses"]),
                gross_margin=money(values["invoiced"] - values["expenses"]),
                realized_margin=money(values["collected"] - values["expenses"]),
            )
        )
    client_report.sort(key=lambda item: item.gross_margin, reverse=True)

    gross_margin = money(invoiced_revenue - expenses_total)
    realized_margin = money(collected_revenue - expenses_total)
    gross_margin_percent = (
        money(gross_margin * Decimal("100") / invoiced_revenue)
        if invoiced_revenue > 0
        else Decimal("0.00")
    )

    return ProfitabilitySummary(
        invoiced_revenue=money(invoiced_revenue),
        collected_revenue=money(collected_revenue),
        expenses_total=money(expenses_total),
        material_costs=money(material_costs),
        gross_margin=gross_margin,
        realized_margin=realized_margin,
        gross_margin_percent=gross_margin_percent,
        work_orders=work_order_report,
        clients=client_report,
    )
