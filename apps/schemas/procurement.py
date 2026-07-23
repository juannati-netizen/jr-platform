from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from apps.models.procurement import Expense, ExpenseCategory, ExpenseStatus
from apps.models.work_order import WorkOrder
from apps.schemas.work_order import UserReference


class SupplierCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    tax_id: str | None = Field(default=None, max_length=32)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=40)
    address: str | None = Field(default=None, max_length=1000)
    notes: str | None = Field(default=None, max_length=4000)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip()

    @field_validator("tax_id", "email", "phone", "address", "notes", mode="before")
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class SupplierUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    tax_id: str | None = Field(default=None, max_length=32)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=40)
    address: str | None = Field(default=None, max_length=1000)
    notes: str | None = Field(default=None, max_length=4000)
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @field_validator("tax_id", "email", "phone", "address", "notes", mode="before")
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class SupplierRead(BaseModel):
    id: str
    name: str
    tax_id: str | None
    email: EmailStr | None
    phone: str | None
    address: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SupplierReference(BaseModel):
    id: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class WorkOrderReference(BaseModel):
    id: str
    title: str
    client_name: str

    @classmethod
    def from_entity(cls, work_order: WorkOrder) -> "WorkOrderReference":
        return cls(
            id=work_order.id,
            title=work_order.title,
            client_name=work_order.client.name,
        )


class ExpenseCreate(BaseModel):
    supplier_id: str | None = None
    work_order_id: str | None = None
    description: str = Field(min_length=2, max_length=300)
    category: ExpenseCategory = ExpenseCategory.OTHER
    status: ExpenseStatus = ExpenseStatus.PENDING
    expense_date: date = Field(default_factory=date.today)
    subtotal: Decimal = Field(gt=0, decimal_places=2)
    tax_rate: Decimal = Field(default=Decimal("21.00"), ge=0, le=100, decimal_places=2)
    reference: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=3000)

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        return value.strip()

    @field_validator("supplier_id", "work_order_id", "reference", "notes", mode="before")
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class ExpenseUpdate(BaseModel):
    supplier_id: str | None = None
    work_order_id: str | None = None
    description: str | None = Field(default=None, min_length=2, max_length=300)
    category: ExpenseCategory | None = None
    status: ExpenseStatus | None = None
    expense_date: date | None = None
    subtotal: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    tax_rate: Decimal | None = Field(default=None, ge=0, le=100, decimal_places=2)
    reference: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=3000)

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @field_validator("supplier_id", "work_order_id", "reference", "notes", mode="before")
    @classmethod
    def empty_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class ExpenseRead(BaseModel):
    id: str
    supplier: SupplierReference | None
    work_order: WorkOrderReference | None
    created_by: UserReference
    description: str
    category: ExpenseCategory
    status: ExpenseStatus
    expense_date: date
    subtotal: Decimal
    tax_rate: Decimal
    tax_total: Decimal
    total: Decimal
    reference: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, expense: Expense) -> "ExpenseRead":
        return cls(
            id=expense.id,
            supplier=(
                SupplierReference.model_validate(expense.supplier)
                if expense.supplier is not None
                else None
            ),
            work_order=(
                WorkOrderReference.from_entity(expense.work_order)
                if expense.work_order is not None
                else None
            ),
            created_by=UserReference(
                id=expense.created_by.id,
                full_name=expense.created_by.full_name,
                email=expense.created_by.email,
            ),
            description=expense.description,
            category=ExpenseCategory(expense.category),
            status=ExpenseStatus(expense.status),
            expense_date=expense.expense_date,
            subtotal=expense.subtotal,
            tax_rate=expense.tax_rate,
            tax_total=expense.tax_total,
            total=expense.total,
            reference=expense.reference,
            notes=expense.notes,
            created_at=expense.created_at,
            updated_at=expense.updated_at,
        )


class WorkOrderProfitability(BaseModel):
    id: str
    title: str
    client_name: str
    invoiced_revenue: Decimal
    collected_revenue: Decimal
    expenses_total: Decimal
    gross_margin: Decimal
    realized_margin: Decimal


class ClientProfitability(BaseModel):
    id: str
    name: str
    invoiced_revenue: Decimal
    collected_revenue: Decimal
    expenses_total: Decimal
    gross_margin: Decimal
    realized_margin: Decimal


class ProfitabilitySummary(BaseModel):
    invoiced_revenue: Decimal
    collected_revenue: Decimal
    expenses_total: Decimal
    material_costs: Decimal
    gross_margin: Decimal
    realized_margin: Decimal
    gross_margin_percent: Decimal
    work_orders: list[WorkOrderProfitability]
    clients: list[ClientProfitability]
