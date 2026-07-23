from __future__ import annotations

import json
from collections import defaultdict
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from apps.models.finance import Invoice, InvoiceStatus
from apps.models.procurement import Expense, ExpenseStatus
from apps.models.tax import (
    TaxAdjustment,
    TaxAdjustmentDirection,
    TaxConfiguration,
    TaxPeriod,
    TaxPeriodStatus,
)
from apps.schemas.tax import (
    TaxAdjustmentCreate,
    TaxAdjustmentRead,
    TaxConfigurationUpdate,
    TaxMonthSummary,
    TaxRateBreakdown,
)

MONTH_NAMES = (
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
)
ZERO = Decimal("0.00")


class TaxPeriodClosedError(Exception):
    pass


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))


def _period_bounds(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end


def get_tax_configuration(db: Session) -> TaxConfiguration:
    item = db.scalar(select(TaxConfiguration).order_by(TaxConfiguration.created_at).limit(1))
    if item is None:
        item = TaxConfiguration()
        db.add(item)
        db.commit()
        db.refresh(item)
    return item


def update_tax_configuration(
    db: Session,
    item: TaxConfiguration,
    payload: TaxConfigurationUpdate,
) -> TaxConfiguration:
    for field, value in payload.model_dump().items():
        setattr(item, field, value)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_tax_period(db: Session, year: int, month: int) -> TaxPeriod | None:
    statement = (
        select(TaxPeriod)
        .where(TaxPeriod.year == year, TaxPeriod.month == month)
        .options(joinedload(TaxPeriod.closed_by))
    )
    return db.scalar(statement)


def list_adjustments(db: Session, year: int, month: int) -> list[TaxAdjustment]:
    statement = (
        select(TaxAdjustment)
        .where(TaxAdjustment.year == year, TaxAdjustment.month == month)
        .order_by(TaxAdjustment.created_at)
    )
    return list(db.scalars(statement).all())


def create_adjustment(
    db: Session,
    payload: TaxAdjustmentCreate,
    *,
    created_by_id: str,
) -> TaxAdjustment:
    period = get_tax_period(db, payload.year, payload.month)
    if period is not None and period.status == TaxPeriodStatus.CLOSED.value:
        raise TaxPeriodClosedError
    item = TaxAdjustment(
        year=payload.year,
        month=payload.month,
        direction=payload.direction.value,
        amount=payload.amount,
        description=payload.description,
        created_by_id=created_by_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def _live_month_summary(db: Session, year: int, month: int) -> TaxMonthSummary:
    start, end = _period_bounds(year, month)
    invoices = list(
        db.scalars(
            select(Invoice)
            .where(
                Invoice.issue_date >= start,
                Invoice.issue_date < end,
                Invoice.status != InvoiceStatus.CANCELLED.value,
            )
            .options(selectinload(Invoice.items))
        )
        .unique()
        .all()
    )
    expenses = list(
        db.scalars(
            select(Expense).where(
                Expense.expense_date >= start,
                Expense.expense_date < end,
                Expense.status != ExpenseStatus.CANCELLED.value,
            )
        ).all()
    )

    output_by_rate: dict[Decimal, list[Decimal]] = defaultdict(lambda: [ZERO, ZERO])
    for invoice in invoices:
        for item in invoice.items:
            rate = Decimal(item.tax_rate)
            output_by_rate[rate][0] += Decimal(item.line_subtotal)
            output_by_rate[rate][1] += Decimal(item.line_tax)

    input_by_rate: dict[Decimal, list[Decimal]] = defaultdict(lambda: [ZERO, ZERO])
    for expense in expenses:
        rate = Decimal(expense.tax_rate)
        input_by_rate[rate][0] += Decimal(expense.subtotal)
        input_by_rate[rate][1] += Decimal(expense.tax_total)

    adjustments = list_adjustments(db, year, month)
    output_adjustments = sum(
        (
            Decimal(item.amount)
            for item in adjustments
            if item.direction == TaxAdjustmentDirection.OUTPUT.value
        ),
        ZERO,
    )
    input_adjustments = sum(
        (
            Decimal(item.amount)
            for item in adjustments
            if item.direction == TaxAdjustmentDirection.INPUT.value
        ),
        ZERO,
    )
    output_base = sum((values[0] for values in output_by_rate.values()), ZERO)
    output_tax = sum((values[1] for values in output_by_rate.values()), ZERO)
    input_base = sum((values[0] for values in input_by_rate.values()), ZERO)
    input_tax = sum((values[1] for values in input_by_rate.values()), ZERO)
    result = output_tax + output_adjustments - input_tax - input_adjustments
    period = get_tax_period(db, year, month)

    return TaxMonthSummary(
        year=year,
        month=month,
        month_label=MONTH_NAMES[month - 1],
        status=TaxPeriodStatus.OPEN,
        output_base=_money(output_base),
        output_tax=_money(output_tax),
        input_base=_money(input_base),
        input_tax=_money(input_tax),
        output_adjustments=_money(output_adjustments),
        input_adjustments=_money(input_adjustments),
        result=_money(result),
        result_type="to_pay" if result > 0 else "to_compensate" if result < 0 else "zero",
        output_breakdown=[
            TaxRateBreakdown(
                tax_rate=rate,
                taxable_base=_money(values[0]),
                tax_amount=_money(values[1]),
            )
            for rate, values in sorted(output_by_rate.items())
        ],
        input_breakdown=[
            TaxRateBreakdown(
                tax_rate=rate,
                taxable_base=_money(values[0]),
                tax_amount=_money(values[1]),
            )
            for rate, values in sorted(input_by_rate.items())
        ],
        adjustments=[TaxAdjustmentRead.model_validate(item) for item in adjustments],
        closed_at=period.closed_at if period else None,
        legal_notice=(
            "Estimación interna basada en facturas y gastos registrados. Debe revisarse con la "
            "documentación contable antes de presentar el modelo 420."
        ),
    )


def get_month_summary(db: Session, year: int, month: int) -> TaxMonthSummary:
    period = get_tax_period(db, year, month)
    if (
        period is not None
        and period.status == TaxPeriodStatus.CLOSED.value
        and period.snapshot_json
    ):
        return TaxMonthSummary.model_validate(json.loads(period.snapshot_json))
    return _live_month_summary(db, year, month)


def list_year_summaries(db: Session, year: int) -> list[TaxMonthSummary]:
    return [get_month_summary(db, year, month) for month in range(1, 13)]


def close_month(
    db: Session,
    year: int,
    month: int,
    *,
    actor_id: str,
    notes: str | None,
) -> TaxMonthSummary:
    summary = _live_month_summary(db, year, month)
    period = get_tax_period(db, year, month)
    if period is None:
        period = TaxPeriod(year=year, month=month)
    summary.status = TaxPeriodStatus.CLOSED
    summary.closed_at = datetime.now(UTC)
    period.status = TaxPeriodStatus.CLOSED.value
    period.snapshot_json = summary.model_dump_json()
    period.notes = notes
    period.closed_at = summary.closed_at
    period.closed_by_id = actor_id
    db.add(period)
    db.commit()
    return summary


def reopen_month(db: Session, year: int, month: int) -> TaxMonthSummary:
    period = get_tax_period(db, year, month)
    if period is not None:
        period.status = TaxPeriodStatus.OPEN.value
        period.snapshot_json = None
        period.closed_at = None
        period.closed_by_id = None
        db.add(period)
        db.commit()
    return _live_month_summary(db, year, month)
