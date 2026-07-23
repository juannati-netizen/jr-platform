from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.models.client import Client
from apps.models.work_order import WorkOrder, WorkOrderStatus
from apps.schemas.dashboard import DashboardSummary, StatusMetric

OPEN_STATUSES = (
    WorkOrderStatus.DRAFT.value,
    WorkOrderStatus.PLANNED.value,
    WorkOrderStatus.IN_PROGRESS.value,
    WorkOrderStatus.BLOCKED.value,
)


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

    return DashboardSummary(
        active_clients=active_clients,
        total_clients=total_clients,
        open_work_orders=open_work_orders,
        completed_work_orders=completed_work_orders,
        overdue_work_orders=overdue_work_orders,
        unassigned_work_orders=unassigned_work_orders,
        status_breakdown=status_breakdown,
    )
