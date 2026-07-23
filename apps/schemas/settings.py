from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from apps.models.settings import AiProvider, FiscalYearStatus, VerifactuMode


class CompanyProfileUpdate(BaseModel):
    legal_name: str = Field(min_length=2, max_length=220)
    trade_name: str | None = Field(default=None, max_length=220)
    tax_id: str = Field(min_length=3, max_length=32)
    legal_form: str | None = Field(default=None, max_length=120)
    tax_regime: str | None = Field(default=None, max_length=180)
    address: str | None = Field(default=None, max_length=500)
    postal_code: str | None = Field(default=None, max_length=20)
    city: str | None = Field(default=None, max_length=120)
    province: str | None = Field(default=None, max_length=120)
    country: str = Field(default="España", min_length=2, max_length=120)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=40)
    website: str | None = Field(default=None, max_length=300)
    iban: str | None = Field(default=None, max_length=50)
    invoice_prefix: str = Field(default="F", min_length=1, max_length=20)
    quote_prefix: str = Field(default="P", min_length=1, max_length=20)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    timezone: str = Field(default="Europe/Madrid", min_length=3, max_length=80)
    logo_data_url: str | None = Field(default=None, max_length=3_000_000)
    brand_color: str = Field(default="#1976d2", pattern=r"^#[0-9A-Fa-f]{6}$")
    document_footer: str | None = Field(default=None, max_length=500)

    @field_validator(
        "trade_name",
        "legal_form",
        "tax_regime",
        "address",
        "postal_code",
        "city",
        "province",
        "email",
        "phone",
        "website",
        "iban",
        "logo_data_url",
        "document_footer",
        mode="before",
    )
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("legal_name", "tax_id", "country", "invoice_prefix", "quote_prefix")
    @classmethod
    def strip_required(cls, value: str) -> str:
        return value.strip()

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("logo_data_url")
    @classmethod
    def validate_logo(cls, value: str | None) -> str | None:
        if value is None:
            return None
        allowed = (
            "data:image/png;base64,",
            "data:image/jpeg;base64,",
            "data:image/webp;base64,",
        )
        if not value.startswith(allowed):
            raise ValueError("El logotipo debe ser PNG, JPG o WebP")
        return value


class CompanyPublicProfile(BaseModel):
    legal_name: str
    trade_name: str | None
    tax_id: str
    address: str | None
    postal_code: str | None
    city: str | None
    province: str | None
    country: str
    email: str | None
    phone: str | None
    website: str | None
    logo_data_url: str | None
    brand_color: str
    document_footer: str | None

    model_config = ConfigDict(from_attributes=True)


class CompanyProfileRead(CompanyProfileUpdate):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FiscalYearCreate(BaseModel):
    year: int = Field(ge=2000, le=2100)
    start_date: date
    end_date: date
    notes: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def validate_dates(self) -> "FiscalYearCreate":
        if self.end_date < self.start_date:
            raise ValueError("La fecha de cierre no puede ser anterior a la apertura")
        return self


class UserSummary(BaseModel):
    id: str
    full_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class FiscalYearRead(BaseModel):
    id: str
    year: int
    start_date: date
    end_date: date
    status: FiscalYearStatus
    opened_at: datetime
    opened_by: UserSummary | None
    closed_at: datetime | None
    closed_by: UserSummary | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, item: object) -> "FiscalYearRead":
        from apps.models.settings import FiscalYear

        if not isinstance(item, FiscalYear):
            raise TypeError("Se esperaba un ejercicio fiscal")
        return cls(
            id=item.id,
            year=item.year,
            start_date=item.start_date,
            end_date=item.end_date,
            status=FiscalYearStatus(item.status),
            opened_at=item.opened_at,
            opened_by=UserSummary.model_validate(item.opened_by) if item.opened_by else None,
            closed_at=item.closed_at,
            closed_by=UserSummary.model_validate(item.closed_by) if item.closed_by else None,
            notes=item.notes,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )


class VerifactuUpdate(BaseModel):
    mode: VerifactuMode = VerifactuMode.DISABLED
    system_name: str = Field(default="JR Platform", min_length=2, max_length=180)
    system_version: str = Field(default="0.11.0", min_length=1, max_length=60)
    producer_name: str | None = Field(default=None, max_length=220)
    producer_tax_id: str | None = Field(default=None, max_length=32)
    qr_enabled: bool = False
    hash_chain_enabled: bool = False
    event_log_enabled: bool = False
    aeat_transmission_enabled: bool = False
    responsible_declaration_signed: bool = False
    certificate_alias: str | None = Field(default=None, max_length=180)
    notes: str | None = Field(default=None, max_length=3000)


class VerifactuRead(VerifactuUpdate):
    id: str
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReadinessItem(BaseModel):
    key: str
    label: str
    completed: bool
    detail: str


class VerifactuReadiness(BaseModel):
    status: str
    completed: int
    total: int
    items: list[ReadinessItem]
    transmission_active: bool
    legal_notice: str


class AiConfigurationUpdate(BaseModel):
    enabled: bool = False
    provider: AiProvider = AiProvider.DISABLED
    model: str | None = Field(default=None, max_length=180)
    assistant_name: str = Field(default="Asistente JR", min_length=2, max_length=120)
    system_prompt: str | None = Field(default=None, max_length=8000)
    allow_customer_data: bool = False
    allow_financial_data: bool = False
    allow_document_content: bool = False
    human_review_required: bool = True
    retention_days: int = Field(default=0, ge=0, le=365)
    notes: str | None = Field(default=None, max_length=3000)

    @model_validator(mode="after")
    def validate_provider(self) -> "AiConfigurationUpdate":
        if self.enabled and self.provider == AiProvider.DISABLED:
            raise ValueError("Selecciona un proveedor de IA antes de activarla")
        if self.enabled and not self.model:
            raise ValueError("Indica el modelo de IA antes de activarla")
        return self


class AiConfigurationRead(AiConfigurationUpdate):
    id: str
    api_key_configured: bool
    base_url_configured: bool
    created_at: datetime
    updated_at: datetime


class AiReadiness(BaseModel):
    status: str
    ready: bool
    items: list[ReadinessItem]
    security_notice: str


class ConfigurationEventRead(BaseModel):
    id: str
    category: str
    action: str
    summary: str
    actor: UserSummary | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
