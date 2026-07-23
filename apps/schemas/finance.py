from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from apps.models.finance import Invoice, InvoiceStatus, Payment, PaymentMethod, Quote, QuoteStatus
from apps.models.user import User
from apps.schemas.client import ClientReference
from apps.schemas.work_order import UserReference


def user_reference(user: User) -> UserReference:
    return UserReference(id=user.id, full_name=user.full_name, email=user.email)


class LineItemInput(BaseModel):
    description: str = Field(min_length=2, max_length=300)
    quantity: Decimal = Field(gt=0, decimal_places=2)
    unit_price: Decimal = Field(ge=0, decimal_places=2)
    tax_rate: Decimal = Field(default=Decimal("21.00"), ge=0, le=100, decimal_places=2)


class LineItemRead(LineItemInput):
    id: str
    position: int
    line_subtotal: Decimal
    line_tax: Decimal
    line_total: Decimal


class QuoteCreate(BaseModel):
    client_id: str
    work_order_id: str | None = None
    issue_date: date = Field(default_factory=date.today)
    valid_until: date | None = None
    notes: str | None = Field(default=None, max_length=3000)
    items: list[LineItemInput] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_dates(self) -> "QuoteCreate":
        if self.valid_until is not None and self.valid_until < self.issue_date:
            raise ValueError("La fecha de validez no puede ser anterior a la emisión")
        return self


class QuoteUpdate(BaseModel):
    status: QuoteStatus | None = None
    valid_until: date | None = None
    notes: str | None = Field(default=None, max_length=3000)
    items: list[LineItemInput] | None = Field(default=None, min_length=1, max_length=100)


class QuoteRead(BaseModel):
    id: str
    number: str
    client: ClientReference
    work_order_id: str | None
    created_by: UserReference
    status: QuoteStatus
    issue_date: date
    valid_until: date | None
    notes: str | None
    subtotal: Decimal
    tax_total: Decimal
    total: Decimal
    items: list[LineItemRead]
    invoice_id: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, quote: Quote) -> "QuoteRead":
        return cls(
            id=quote.id,
            number=quote.number,
            client=ClientReference.model_validate(quote.client),
            work_order_id=quote.work_order_id,
            created_by=user_reference(quote.created_by),
            status=QuoteStatus(quote.status),
            issue_date=quote.issue_date,
            valid_until=quote.valid_until,
            notes=quote.notes,
            subtotal=quote.subtotal,
            tax_total=quote.tax_total,
            total=quote.total,
            items=[
                LineItemRead(
                    id=item.id,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    tax_rate=item.tax_rate,
                    position=item.position,
                    line_subtotal=item.line_subtotal,
                    line_tax=item.line_tax,
                    line_total=item.line_total,
                )
                for item in quote.items
            ],
            invoice_id=quote.invoice.id if quote.invoice else None,
            created_at=quote.created_at,
            updated_at=quote.updated_at,
        )


class InvoiceCreate(BaseModel):
    client_id: str
    work_order_id: str | None = None
    issue_date: date = Field(default_factory=date.today)
    due_date: date | None = None
    notes: str | None = Field(default=None, max_length=3000)
    items: list[LineItemInput] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_dates(self) -> "InvoiceCreate":
        if self.due_date is not None and self.due_date < self.issue_date:
            raise ValueError("La fecha de vencimiento no puede ser anterior a la emisión")
        return self


class InvoiceUpdate(BaseModel):
    status: InvoiceStatus | None = None
    due_date: date | None = None
    notes: str | None = Field(default=None, max_length=3000)


class PaymentCreate(BaseModel):
    amount: Decimal = Field(gt=0, decimal_places=2)
    method: PaymentMethod = PaymentMethod.BANK_TRANSFER
    paid_at: datetime | None = None
    reference: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=1000)


class PaymentRead(BaseModel):
    id: str
    amount: Decimal
    method: PaymentMethod
    paid_at: datetime
    reference: str | None
    notes: str | None
    recorded_by: UserReference
    created_at: datetime

    @classmethod
    def from_entity(cls, payment: Payment) -> "PaymentRead":
        return cls(
            id=payment.id,
            amount=payment.amount,
            method=PaymentMethod(payment.method),
            paid_at=payment.paid_at,
            reference=payment.reference,
            notes=payment.notes,
            recorded_by=user_reference(payment.recorded_by),
            created_at=payment.created_at,
        )


class InvoiceRead(BaseModel):
    id: str
    number: str
    client: ClientReference
    work_order_id: str | None
    source_quote_id: str | None
    created_by: UserReference
    status: InvoiceStatus
    issue_date: date
    due_date: date | None
    notes: str | None
    subtotal: Decimal
    tax_total: Decimal
    total: Decimal
    paid_total: Decimal
    pending_total: Decimal
    items: list[LineItemRead]
    payments: list[PaymentRead]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, invoice: Invoice) -> "InvoiceRead":
        return cls(
            id=invoice.id,
            number=invoice.number,
            client=ClientReference.model_validate(invoice.client),
            work_order_id=invoice.work_order_id,
            source_quote_id=invoice.source_quote_id,
            created_by=user_reference(invoice.created_by),
            status=InvoiceStatus(invoice.status),
            issue_date=invoice.issue_date,
            due_date=invoice.due_date,
            notes=invoice.notes,
            subtotal=invoice.subtotal,
            tax_total=invoice.tax_total,
            total=invoice.total,
            paid_total=invoice.paid_total,
            pending_total=max(invoice.total - invoice.paid_total, Decimal("0.00")),
            items=[
                LineItemRead(
                    id=item.id,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    tax_rate=item.tax_rate,
                    position=item.position,
                    line_subtotal=item.line_subtotal,
                    line_tax=item.line_tax,
                    line_total=item.line_total,
                )
                for item in invoice.items
            ],
            payments=[PaymentRead.from_entity(payment) for payment in invoice.payments],
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
        )
