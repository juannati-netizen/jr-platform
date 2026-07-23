from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from apps.models.tax import (
    TaxAdjustmentDirection,
    TaxFilingModel,
    TaxPeriodStatus,
    TaxSystem,
)


class TaxConfigurationUpdate(BaseModel):
    tax_system: TaxSystem = TaxSystem.IGIC
    filing_model: TaxFilingModel = TaxFilingModel.MODEL_420
    filing_frequency: str = Field(default="quarterly", pattern="^quarterly$")
    monthly_tracking_enabled: bool = True
    default_tax_rate: Decimal = Field(default=Decimal("7.00"), ge=0, le=100, decimal_places=2)
    notes: str | None = Field(default=None, max_length=3000)

    @model_validator(mode="after")
    def validate_model(self) -> "TaxConfigurationUpdate":
        if self.tax_system == TaxSystem.IGIC and self.filing_model != TaxFilingModel.MODEL_420:
            raise ValueError("El régimen IGIC de esta versión utiliza el modelo 420")
        return self


class TaxConfigurationRead(TaxConfigurationUpdate):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaxRateBreakdown(BaseModel):
    tax_rate: Decimal
    taxable_base: Decimal
    tax_amount: Decimal


class TaxAdjustmentCreate(BaseModel):
    year: int = Field(ge=2000, le=2100)
    month: int = Field(ge=1, le=12)
    direction: TaxAdjustmentDirection
    amount: Decimal = Field(gt=0, decimal_places=2)
    description: str = Field(min_length=2, max_length=500)


class TaxAdjustmentRead(BaseModel):
    id: str
    year: int
    month: int
    direction: TaxAdjustmentDirection
    amount: Decimal
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaxMonthSummary(BaseModel):
    year: int
    month: int
    month_label: str
    status: TaxPeriodStatus
    output_base: Decimal
    output_tax: Decimal
    input_base: Decimal
    input_tax: Decimal
    output_adjustments: Decimal
    input_adjustments: Decimal
    result: Decimal
    result_type: str
    output_breakdown: list[TaxRateBreakdown]
    input_breakdown: list[TaxRateBreakdown]
    adjustments: list[TaxAdjustmentRead]
    closed_at: datetime | None
    legal_notice: str


class TaxPeriodAction(BaseModel):
    notes: str | None = Field(default=None, max_length=2000)


class TaxQuarterSummary(BaseModel):
    year: int
    quarter: int
    period_label: str
    months: list[TaxMonthSummary]
    output_base: Decimal
    output_tax: Decimal
    input_base: Decimal
    input_tax: Decimal
    output_adjustments: Decimal
    input_adjustments: Decimal
    result: Decimal
    result_type: str
    model: str
    filing_window: str
    all_months_closed: bool
    legal_notice: str
