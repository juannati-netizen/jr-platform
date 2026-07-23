from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import require_roles
from apps.db.session import get_db
from apps.models.settings import AiProvider, FiscalYearStatus, VerifactuMode
from apps.models.user import User, UserRole
from apps.repositories.settings import (
    FiscalYearAlreadyExistsError,
    ai_api_key_configured,
    ai_base_url_configured,
    close_fiscal_year,
    create_configuration_event,
    create_fiscal_year,
    get_ai_configuration,
    get_company_profile,
    get_fiscal_year,
    get_verifactu_configuration,
    list_configuration_events,
    list_fiscal_years,
    open_fiscal_year,
    update_ai_configuration,
    update_company_profile,
    update_verifactu_configuration,
)
from apps.schemas.settings import (
    AiConfigurationRead,
    AiConfigurationUpdate,
    AiReadiness,
    CompanyProfileRead,
    CompanyProfileUpdate,
    ConfigurationEventRead,
    FiscalYearCreate,
    FiscalYearRead,
    ReadinessItem,
    VerifactuRead,
    VerifactuReadiness,
    VerifactuUpdate,
)

router = APIRouter()
AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN))]
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/company", response_model=CompanyProfileRead)
def read_company_profile(db: DbSession, _: AdminUser) -> CompanyProfileRead:
    return CompanyProfileRead.model_validate(get_company_profile(db))


@router.put("/company", response_model=CompanyProfileRead)
def save_company_profile(
    payload: CompanyProfileUpdate,
    db: DbSession,
    current_user: AdminUser,
) -> CompanyProfileRead:
    profile = update_company_profile(db, get_company_profile(db), payload)
    create_configuration_event(
        db,
        category="company",
        action="updated",
        summary=f"Datos de empresa actualizados: {profile.legal_name}",
        actor_id=current_user.id,
    )
    return CompanyProfileRead.model_validate(profile)


@router.get("/fiscal-years", response_model=list[FiscalYearRead])
def read_fiscal_years(db: DbSession, _: AdminUser) -> list[FiscalYearRead]:
    return [FiscalYearRead.from_entity(item) for item in list_fiscal_years(db)]


@router.post(
    "/fiscal-years",
    response_model=FiscalYearRead,
    status_code=status.HTTP_201_CREATED,
)
def add_fiscal_year(
    payload: FiscalYearCreate,
    db: DbSession,
    current_user: AdminUser,
) -> FiscalYearRead:
    try:
        item = create_fiscal_year(db, payload, opened_by_id=current_user.id)
    except FiscalYearAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail="Ese ejercicio fiscal ya existe") from exc
    create_configuration_event(
        db,
        category="fiscal_year",
        action="opened",
        summary=f"Ejercicio {item.year} abierto",
        actor_id=current_user.id,
    )
    return FiscalYearRead.from_entity(item)


@router.post("/fiscal-years/{fiscal_year_id}/open", response_model=FiscalYearRead)
def reopen_fiscal_year(
    fiscal_year_id: str,
    db: DbSession,
    current_user: AdminUser,
) -> FiscalYearRead:
    item = get_fiscal_year(db, fiscal_year_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Ejercicio fiscal no encontrado")
    if item.status == FiscalYearStatus.OPEN.value:
        return FiscalYearRead.from_entity(item)
    item = open_fiscal_year(db, item, actor_id=current_user.id)
    create_configuration_event(
        db,
        category="fiscal_year",
        action="reopened",
        summary=f"Ejercicio {item.year} reabierto",
        actor_id=current_user.id,
    )
    return FiscalYearRead.from_entity(item)


@router.post("/fiscal-years/{fiscal_year_id}/close", response_model=FiscalYearRead)
def finish_fiscal_year(
    fiscal_year_id: str,
    db: DbSession,
    current_user: AdminUser,
) -> FiscalYearRead:
    item = get_fiscal_year(db, fiscal_year_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Ejercicio fiscal no encontrado")
    if item.status == FiscalYearStatus.CLOSED.value:
        return FiscalYearRead.from_entity(item)
    item = close_fiscal_year(db, item, actor_id=current_user.id)
    create_configuration_event(
        db,
        category="fiscal_year",
        action="closed",
        summary=f"Ejercicio {item.year} cerrado",
        actor_id=current_user.id,
    )
    return FiscalYearRead.from_entity(item)


@router.get("/verifactu", response_model=VerifactuRead)
def read_verifactu(db: DbSession, _: AdminUser) -> VerifactuRead:
    return VerifactuRead.model_validate(get_verifactu_configuration(db))


@router.put("/verifactu", response_model=VerifactuRead)
def save_verifactu(
    payload: VerifactuUpdate,
    db: DbSession,
    current_user: AdminUser,
) -> VerifactuRead:
    if payload.aeat_transmission_enabled and payload.mode != VerifactuMode.TEST:
        raise HTTPException(
            status_code=422,
            detail=(
                "La remisión real a la AEAT no está disponible en esta versión. "
                "Solo puede marcarse en modo de pruebas."
            ),
        )
    item = update_verifactu_configuration(db, get_verifactu_configuration(db), payload)
    create_configuration_event(
        db,
        category="verifactu",
        action="updated",
        summary=f"Configuración VERI*FACTU actualizada en modo {item.mode}",
        actor_id=current_user.id,
    )
    return VerifactuRead.model_validate(item)


@router.get("/verifactu/readiness", response_model=VerifactuReadiness)
def read_verifactu_readiness(db: DbSession, _: AdminUser) -> VerifactuReadiness:
    company = get_company_profile(db)
    item = get_verifactu_configuration(db)
    checks = [
        ReadinessItem(
            key="company_name",
            label="Razón social",
            completed=bool(company.legal_name.strip()),
            detail="Debe identificar al obligado a expedir factura.",
        ),
        ReadinessItem(
            key="tax_id",
            label="NIF/CIF",
            completed=bool(company.tax_id.strip()),
            detail="Debe coincidir con el obligado tributario.",
        ),
        ReadinessItem(
            key="system_identity",
            label="Identificación del sistema",
            completed=bool(item.system_name.strip() and item.system_version.strip()),
            detail="Nombre y versión visibles del sistema de facturación.",
        ),
        ReadinessItem(
            key="producer_identity",
            label="Identificación del productor",
            completed=bool(item.producer_name and item.producer_tax_id),
            detail="Datos del productor o fabricante del sistema.",
        ),
        ReadinessItem(
            key="qr",
            label="Código QR",
            completed=item.qr_enabled,
            detail="Preparación para incluir la representación QR exigida.",
        ),
        ReadinessItem(
            key="hash_chain",
            label="Huella y encadenamiento",
            completed=item.hash_chain_enabled,
            detail="Integridad, trazabilidad e inalterabilidad de los registros.",
        ),
        ReadinessItem(
            key="event_log",
            label="Registro de eventos",
            completed=item.event_log_enabled,
            detail="Registro técnico requerido en modalidad no VERI*FACTU.",
        ),
        ReadinessItem(
            key="responsible_declaration",
            label="Declaración responsable",
            completed=item.responsible_declaration_signed,
            detail="Debe existir por cada versión del sistema.",
        ),
    ]
    completed = sum(1 for check in checks if check.completed)
    if item.mode == VerifactuMode.DISABLED.value:
        readiness_status = "disabled"
    elif completed == len(checks):
        readiness_status = "ready_for_review"
    else:
        readiness_status = "in_progress"
    return VerifactuReadiness(
        status=readiness_status,
        completed=completed,
        total=len(checks),
        items=checks,
        transmission_active=item.aeat_transmission_enabled,
        legal_notice=(
            "Este panel controla la preparación técnica. No certifica el cumplimiento legal "
            "ni activa por sí solo la remisión a la AEAT."
        ),
    )


@router.get("/ai", response_model=AiConfigurationRead)
def read_ai_configuration(db: DbSession, _: AdminUser) -> AiConfigurationRead:
    item = get_ai_configuration(db)
    return AiConfigurationRead(
        **{
            column: getattr(item, column)
            for column in (
                "id",
                "enabled",
                "provider",
                "model",
                "assistant_name",
                "system_prompt",
                "allow_customer_data",
                "allow_financial_data",
                "allow_document_content",
                "human_review_required",
                "retention_days",
                "notes",
                "created_at",
                "updated_at",
            )
        },
        api_key_configured=ai_api_key_configured(),
        base_url_configured=ai_base_url_configured(),
    )


@router.put("/ai", response_model=AiConfigurationRead)
def save_ai_configuration(
    payload: AiConfigurationUpdate,
    db: DbSession,
    current_user: AdminUser,
) -> AiConfigurationRead:
    item = update_ai_configuration(db, get_ai_configuration(db), payload)
    create_configuration_event(
        db,
        category="ai",
        action="updated",
        summary=f"Configuración de IA actualizada: {item.provider}",
        actor_id=current_user.id,
    )
    return read_ai_configuration(db, current_user)


@router.get("/ai/readiness", response_model=AiReadiness)
def read_ai_readiness(db: DbSession, _: AdminUser) -> AiReadiness:
    item = get_ai_configuration(db)
    needs_key = item.provider in {AiProvider.OPENAI.value, AiProvider.AZURE_OPENAI.value}
    needs_url = item.provider in {AiProvider.AZURE_OPENAI.value, AiProvider.CUSTOM.value}
    checks = [
        ReadinessItem(
            key="enabled",
            label="Centro de IA activado",
            completed=item.enabled,
            detail="Activa la IA únicamente cuando la configuración esté revisada.",
        ),
        ReadinessItem(
            key="provider",
            label="Proveedor seleccionado",
            completed=item.provider != AiProvider.DISABLED.value,
            detail="OpenAI, Azure OpenAI, proveedor local o compatible.",
        ),
        ReadinessItem(
            key="model",
            label="Modelo configurado",
            completed=bool(item.model),
            detail="Nombre exacto del modelo que utilizará el asistente.",
        ),
        ReadinessItem(
            key="api_key",
            label="Clave configurada en entorno",
            completed=not needs_key or ai_api_key_configured(),
            detail="Las claves nunca se guardan en la base de datos ni se devuelven al portal.",
        ),
        ReadinessItem(
            key="base_url",
            label="Dirección del proveedor",
            completed=not needs_url or ai_base_url_configured(),
            detail="Necesaria para Azure OpenAI o proveedores compatibles.",
        ),
        ReadinessItem(
            key="human_review",
            label="Revisión humana",
            completed=item.human_review_required,
            detail="Las respuestas con impacto empresarial deben ser revisadas.",
        ),
    ]
    ready = all(check.completed for check in checks)
    return AiReadiness(
        status="ready" if ready else "in_progress",
        ready=ready,
        items=checks,
        security_notice=(
            "Las credenciales se leen desde variables de entorno. Este sprint configura el "
            "centro de IA, pero todavía no envía información a ningún proveedor."
        ),
    )


@router.get("/events", response_model=list[ConfigurationEventRead])
def read_configuration_events(
    db: DbSession,
    _: AdminUser,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[ConfigurationEventRead]:
    return [
        ConfigurationEventRead.model_validate(item)
        for item in list_configuration_events(db, limit=limit)
    ]
