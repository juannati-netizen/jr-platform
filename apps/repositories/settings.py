from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from apps.core.config import settings
from apps.models.settings import (
    AiConfiguration,
    CompanyProfile,
    ConfigurationEvent,
    FiscalYear,
    FiscalYearStatus,
    VerifactuConfiguration,
)
from apps.schemas.settings import (
    AiConfigurationUpdate,
    CompanyProfileUpdate,
    FiscalYearCreate,
    VerifactuUpdate,
)


class FiscalYearAlreadyExistsError(Exception):
    pass


def get_company_profile(db: Session) -> CompanyProfile:
    profile = db.scalar(select(CompanyProfile).order_by(CompanyProfile.created_at).limit(1))
    if profile is None:
        profile = CompanyProfile()
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def update_company_profile(
    db: Session,
    profile: CompanyProfile,
    payload: CompanyProfileUpdate,
) -> CompanyProfile:
    for field, value in payload.model_dump().items():
        setattr(profile, field, value)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def list_fiscal_years(db: Session) -> list[FiscalYear]:
    statement = (
        select(FiscalYear)
        .options(joinedload(FiscalYear.opened_by), joinedload(FiscalYear.closed_by))
        .order_by(FiscalYear.year.desc())
    )
    return list(db.scalars(statement).unique().all())


def get_fiscal_year(db: Session, fiscal_year_id: str) -> FiscalYear | None:
    statement = (
        select(FiscalYear)
        .where(FiscalYear.id == fiscal_year_id)
        .options(joinedload(FiscalYear.opened_by), joinedload(FiscalYear.closed_by))
    )
    return db.scalar(statement)


def create_fiscal_year(
    db: Session,
    payload: FiscalYearCreate,
    *,
    opened_by_id: str,
) -> FiscalYear:
    item = FiscalYear(
        year=payload.year,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status=FiscalYearStatus.OPEN.value,
        opened_by_id=opened_by_id,
        notes=payload.notes,
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise FiscalYearAlreadyExistsError from exc
    return get_fiscal_year(db, item.id) or item


def open_fiscal_year(db: Session, item: FiscalYear, *, actor_id: str) -> FiscalYear:
    item.status = FiscalYearStatus.OPEN.value
    item.opened_at = datetime.now(UTC)
    item.opened_by_id = actor_id
    item.closed_at = None
    item.closed_by_id = None
    db.add(item)
    db.commit()
    return get_fiscal_year(db, item.id) or item


def close_fiscal_year(db: Session, item: FiscalYear, *, actor_id: str) -> FiscalYear:
    item.status = FiscalYearStatus.CLOSED.value
    item.closed_at = datetime.now(UTC)
    item.closed_by_id = actor_id
    db.add(item)
    db.commit()
    return get_fiscal_year(db, item.id) or item


def get_verifactu_configuration(db: Session) -> VerifactuConfiguration:
    item = db.scalar(
        select(VerifactuConfiguration).order_by(VerifactuConfiguration.created_at).limit(1)
    )
    if item is None:
        item = VerifactuConfiguration()
        db.add(item)
        db.commit()
        db.refresh(item)
    return item


def update_verifactu_configuration(
    db: Session,
    item: VerifactuConfiguration,
    payload: VerifactuUpdate,
) -> VerifactuConfiguration:
    for field, value in payload.model_dump().items():
        setattr(item, field, value)
    item.reviewed_at = datetime.now(UTC)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_ai_configuration(db: Session) -> AiConfiguration:
    item = db.scalar(select(AiConfiguration).order_by(AiConfiguration.created_at).limit(1))
    if item is None:
        item = AiConfiguration()
        db.add(item)
        db.commit()
        db.refresh(item)
    return item


def update_ai_configuration(
    db: Session,
    item: AiConfiguration,
    payload: AiConfigurationUpdate,
) -> AiConfiguration:
    for field, value in payload.model_dump().items():
        setattr(item, field, value)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def create_configuration_event(
    db: Session,
    *,
    category: str,
    action: str,
    summary: str,
    actor_id: str | None,
) -> ConfigurationEvent:
    event = ConfigurationEvent(
        category=category,
        action=action,
        summary=summary,
        actor_id=actor_id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_configuration_events(db: Session, limit: int = 100) -> list[ConfigurationEvent]:
    statement = (
        select(ConfigurationEvent)
        .options(joinedload(ConfigurationEvent.actor))
        .order_by(ConfigurationEvent.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(statement).unique().all())


def ai_api_key_configured() -> bool:
    return bool(settings.ai_api_key.strip())


def ai_base_url_configured() -> bool:
    return bool(settings.ai_base_url.strip())
