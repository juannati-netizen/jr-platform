from decimal import Decimal

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
    draft_quotes: int
    accepted_quotes: int
    quoted_total: Decimal
    invoiced_total: Decimal
    collected_total: Decimal
    pending_total: Decimal
    overdue_invoices: int
    active_suppliers: int
    pending_expenses: int
    expenses_total: Decimal
    material_costs: Decimal
    gross_margin: Decimal
    realized_margin: Decimal
