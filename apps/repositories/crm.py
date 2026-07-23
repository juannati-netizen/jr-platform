from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql import Select

from apps.models.crm import (
    CrmActivity,
    Lead,
    LeadStatus,
    Opportunity,
    OpportunityStage,
    OpportunityStageHistory,
)
from apps.repositories.clients import create_client
from apps.repositories.finance import create_quote
from apps.schemas.client import ClientCreate
from apps.schemas.crm import (
    CrmActivityCreate,
    CrmActivityUpdate,
    CrmSummary,
    LeadCreate,
    LeadUpdate,
    OpportunityCreate,
    OpportunityQuoteConversion,
    OpportunityUpdate,
    PipelineMetric,
)
from apps.schemas.finance import LineItemInput, QuoteCreate

OPEN_STAGES = (
    OpportunityStage.PROSPECTING.value,
    OpportunityStage.QUALIFICATION.value,
    OpportunityStage.PROPOSAL.value,
    OpportunityStage.NEGOTIATION.value,
)


class LeadAlreadyConvertedError(Exception):
    pass


class OpportunityAlreadyConvertedError(Exception):
    pass


class OpportunityCannotConvertError(Exception):
    pass


def lead_statement() -> Select[tuple[Lead]]:
    return select(Lead).options(
        selectinload(Lead.owner),
        selectinload(Lead.converted_client),
    )


def opportunity_statement() -> Select[tuple[Opportunity]]:
    return select(Opportunity).options(
        selectinload(Opportunity.lead).selectinload(Lead.owner),
        selectinload(Opportunity.lead).selectinload(Lead.converted_client),
        selectinload(Opportunity.client),
        selectinload(Opportunity.owner),
        selectinload(Opportunity.quote),
        selectinload(Opportunity.stage_history).selectinload(OpportunityStageHistory.changed_by),
    )


def activity_statement() -> Select[tuple[CrmActivity]]:
    return select(CrmActivity).options(
        selectinload(CrmActivity.assigned_to),
        selectinload(CrmActivity.created_by),
    )


def list_leads(
    db: Session,
    *,
    search: str | None = None,
    status: LeadStatus | None = None,
) -> list[Lead]:
    statement = lead_statement()
    if status is not None:
        statement = statement.where(Lead.status == status.value)
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Lead.name.ilike(pattern),
                Lead.company.ilike(pattern),
                Lead.email.ilike(pattern),
                Lead.phone.ilike(pattern),
            )
        )
    statement = statement.order_by(Lead.updated_at.desc())
    return list(db.scalars(statement).unique().all())


def get_lead(db: Session, lead_id: str) -> Lead | None:
    return db.scalar(lead_statement().where(Lead.id == lead_id))


def create_lead(db: Session, payload: LeadCreate) -> Lead:
    lead = Lead(
        name=payload.name.strip(),
        company=payload.company.strip() if payload.company else None,
        phone=payload.phone.strip() if payload.phone else None,
        email=str(payload.email).lower() if payload.email else None,
        source=payload.source.value,
        status=payload.status.value,
        owner_id=payload.owner_id,
        notes=payload.notes.strip() if payload.notes else None,
    )
    db.add(lead)
    db.commit()
    return get_lead(db, lead.id) or lead


def update_lead(db: Session, lead: Lead, payload: LeadUpdate) -> Lead:
    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes and payload.name is not None:
        lead.name = payload.name.strip()
    if "company" in changes:
        lead.company = payload.company.strip() if payload.company else None
    if "phone" in changes:
        lead.phone = payload.phone.strip() if payload.phone else None
    if "email" in changes:
        lead.email = str(payload.email).lower() if payload.email else None
    if "source" in changes and payload.source is not None:
        lead.source = payload.source.value
    if "status" in changes and payload.status is not None:
        lead.status = payload.status.value
    if "owner_id" in changes:
        lead.owner_id = payload.owner_id
    if "notes" in changes:
        lead.notes = payload.notes.strip() if payload.notes else None
    db.commit()
    return get_lead(db, lead.id) or lead


def convert_lead_to_client(db: Session, lead: Lead, *, converted_by_id: str) -> Lead:
    if lead.converted_client_id is not None:
        raise LeadAlreadyConvertedError
    client = create_client(
        db,
        ClientCreate(
            name=lead.company or lead.name,
            email=lead.email,
            phone=lead.phone,
            notes=f"Convertido desde lead: {lead.name}"
            + (f"\n\n{lead.notes}" if lead.notes else ""),
        ),
    )
    lead.converted_client_id = client.id
    lead.converted_at = datetime.now(UTC)
    lead.converted_by_id = converted_by_id
    lead.status = LeadStatus.CONVERTED.value
    db.commit()
    db.expire_all()
    return get_lead(db, lead.id) or lead


def list_opportunities(
    db: Session,
    *,
    stage: OpportunityStage | None = None,
    owner_id: str | None = None,
) -> list[Opportunity]:
    statement = opportunity_statement()
    if stage is not None:
        statement = statement.where(Opportunity.stage == stage.value)
    if owner_id is not None:
        statement = statement.where(Opportunity.owner_id == owner_id)
    statement = statement.order_by(Opportunity.expected_close, Opportunity.updated_at.desc())
    return list(db.scalars(statement).unique().all())


def get_opportunity(db: Session, opportunity_id: str) -> Opportunity | None:
    return db.scalar(opportunity_statement().where(Opportunity.id == opportunity_id))


def create_opportunity(
    db: Session,
    payload: OpportunityCreate,
    *,
    changed_by_id: str,
) -> Opportunity:
    opportunity = Opportunity(
        title=payload.title.strip(),
        lead_id=payload.lead_id,
        client_id=payload.client_id,
        owner_id=payload.owner_id,
        stage=payload.stage.value,
        estimated_value=payload.estimated_value,
        probability=payload.probability,
        expected_close=payload.expected_close,
        notes=payload.notes.strip() if payload.notes else None,
    )
    opportunity.stage_history.append(
        OpportunityStageHistory(
            previous_stage=None,
            new_stage=payload.stage.value,
            changed_by_id=changed_by_id,
            change_source="create",
        )
    )
    db.add(opportunity)
    db.commit()
    return get_opportunity(db, opportunity.id) or opportunity


def update_opportunity(
    db: Session,
    opportunity: Opportunity,
    payload: OpportunityUpdate,
    *,
    changed_by_id: str,
) -> Opportunity:
    changes = payload.model_dump(exclude_unset=True)
    if "title" in changes and payload.title is not None:
        opportunity.title = payload.title.strip()
    if "lead_id" in changes:
        opportunity.lead_id = payload.lead_id
    if "client_id" in changes:
        opportunity.client_id = payload.client_id
    if "owner_id" in changes:
        opportunity.owner_id = payload.owner_id
    if "estimated_value" in changes and payload.estimated_value is not None:
        opportunity.estimated_value = payload.estimated_value
    if "probability" in changes and payload.probability is not None:
        opportunity.probability = payload.probability
    if "expected_close" in changes:
        opportunity.expected_close = payload.expected_close
    if "notes" in changes:
        opportunity.notes = payload.notes.strip() if payload.notes else None
    if "stage" in changes and payload.stage is not None:
        previous_stage = opportunity.stage
        if previous_stage != payload.stage.value:
            opportunity.stage = payload.stage.value
            opportunity.stage_history.append(
                OpportunityStageHistory(
                    previous_stage=previous_stage,
                    new_stage=payload.stage.value,
                    changed_by_id=changed_by_id,
                    change_source=payload.change_source,
                )
            )
    db.commit()
    return get_opportunity(db, opportunity.id) or opportunity


def convert_opportunity_to_quote(
    db: Session,
    opportunity: Opportunity,
    payload: OpportunityQuoteConversion,
    *,
    converted_by_id: str,
) -> Opportunity:
    if opportunity.quote_id is not None:
        raise OpportunityAlreadyConvertedError
    if opportunity.client_id is None or opportunity.stage == OpportunityStage.LOST.value:
        raise OpportunityCannotConvertError

    quote = create_quote(
        db,
        QuoteCreate(
            client_id=opportunity.client_id,
            notes=payload.notes or opportunity.notes,
            items=[
                LineItemInput(
                    description=opportunity.title,
                    quantity=Decimal("1.00"),
                    unit_price=opportunity.estimated_value,
                    tax_rate=payload.tax_rate,
                )
            ],
        ),
        created_by_id=converted_by_id,
    )
    opportunity.quote_id = quote.id
    opportunity.converted_at = datetime.now(UTC)
    opportunity.converted_by_id = converted_by_id
    db.commit()
    db.expire_all()
    return get_opportunity(db, opportunity.id) or opportunity


def list_activities(
    db: Session,
    *,
    pending_only: bool = False,
    assigned_to_id: str | None = None,
) -> list[CrmActivity]:
    statement = activity_statement()
    if pending_only:
        statement = statement.where(CrmActivity.completed.is_(False))
    if assigned_to_id is not None:
        statement = statement.where(CrmActivity.assigned_to_id == assigned_to_id)
    statement = statement.order_by(
        CrmActivity.completed, CrmActivity.due_at, CrmActivity.created_at
    )
    return list(db.scalars(statement).unique().all())


def get_activity(db: Session, activity_id: str) -> CrmActivity | None:
    return db.scalar(activity_statement().where(CrmActivity.id == activity_id))


def create_activity(
    db: Session,
    payload: CrmActivityCreate,
    *,
    created_by_id: str,
) -> CrmActivity:
    activity = CrmActivity(
        opportunity_id=payload.opportunity_id,
        lead_id=payload.lead_id,
        assigned_to_id=payload.assigned_to_id,
        created_by_id=created_by_id,
        activity_type=payload.activity_type.value,
        subject=payload.subject.strip(),
        due_at=payload.due_at,
        completed=payload.completed,
        completed_at=datetime.now(UTC) if payload.completed else None,
        notes=payload.notes.strip() if payload.notes else None,
    )
    db.add(activity)
    db.commit()
    return get_activity(db, activity.id) or activity


def update_activity(
    db: Session,
    activity: CrmActivity,
    payload: CrmActivityUpdate,
) -> CrmActivity:
    changes = payload.model_dump(exclude_unset=True)
    if "assigned_to_id" in changes:
        activity.assigned_to_id = payload.assigned_to_id
    if "activity_type" in changes and payload.activity_type is not None:
        activity.activity_type = payload.activity_type.value
    if "subject" in changes and payload.subject is not None:
        activity.subject = payload.subject.strip()
    if "due_at" in changes:
        activity.due_at = payload.due_at
    if "notes" in changes:
        activity.notes = payload.notes.strip() if payload.notes else None
    if "completed" in changes and payload.completed is not None:
        activity.completed = payload.completed
        activity.completed_at = datetime.now(UTC) if payload.completed else None
    db.commit()
    return get_activity(db, activity.id) or activity


def get_crm_summary(db: Session) -> CrmSummary:
    total_leads = db.scalar(select(func.count()).select_from(Lead)) or 0
    qualified_leads = (
        db.scalar(
            select(func.count()).select_from(Lead).where(Lead.status == LeadStatus.QUALIFIED.value)
        )
        or 0
    )
    open_opportunities = (
        db.scalar(
            select(func.count()).select_from(Opportunity).where(Opportunity.stage.in_(OPEN_STAGES))
        )
        or 0
    )
    won_opportunities = (
        db.scalar(
            select(func.count())
            .select_from(Opportunity)
            .where(Opportunity.stage == OpportunityStage.WON.value)
        )
        or 0
    )
    pipeline_value = db.scalar(
        select(func.sum(Opportunity.estimated_value)).where(Opportunity.stage.in_(OPEN_STAGES))
    ) or Decimal("0.00")
    weighted_pipeline = db.scalar(
        select(
            func.sum(Opportunity.estimated_value * Opportunity.probability / Decimal("100"))
        ).where(Opportunity.stage.in_(OPEN_STAGES))
    ) or Decimal("0.00")
    pending_activities = (
        db.scalar(
            select(func.count()).select_from(CrmActivity).where(CrmActivity.completed.is_(False))
        )
        or 0
    )
    overdue_activities = (
        db.scalar(
            select(func.count())
            .select_from(CrmActivity)
            .where(
                CrmActivity.completed.is_(False),
                CrmActivity.due_at.is_not(None),
                CrmActivity.due_at < datetime.now(UTC),
            )
        )
        or 0
    )

    rows = db.execute(
        select(
            Opportunity.stage,
            func.count(Opportunity.id),
            func.coalesce(func.sum(Opportunity.estimated_value), 0),
            func.coalesce(
                func.sum(Opportunity.estimated_value * Opportunity.probability / Decimal("100")),
                0,
            ),
        ).group_by(Opportunity.stage)
    ).all()
    by_stage = {
        str(stage): (int(count), Decimal(total), Decimal(weighted))
        for stage, count, total, weighted in rows
    }
    stages = [
        PipelineMetric(
            stage=stage,
            count=by_stage.get(stage.value, (0, Decimal("0"), Decimal("0")))[0],
            total_value=by_stage.get(stage.value, (0, Decimal("0"), Decimal("0")))[1],
            weighted_value=by_stage.get(stage.value, (0, Decimal("0"), Decimal("0")))[2],
        )
        for stage in OpportunityStage
    ]
    return CrmSummary(
        total_leads=total_leads,
        qualified_leads=qualified_leads,
        open_opportunities=open_opportunities,
        won_opportunities=won_opportunities,
        pipeline_value=pipeline_value,
        weighted_pipeline=weighted_pipeline,
        pending_activities=pending_activities,
        overdue_activities=overdue_activities,
        stages=stages,
    )
