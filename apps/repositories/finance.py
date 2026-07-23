from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql import Select

from apps.models.finance import (
    Invoice,
    InvoiceItem,
    InvoiceStatus,
    Payment,
    Quote,
    QuoteItem,
    QuoteStatus,
)
from apps.schemas.finance import (
    InvoiceCreate,
    InvoiceUpdate,
    LineItemInput,
    PaymentCreate,
    QuoteCreate,
    QuoteUpdate,
)


TWOPLACES = Decimal("0.01")


class QuoteAlreadyInvoicedError(Exception):
    pass


class QuoteNotAcceptedError(Exception):
    pass


class PaymentExceedsPendingError(Exception):
    pass


def money(value: Decimal) -> Decimal:
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def line_values(item: LineItemInput) -> tuple[Decimal, Decimal, Decimal]:
    subtotal = money(item.quantity * item.unit_price)
    tax = money(subtotal * item.tax_rate / Decimal("100"))
    return subtotal, tax, money(subtotal + tax)


def next_number(db: Session, model: type[Quote] | type[Invoice], prefix: str) -> str:
    year = date.today().year
    count = db.scalar(
        select(func.count()).select_from(model).where(model.number.like(f"{prefix}-{year}-%"))
    ) or 0
    return f"{prefix}-{year}-{count + 1:04d}"


def apply_quote_items(quote: Quote, items: list[LineItemInput]) -> None:
    quote.items.clear()
    subtotal = Decimal("0.00")
    tax_total = Decimal("0.00")
    for position, payload in enumerate(items, start=1):
        line_subtotal, line_tax, line_total = line_values(payload)
        quote.items.append(
            QuoteItem(
                description=payload.description.strip(),
                quantity=payload.quantity,
                unit_price=payload.unit_price,
                tax_rate=payload.tax_rate,
                line_subtotal=line_subtotal,
                line_tax=line_tax,
                line_total=line_total,
                position=position,
            )
        )
        subtotal += line_subtotal
        tax_total += line_tax
    quote.subtotal = money(subtotal)
    quote.tax_total = money(tax_total)
    quote.total = money(subtotal + tax_total)


def apply_invoice_items(invoice: Invoice, items: list[LineItemInput]) -> None:
    invoice.items.clear()
    subtotal = Decimal("0.00")
    tax_total = Decimal("0.00")
    for position, payload in enumerate(items, start=1):
        line_subtotal, line_tax, line_total = line_values(payload)
        invoice.items.append(
            InvoiceItem(
                description=payload.description.strip(),
                quantity=payload.quantity,
                unit_price=payload.unit_price,
                tax_rate=payload.tax_rate,
                line_subtotal=line_subtotal,
                line_tax=line_tax,
                line_total=line_total,
                position=position,
            )
        )
        subtotal += line_subtotal
        tax_total += line_tax
    invoice.subtotal = money(subtotal)
    invoice.tax_total = money(tax_total)
    invoice.total = money(subtotal + tax_total)


def quote_statement() -> Select[tuple[Quote]]:
    return select(Quote).options(
        selectinload(Quote.client),
        selectinload(Quote.created_by),
        selectinload(Quote.items),
        selectinload(Quote.invoice),
    )


def invoice_statement() -> Select[tuple[Invoice]]:
    return select(Invoice).options(
        selectinload(Invoice.client),
        selectinload(Invoice.created_by),
        selectinload(Invoice.items),
        selectinload(Invoice.payments).selectinload(Payment.recorded_by),
    )


def list_quotes(
    db: Session,
    *,
    status: QuoteStatus | None = None,
    client_id: str | None = None,
) -> list[Quote]:
    statement = quote_statement()
    if status is not None:
        statement = statement.where(Quote.status == status.value)
    if client_id is not None:
        statement = statement.where(Quote.client_id == client_id)
    statement = statement.order_by(Quote.issue_date.desc(), Quote.number.desc())
    return list(db.scalars(statement).unique().all())


def get_quote(db: Session, quote_id: str) -> Quote | None:
    statement = quote_statement().where(Quote.id == quote_id)
    return db.scalar(statement)


def create_quote(db: Session, payload: QuoteCreate, *, created_by_id: str) -> Quote:
    quote = Quote(
        number=next_number(db, Quote, "PRE"),
        client_id=payload.client_id,
        work_order_id=payload.work_order_id,
        created_by_id=created_by_id,
        issue_date=payload.issue_date,
        valid_until=payload.valid_until,
        notes=payload.notes.strip() if payload.notes else None,
    )
    apply_quote_items(quote, payload.items)
    db.add(quote)
    db.commit()
    return get_quote(db, quote.id) or quote


def update_quote(db: Session, quote: Quote, payload: QuoteUpdate) -> Quote:
    changes = payload.model_dump(exclude_unset=True)
    if "status" in changes and payload.status is not None:
        quote.status = payload.status.value
    if "valid_until" in changes:
        quote.valid_until = payload.valid_until
    if "notes" in changes:
        quote.notes = payload.notes.strip() if payload.notes else None
    if "items" in changes and payload.items is not None:
        apply_quote_items(quote, payload.items)
    db.commit()
    return get_quote(db, quote.id) or quote


def list_invoices(
    db: Session,
    *,
    status: InvoiceStatus | None = None,
    client_id: str | None = None,
) -> list[Invoice]:
    statement = invoice_statement()
    if status is not None:
        statement = statement.where(Invoice.status == status.value)
    if client_id is not None:
        statement = statement.where(Invoice.client_id == client_id)
    statement = statement.order_by(Invoice.issue_date.desc(), Invoice.number.desc())
    return list(db.scalars(statement).unique().all())


def get_invoice(db: Session, invoice_id: str) -> Invoice | None:
    statement = invoice_statement().where(Invoice.id == invoice_id)
    return db.scalar(statement)


def create_invoice(db: Session, payload: InvoiceCreate, *, created_by_id: str) -> Invoice:
    invoice = Invoice(
        number=next_number(db, Invoice, "FAC"),
        client_id=payload.client_id,
        work_order_id=payload.work_order_id,
        created_by_id=created_by_id,
        issue_date=payload.issue_date,
        due_date=payload.due_date,
        notes=payload.notes.strip() if payload.notes else None,
    )
    apply_invoice_items(invoice, payload.items)
    db.add(invoice)
    db.commit()
    return get_invoice(db, invoice.id) or invoice


def update_invoice(db: Session, invoice: Invoice, payload: InvoiceUpdate) -> Invoice:
    changes = payload.model_dump(exclude_unset=True)
    if "status" in changes and payload.status is not None:
        invoice.status = payload.status.value
    if "due_date" in changes:
        invoice.due_date = payload.due_date
    if "notes" in changes:
        invoice.notes = payload.notes.strip() if payload.notes else None
    db.commit()
    return get_invoice(db, invoice.id) or invoice


def convert_quote_to_invoice(
    db: Session,
    quote: Quote,
    *,
    created_by_id: str,
    due_date: date | None,
) -> Invoice:
    if quote.invoice is not None:
        raise QuoteAlreadyInvoicedError
    if quote.status != QuoteStatus.ACCEPTED.value:
        raise QuoteNotAcceptedError

    invoice = Invoice(
        number=next_number(db, Invoice, "FAC"),
        client_id=quote.client_id,
        work_order_id=quote.work_order_id,
        source_quote_id=quote.id,
        created_by_id=created_by_id,
        issue_date=date.today(),
        due_date=due_date,
        notes=quote.notes,
        subtotal=quote.subtotal,
        tax_total=quote.tax_total,
        total=quote.total,
    )
    for item in quote.items:
        invoice.items.append(
            InvoiceItem(
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                tax_rate=item.tax_rate,
                line_subtotal=item.line_subtotal,
                line_tax=item.line_tax,
                line_total=item.line_total,
                position=item.position,
            )
        )
    db.add(invoice)
    db.commit()
    return get_invoice(db, invoice.id) or invoice


def add_payment(
    db: Session,
    invoice: Invoice,
    payload: PaymentCreate,
    *,
    recorded_by_id: str,
) -> Invoice:
    pending = money(invoice.total - invoice.paid_total)
    if payload.amount > pending:
        raise PaymentExceedsPendingError

    payment = Payment(
        invoice_id=invoice.id,
        recorded_by_id=recorded_by_id,
        amount=money(payload.amount),
        method=payload.method.value,
        paid_at=payload.paid_at or datetime.now(UTC),
        reference=payload.reference.strip() if payload.reference else None,
        notes=payload.notes.strip() if payload.notes else None,
    )
    db.add(payment)
    invoice.paid_total = money(invoice.paid_total + payload.amount)
    invoice.status = (
        InvoiceStatus.PAID.value
        if invoice.paid_total >= invoice.total
        else InvoiceStatus.PARTIAL.value
    )
    db.commit()
    db.expire_all()
    return get_invoice(db, invoice.id) or invoice
