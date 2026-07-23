import csv
import io
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import require_roles
from apps.db.session import get_db
from apps.models.tax import TaxPeriodStatus
from apps.models.user import User, UserRole
from apps.repositories.settings import create_configuration_event
from apps.repositories.tax import (
    TaxPeriodClosedError,
    close_month,
    create_adjustment,
    get_month_summary,
    get_tax_configuration,
    list_year_summaries,
    reopen_month,
    update_tax_configuration,
)
from apps.schemas.tax import (
    TaxAdjustmentCreate,
    TaxAdjustmentRead,
    TaxConfigurationRead,
    TaxConfigurationUpdate,
    TaxMonthSummary,
    TaxPeriodAction,
    TaxQuarterSummary,
)

router = APIRouter()
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN))]
DbSession = Annotated[Session, Depends(get_db)]


def _result_type(result: Decimal) -> str:
    if result > 0:
        return "to_pay"
    if result < 0:
        return "to_compensate"
    return "zero"


def _quarter_months(quarter: int) -> range:
    first_month = (quarter - 1) * 3 + 1
    return range(first_month, first_month + 3)


def _filing_window(year: int, quarter: int) -> str:
    windows = {
        1: f"1–20 de abril de {year}",
        2: f"1–20 de julio de {year}",
        3: f"1–20 de octubre de {year}",
        4: f"Durante enero de {year + 1}",
    }
    return windows[quarter]


def build_quarter_summary(db: Session, year: int, quarter: int) -> TaxQuarterSummary:
    months = [get_month_summary(db, year, month) for month in _quarter_months(quarter)]
    output_base = sum((month.output_base for month in months), Decimal("0.00"))
    output_tax = sum((month.output_tax for month in months), Decimal("0.00"))
    input_base = sum((month.input_base for month in months), Decimal("0.00"))
    input_tax = sum((month.input_tax for month in months), Decimal("0.00"))
    output_adjustments = sum((month.output_adjustments for month in months), Decimal("0.00"))
    input_adjustments = sum((month.input_adjustments for month in months), Decimal("0.00"))
    result = output_tax + output_adjustments - input_tax - input_adjustments
    return TaxQuarterSummary(
        year=year,
        quarter=quarter,
        period_label=f"{quarter}.º trimestre de {year}",
        months=months,
        output_base=output_base,
        output_tax=output_tax,
        input_base=input_base,
        input_tax=input_tax,
        output_adjustments=output_adjustments,
        input_adjustments=input_adjustments,
        result=result,
        result_type=_result_type(result),
        model="420",
        filing_window=_filing_window(year, quarter),
        all_months_closed=all(month.status == TaxPeriodStatus.CLOSED for month in months),
        legal_notice=(
            "Borrador interno del modelo 420. No sustituye la autoliquidación oficial ni la "
            "revisión de un profesional tributario."
        ),
    )


@router.get("/configuration", response_model=TaxConfigurationRead)
def read_tax_configuration(db: DbSession, _: AdminUser) -> TaxConfigurationRead:
    return TaxConfigurationRead.model_validate(get_tax_configuration(db))


@router.put("/configuration", response_model=TaxConfigurationRead)
def save_tax_configuration(
    payload: TaxConfigurationUpdate,
    db: DbSession,
    current_user: AdminUser,
) -> TaxConfigurationRead:
    item = update_tax_configuration(db, get_tax_configuration(db), payload)
    create_configuration_event(
        db,
        category="tax",
        action="configuration_updated",
        summary=f"Fiscalidad configurada como {item.tax_system.upper()} modelo {item.filing_model}",
        actor_id=current_user.id,
    )
    return TaxConfigurationRead.model_validate(item)


@router.get("/months", response_model=list[TaxMonthSummary])
def read_tax_months(
    db: DbSession,
    _: AdminUser,
    year: Annotated[int, Query(ge=2000, le=2100)],
) -> list[TaxMonthSummary]:
    return list_year_summaries(db, year)


@router.get("/months/{year}/{month}", response_model=TaxMonthSummary)
def read_tax_month(
    year: int,
    month: int,
    db: DbSession,
    _: AdminUser,
) -> TaxMonthSummary:
    if not 2000 <= year <= 2100 or not 1 <= month <= 12:
        raise HTTPException(status_code=422, detail="Periodo fiscal no válido")
    return get_month_summary(db, year, month)


@router.post("/months/{year}/{month}/close", response_model=TaxMonthSummary)
def finish_tax_month(
    year: int,
    month: int,
    payload: TaxPeriodAction,
    db: DbSession,
    current_user: AdminUser,
) -> TaxMonthSummary:
    if not 2000 <= year <= 2100 or not 1 <= month <= 12:
        raise HTTPException(status_code=422, detail="Periodo fiscal no válido")
    summary = close_month(
        db,
        year,
        month,
        actor_id=current_user.id,
        notes=payload.notes,
    )
    create_configuration_event(
        db,
        category="tax",
        action="month_closed",
        summary=f"Periodo fiscal {month:02d}/{year} cerrado",
        actor_id=current_user.id,
    )
    return summary


@router.post("/months/{year}/{month}/open", response_model=TaxMonthSummary)
def reopen_tax_month(
    year: int,
    month: int,
    db: DbSession,
    current_user: AdminUser,
) -> TaxMonthSummary:
    if not 2000 <= year <= 2100 or not 1 <= month <= 12:
        raise HTTPException(status_code=422, detail="Periodo fiscal no válido")
    summary = reopen_month(db, year, month)
    create_configuration_event(
        db,
        category="tax",
        action="month_reopened",
        summary=f"Periodo fiscal {month:02d}/{year} reabierto",
        actor_id=current_user.id,
    )
    return summary


@router.post(
    "/adjustments",
    response_model=TaxAdjustmentRead,
    status_code=status.HTTP_201_CREATED,
)
def add_tax_adjustment(
    payload: TaxAdjustmentCreate,
    db: DbSession,
    current_user: AdminUser,
) -> TaxAdjustmentRead:
    try:
        item = create_adjustment(db, payload, created_by_id=current_user.id)
    except TaxPeriodClosedError as exc:
        raise HTTPException(
            status_code=409,
            detail="Reabre el periodo antes de añadir ajustes",
        ) from exc
    create_configuration_event(
        db,
        category="tax",
        action="adjustment_created",
        summary=f"Ajuste fiscal añadido a {payload.month:02d}/{payload.year}",
        actor_id=current_user.id,
    )
    return TaxAdjustmentRead.model_validate(item)


@router.get("/model-420/{year}/{quarter}", response_model=TaxQuarterSummary)
def read_model_420(
    year: int,
    quarter: int,
    db: DbSession,
    _: AdminUser,
) -> TaxQuarterSummary:
    if not 2000 <= year <= 2100 or quarter not in {1, 2, 3, 4}:
        raise HTTPException(status_code=422, detail="Trimestre no válido")
    return build_quarter_summary(db, year, quarter)


@router.get("/model-420/{year}/{quarter}/csv")
def download_model_420_csv(
    year: int,
    quarter: int,
    db: DbSession,
    _: AdminUser,
) -> Response:
    if not 2000 <= year <= 2100 or quarter not in {1, 2, 3, 4}:
        raise HTTPException(status_code=422, detail="Trimestre no válido")
    summary = build_quarter_summary(db, year, quarter)
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["Modelo", "Ejercicio", "Trimestre", "Periodo de presentación"])
    writer.writerow([summary.model, year, quarter, summary.filing_window])
    writer.writerow([])
    writer.writerow(
        [
            "Mes",
            "Base repercutida",
            "IGIC repercutido",
            "Base soportada",
            "IGIC soportado",
            "Ajustes repercutidos",
            "Ajustes soportados",
            "Resultado",
            "Estado",
        ]
    )
    for month in summary.months:
        writer.writerow(
            [
                month.month_label,
                month.output_base,
                month.output_tax,
                month.input_base,
                month.input_tax,
                month.output_adjustments,
                month.input_adjustments,
                month.result,
                month.status.value,
            ]
        )
    writer.writerow([])
    writer.writerow(
        [
            "TOTAL",
            summary.output_base,
            summary.output_tax,
            summary.input_base,
            summary.input_tax,
            summary.output_adjustments,
            summary.input_adjustments,
            summary.result,
            "cerrado" if summary.all_months_closed else "pendiente de cierre",
        ]
    )
    return Response(
        content=output.getvalue().encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                f'attachment; filename="modelo-420-{year}-T{quarter}-borrador.csv"'
            )
        },
    )
