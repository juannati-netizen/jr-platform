from pydantic import BaseModel

from apps.models.work_order import WorkOrderStatus


class StatusMetric(BaseModel):
    status: WorkOrderStatus
    count: int


class DashboardSummary(BaseModel):
    active_clients: int
    total_clients: int
    open_work_orders: int
    completed_work_orders: int
    overdue_work_orders: int
    unassigned_work_orders: int
    status_breakdown: list[StatusMetric]
