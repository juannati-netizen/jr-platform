from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from apps.api.dependencies.auth import get_current_user
from apps.db.session import get_db
from apps.models.crm import LeadStatus, OpportunityStage
from apps.models.user import User
from apps.repositories.clients import get_client
from apps.repositories.crm import (
    LeadAlreadyConvertedError,
    OpportunityAlreadyConvertedError,
    OpportunityCannotConvertError,
    convert_lead_to_client,
    convert_opportunity_to_quote,
    create_activity,
    create_lead,
    create_opportunity,
    get_activity,
    get_crm_summary,
    get_lead,
    get_opportunity,
    list_activities,
    list_leads,
    list_opportunities,
    update_activity,
    update_lead,
    update_opportunity,
)
from apps.repositories.users import get_user_by_id
from apps.schemas.client import ClientRead
from apps.schemas.crm import (
    CrmActivityCreate,
    CrmActivityRead,
    CrmActivityUpdate,
    CrmSummary,
    LeadCreate,
    LeadRead,
    LeadUpdate,
    OpportunityCreate,
    OpportunityQuoteConversion,
    OpportunityRead,
    OpportunityStageHistoryRead,
    OpportunityUpdate,
)
from apps.schemas.finance import QuoteRead

router = APIRouter()


def validate_user(db: Session, user_id: str | None) -> None:
    if user_id is None:
        return
    user = get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=422, detail="El responsable indicado no está disponible")


def validate_lead_client_refs(
    db: Session,
    *,
    lead_id: str | None,
    client_id: str | None,
) -> None:
    if lead_id is not None and get_lead(db, lead_id) is None:
        raise HTTPException(status_code=422, detail="El lead indicado no existe")
    if client_id is not None:
        client = get_client(db, client_id)
        if client is None or not client.is_active:
            raise HTTPException(status_code=422, detail="El cliente indicado no está disponible")


@router.get("/summary", response_model=CrmSummary)
def read_crm_summary(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> CrmSummary:
    return get_crm_summary(db)


@router.get("/leads", response_model=list[LeadRead])
def read_leads(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    search: Annotated[str | None, Query(max_length=180)] = None,
    lead_status: Annotated[LeadStatus | None, Query(alias="status")] = None,
) -> list[LeadRead]:
    return [
        LeadRead.from_entity(item) for item in list_leads(db, search=search, status=lead_status)
    ]


@router.post("/leads", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def add_lead(
    payload: LeadCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> LeadRead:
    validate_user(db, payload.owner_id)
    return LeadRead.from_entity(create_lead(db, payload))


@router.patch("/leads/{lead_id}", response_model=LeadRead)
def change_lead(
    lead_id: str,
    payload: LeadUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> LeadRead:
    lead = get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    if "owner_id" in payload.model_dump(exclude_unset=True):
        validate_user(db, payload.owner_id)
    return LeadRead.from_entity(update_lead(db, lead, payload))


@router.post("/leads/{lead_id}/convert-to-client", response_model=ClientRead)
def convert_lead(
    lead_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ClientRead:
    lead = get_lead(db, lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    try:
        converted = convert_lead_to_client(db, lead, converted_by_id=current_user.id)
    except LeadAlreadyConvertedError as exc:
        raise HTTPException(status_code=409, detail="El lead ya fue convertido") from exc
    if converted.converted_client is None:
        raise HTTPException(status_code=500, detail="No se pudo recuperar el cliente convertido")
    return ClientRead.model_validate(converted.converted_client)


@router.get("/opportunities", response_model=list[OpportunityRead])
def read_opportunities(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    stage: OpportunityStage | None = None,
    assigned_to_me: bool = False,
) -> list[OpportunityRead]:
    owner_id = current_user.id if assigned_to_me else None
    return [
        OpportunityRead.from_entity(item)
        for item in list_opportunities(db, stage=stage, owner_id=owner_id)
    ]


@router.post(
    "/opportunities",
    response_model=OpportunityRead,
    status_code=status.HTTP_201_CREATED,
)
def add_opportunity(
    payload: OpportunityCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OpportunityRead:
    validate_user(db, payload.owner_id)
    validate_lead_client_refs(db, lead_id=payload.lead_id, client_id=payload.client_id)
    return OpportunityRead.from_entity(
        create_opportunity(db, payload, changed_by_id=current_user.id)
    )


@router.patch("/opportunities/{opportunity_id}", response_model=OpportunityRead)
def change_opportunity(
    opportunity_id: str,
    payload: OpportunityUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OpportunityRead:
    opportunity = get_opportunity(db, opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    changes = payload.model_dump(exclude_unset=True)
    if "owner_id" in changes:
        validate_user(db, payload.owner_id)
    validate_lead_client_refs(
        db,
        lead_id=payload.lead_id if "lead_id" in changes else None,
        client_id=payload.client_id if "client_id" in changes else None,
    )
    return OpportunityRead.from_entity(
        update_opportunity(db, opportunity, payload, changed_by_id=current_user.id)
    )


@router.get(
    "/opportunities/{opportunity_id}/stage-history",
    response_model=list[OpportunityStageHistoryRead],
)
def read_stage_history(
    opportunity_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> list[OpportunityStageHistoryRead]:
    opportunity = get_opportunity(db, opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    return [OpportunityStageHistoryRead.from_entity(item) for item in opportunity.stage_history]


@router.post("/opportunities/{opportunity_id}/convert-to-quote", response_model=QuoteRead)
def convert_opportunity(
    opportunity_id: str,
    payload: OpportunityQuoteConversion,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> QuoteRead:
    opportunity = get_opportunity(db, opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
    try:
        converted = convert_opportunity_to_quote(
            db,
            opportunity,
            payload,
            converted_by_id=current_user.id,
        )
    except OpportunityAlreadyConvertedError as exc:
        raise HTTPException(status_code=409, detail="La oportunidad ya tiene presupuesto") from exc
    except OpportunityCannotConvertError as exc:
        raise HTTPException(
            status_code=409,
            detail="La oportunidad necesita cliente y no puede estar perdida",
        ) from exc
    if converted.quote is None:
        raise HTTPException(status_code=500, detail="No se pudo recuperar el presupuesto")
    return QuoteRead.from_entity(converted.quote)


@router.get("/activities", response_model=list[CrmActivityRead])
def read_activities(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    pending_only: bool = False,
    assigned_to_me: bool = False,
) -> list[CrmActivityRead]:
    assigned_to_id = current_user.id if assigned_to_me else None
    return [
        CrmActivityRead.from_entity(item)
        for item in list_activities(
            db,
            pending_only=pending_only,
            assigned_to_id=assigned_to_id,
        )
    ]


@router.post(
    "/activities",
    response_model=CrmActivityRead,
    status_code=status.HTTP_201_CREATED,
)
def add_activity(
    payload: CrmActivityCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CrmActivityRead:
    validate_user(db, payload.assigned_to_id)
    validate_lead_client_refs(db, lead_id=payload.lead_id, client_id=None)
    if payload.opportunity_id is not None and get_opportunity(db, payload.opportunity_id) is None:
        raise HTTPException(status_code=422, detail="La oportunidad indicada no existe")
    return CrmActivityRead.from_entity(create_activity(db, payload, created_by_id=current_user.id))


@router.patch("/activities/{activity_id}", response_model=CrmActivityRead)
def change_activity(
    activity_id: str,
    payload: CrmActivityUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> CrmActivityRead:
    activity = get_activity(db, activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    if "assigned_to_id" in payload.model_dump(exclude_unset=True):
        validate_user(db, payload.assigned_to_id)
    return CrmActivityRead.from_entity(update_activity(db, activity, payload))
