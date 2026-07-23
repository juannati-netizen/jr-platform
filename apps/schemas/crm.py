from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, model_validator

from apps.models.crm import (
    CrmActivity,
    CrmActivityType,
    Lead,
    LeadSource,
    LeadStatus,
    Opportunity,
    OpportunityStage,
    OpportunityStageHistory,
)
from apps.schemas.client import ClientReference
from apps.schemas.work_order import UserReference


class LeadCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    company: str | None = Field(default=None, max_length=180)
    phone: str | None = Field(default=None, max_length=40)
    email: EmailStr | None = None
    source: LeadSource = LeadSource.OTHER
    status: LeadStatus = LeadStatus.NEW
    owner_id: str | None = None
    notes: str | None = Field(default=None, max_length=4000)


class LeadUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    company: str | None = Field(default=None, max_length=180)
    phone: str | None = Field(default=None, max_length=40)
    email: EmailStr | None = None
    source: LeadSource | None = None
    status: LeadStatus | None = None
    owner_id: str | None = None
    notes: str | None = Field(default=None, max_length=4000)


class LeadRead(BaseModel):
    id: str
    name: str
    company: str | None
    phone: str | None
    email: str | None
    source: LeadSource
    status: LeadStatus
    owner: UserReference | None
    notes: str | None
    converted_client: ClientReference | None
    converted_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, lead: Lead) -> "LeadRead":
        owner = None
        if lead.owner is not None:
            owner = UserReference(
                id=lead.owner.id,
                full_name=lead.owner.full_name,
                email=lead.owner.email,
            )
        client = None
        if lead.converted_client is not None:
            client = ClientReference.model_validate(lead.converted_client)
        return cls(
            id=lead.id,
            name=lead.name,
            company=lead.company,
            phone=lead.phone,
            email=lead.email,
            source=LeadSource(lead.source),
            status=LeadStatus(lead.status),
            owner=owner,
            notes=lead.notes,
            converted_client=client,
            converted_at=lead.converted_at,
            created_at=lead.created_at,
            updated_at=lead.updated_at,
        )


class OpportunityCreate(BaseModel):
    title: str = Field(min_length=3, max_length=220)
    lead_id: str | None = None
    client_id: str | None = None
    owner_id: str | None = None
    stage: OpportunityStage = OpportunityStage.PROSPECTING
    estimated_value: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    probability: int = Field(default=10, ge=0, le=100)
    expected_close: date | None = None
    notes: str | None = Field(default=None, max_length=5000)


class OpportunityUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=220)
    lead_id: str | None = None
    client_id: str | None = None
    owner_id: str | None = None
    stage: OpportunityStage | None = None
    estimated_value: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    probability: int | None = Field(default=None, ge=0, le=100)
    expected_close: date | None = None
    notes: str | None = Field(default=None, max_length=5000)
    change_source: str = Field(default="ui", max_length=40)


class OpportunityRead(BaseModel):
    id: str
    title: str
    lead: LeadRead | None
    client: ClientReference | None
    owner: UserReference | None
    stage: OpportunityStage
    estimated_value: Decimal
    probability: int
    weighted_value: Decimal
    expected_close: date | None
    notes: str | None
    quote_id: str | None
    converted_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, opportunity: Opportunity) -> "OpportunityRead":
        owner = None
        if opportunity.owner is not None:
            owner = UserReference(
                id=opportunity.owner.id,
                full_name=opportunity.owner.full_name,
                email=opportunity.owner.email,
            )
        client = None
        if opportunity.client is not None:
            client = ClientReference.model_validate(opportunity.client)
        return cls(
            id=opportunity.id,
            title=opportunity.title,
            lead=LeadRead.from_entity(opportunity.lead) if opportunity.lead else None,
            client=client,
            owner=owner,
            stage=OpportunityStage(opportunity.stage),
            estimated_value=opportunity.estimated_value,
            probability=opportunity.probability,
            weighted_value=(
                opportunity.estimated_value * Decimal(opportunity.probability) / Decimal("100")
            ),
            expected_close=opportunity.expected_close,
            notes=opportunity.notes,
            quote_id=opportunity.quote_id,
            converted_at=opportunity.converted_at,
            created_at=opportunity.created_at,
            updated_at=opportunity.updated_at,
        )


class OpportunityStageHistoryRead(BaseModel):
    id: str
    previous_stage: OpportunityStage | None
    new_stage: OpportunityStage
    changed_by: UserReference | None
    change_source: str
    changed_at: datetime

    @classmethod
    def from_entity(cls, history: OpportunityStageHistory) -> "OpportunityStageHistoryRead":
        changed_by = None
        if history.changed_by is not None:
            changed_by = UserReference(
                id=history.changed_by.id,
                full_name=history.changed_by.full_name,
                email=history.changed_by.email,
            )
        return cls(
            id=history.id,
            previous_stage=(
                OpportunityStage(history.previous_stage)
                if history.previous_stage is not None
                else None
            ),
            new_stage=OpportunityStage(history.new_stage),
            changed_by=changed_by,
            change_source=history.change_source,
            changed_at=history.changed_at,
        )


class OpportunityQuoteConversion(BaseModel):
    tax_rate: Decimal = Field(default=Decimal("7.00"), ge=0, le=100, decimal_places=2)
    notes: str | None = Field(default=None, max_length=3000)


class CrmActivityCreate(BaseModel):
    opportunity_id: str | None = None
    lead_id: str | None = None
    assigned_to_id: str | None = None
    activity_type: CrmActivityType = CrmActivityType.TASK
    subject: str = Field(min_length=2, max_length=220)
    due_at: datetime | None = None
    completed: bool = False
    notes: str | None = Field(default=None, max_length=4000)

    @model_validator(mode="after")
    def validate_parent(self) -> "CrmActivityCreate":
        if self.opportunity_id is None and self.lead_id is None:
            raise ValueError("La actividad debe vincularse a un lead o una oportunidad")
        return self


class CrmActivityUpdate(BaseModel):
    assigned_to_id: str | None = None
    activity_type: CrmActivityType | None = None
    subject: str | None = Field(default=None, min_length=2, max_length=220)
    due_at: datetime | None = None
    completed: bool | None = None
    notes: str | None = Field(default=None, max_length=4000)


class CrmActivityRead(BaseModel):
    id: str
    opportunity_id: str | None
    lead_id: str | None
    assigned_to: UserReference | None
    created_by: UserReference
    activity_type: CrmActivityType
    subject: str
    due_at: datetime | None
    completed: bool
    completed_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, activity: CrmActivity) -> "CrmActivityRead":
        assigned = None
        if activity.assigned_to is not None:
            assigned = UserReference(
                id=activity.assigned_to.id,
                full_name=activity.assigned_to.full_name,
                email=activity.assigned_to.email,
            )
        return cls(
            id=activity.id,
            opportunity_id=activity.opportunity_id,
            lead_id=activity.lead_id,
            assigned_to=assigned,
            created_by=UserReference(
                id=activity.created_by.id,
                full_name=activity.created_by.full_name,
                email=activity.created_by.email,
            ),
            activity_type=CrmActivityType(activity.activity_type),
            subject=activity.subject,
            due_at=activity.due_at,
            completed=activity.completed,
            completed_at=activity.completed_at,
            notes=activity.notes,
            created_at=activity.created_at,
            updated_at=activity.updated_at,
        )


class PipelineMetric(BaseModel):
    stage: OpportunityStage
    count: int
    total_value: Decimal
    weighted_value: Decimal


class CrmSummary(BaseModel):
    total_leads: int
    qualified_leads: int
    open_opportunities: int
    won_opportunities: int
    pipeline_value: Decimal
    weighted_pipeline: Decimal
    pending_activities: int
    overdue_activities: int
    stages: list[PipelineMetric]
