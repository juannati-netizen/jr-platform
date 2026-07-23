from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.models.client import Client
from apps.models.crm import Project, ProjectStatus
from apps.models.finance import Invoice, InvoiceStatus, Quote, QuoteStatus
from apps.models.inventory import CatalogItem, InventoryLevel
from apps.models.procurement import Expense, ExpenseStatus, Supplier
from apps.models.work_order import WorkOrder, WorkOrderStatus
from apps.repositories.crm import get_crm_summary
from apps.repositories.procurement import get_profitability_summary
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

    active_suppliers = (
        db.scalar(select(func.count()).select_from(Supplier).where(Supplier.is_active.is_(True)))
        or 0
    )
    pending_expenses = (
        db.scalar(
            select(func.count())
            .select_from(Expense)
            .where(Expense.status == ExpenseStatus.PENDING.value)
        )
        or 0
    )
    active_catalog_items = (
        db.scalar(
            select(func.count()).select_from(CatalogItem).where(CatalogItem.is_active.is_(True))
        )
        or 0
    )
    low_stock_items = (
        db.scalar(
            select(func.count())
            .select_from(InventoryLevel)
            .where(
                InventoryLevel.min_stock > 0,
                InventoryLevel.stock - InventoryLevel.reserved <= InventoryLevel.min_stock,
            )
        )
        or 0
    )
    inventory_value = decimal_scalar(
        db.scalar(
            select(func.sum(InventoryLevel.stock * CatalogItem.purchase_price))
            .select_from(InventoryLevel)
            .join(CatalogItem, CatalogItem.id == InventoryLevel.catalog_item_id)
        )
    )
    profitability = get_profitability_summary(db)
    crm = get_crm_summary(db)
    active_projects = (
        db.scalar(
            select(func.count())
            .select_from(Project)
            .where(
                Project.status.in_(
                    (
                        ProjectStatus.PLANNED.value,
                        ProjectStatus.ACTIVE.value,
                        ProjectStatus.ON_HOLD.value,
                    )
                )
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
        active_suppliers=active_suppliers,
        active_catalog_items=active_catalog_items,
        low_stock_items=low_stock_items,
        inventory_value=inventory_value,
        pending_expenses=pending_expenses,
        expenses_total=profitability.expenses_total,
        material_costs=profitability.material_costs,
        gross_margin=profitability.gross_margin,
        realized_margin=profitability.realized_margin,
        total_leads=crm.total_leads,
        open_opportunities=crm.open_opportunities,
        pipeline_value=crm.pipeline_value,
        weighted_pipeline=crm.weighted_pipeline,
        pending_crm_activities=crm.pending_activities,
        active_projects=active_projects,
    )
