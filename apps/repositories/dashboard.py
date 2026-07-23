from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.models.client import Client
from apps.models.finance import Invoice, InvoiceStatus, Quote, QuoteStatus
from apps.models.work_order import WorkOrder, WorkOrderStatus
from apps.schemas.dashboard import DashboardSummary, StatusMetric

OPEN_STATUSES = (
    WorkOrderStatus.DRAFT.value,
    WorkOrderStatus.PLANNED.value,
    WorkOrderStatus.IN_PROGRESS.value,
    WorkOrderStatus.BLOCKED.value,
)


def decimal_scalar(value: Decimal | None) -> Decimal:
    return value or Decimal("0.00")


def get_dashboard_summary(db: Session) -> DashboardSummary:
    total_clients = db.scalar(select(func.count()).select_from(Client)) or 0
    active_clients = (
        db.scalar(select(func.count()).select_from(Client).where(Client.is_active.is_(True))) or 0
    )
    open_work_orders = (
        db.scalar(
            select(func.count()).select_from(WorkOrder).where(WorkOrder.status.in_(OPEN_STATUSES))
        )
        or 0
    )
    completed_work_orders = (
        db.scalar(
            select(func.count())
            .select_from(WorkOrder)
            .where(WorkOrder.status == WorkOrderStatus.COMPLETED.value)
        )
        or 0
    )
    overdue_work_orders = (
        db.scalar(
            select(func.count())
            .select_from(WorkOrder)
            .where(
                WorkOrder.scheduled_for.is_not(None),
                WorkOrder.scheduled_for < datetime.now(UTC),
                WorkOrder.status.in_(OPEN_STATUSES),
            )
        )
        or 0
    )
    unassigned_work_orders = (
        db.scalar(
            select(func.count())
            .select_from(WorkOrder)
            .where(WorkOrder.assignee_id.is_(None), WorkOrder.status.in_(OPEN_STATUSES))
        )
        or 0
    )

    status_rows = db.execute(
        select(WorkOrder.status, func.count(WorkOrder.id)).group_by(WorkOrder.status)
    ).all()
    counts = {str(status): int(count) for status, count in status_rows}
    status_breakdown = [
        StatusMetric(status=status, count=counts.get(status.value, 0)) for status in WorkOrderStatus
    ]

    draft_quotes = (
        db.scalar(
            select(func.count()).select_from(Quote).where(Quote.status == QuoteStatus.DRAFT.value)
        )
        or 0
    )
    accepted_quotes = (
        db.scalar(
            select(func.count())
            .select_from(Quote)
            .where(Quote.status == QuoteStatus.ACCEPTED.value)
        )
        or 0
    )
    quoted_total = decimal_scalar(
        db.scalar(
            select(func.sum(Quote.total)).where(
                Quote.status.in_((QuoteStatus.SENT.value, QuoteStatus.ACCEPTED.value))
            )
        )
    )
    invoiced_total = decimal_scalar(
        db.scalar(
            select(func.sum(Invoice.total)).where(Invoice.status != InvoiceStatus.CANCELLED.value)
        )
    )
    collected_total = decimal_scalar(
        db.scalar(
            select(func.sum(Invoice.paid_total)).where(
                Invoice.status != InvoiceStatus.CANCELLED.value
            )
        )
    )
    pending_total = max(invoiced_total - collected_total, Decimal("0.00"))
    overdue_invoices = (
        db.scalar(
            select(func.count())
            .select_from(Invoice)
            .where(
                Invoice.due_date.is_not(None),
                Invoice.due_date < date.today(),
                Invoice.status.in_((InvoiceStatus.ISSUED.value, InvoiceStatus.PARTIAL.value)),
            )
        )
        or 0
    )

    return DashboardSummary(
        active_clients=active_clients,
        total_clients=total_clients,
        open_work_orders=open_work_orders,
        completed_work_orders=completed_work_orders,
        overdue_work_orders=overdue_work_orders,
        unassigned_work_orders=unassigned_work_orders,
        status_breakdown=status_breakdown,
        draft_quotes=draft_quotes,
        accepted_quotes=accepted_quotes,
        quoted_total=quoted_total,
        invoiced_total=invoiced_total,
        collected_total=collected_total,
        pending_total=pending_total,
        overdue_invoices=overdue_invoices,
    )
