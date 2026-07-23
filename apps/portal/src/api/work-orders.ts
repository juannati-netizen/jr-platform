import { apiRequest } from './client'
import type {
  WorkOrder,
  WorkOrderNote,
  WorkOrderPriority,
  WorkOrderStatus,
} from './types'

export interface WorkOrderInput {
  client_id: string
  title: string
  description?: string
  status: WorkOrderStatus
  priority: WorkOrderPriority
  assignee_id?: string | null
  scheduled_for?: string | null
}

export function getWorkOrders(): Promise<WorkOrder[]> {
  return apiRequest<WorkOrder[]>('/work-orders')
}

export function createWorkOrder(payload: WorkOrderInput): Promise<WorkOrder> {
  return apiRequest<WorkOrder>('/work-orders', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateWorkOrder(
  workOrderId: string,
  payload: Partial<WorkOrderInput>,
): Promise<WorkOrder> {
  return apiRequest<WorkOrder>(`/work-orders/${workOrderId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function getWorkOrderNotes(workOrderId: string): Promise<WorkOrderNote[]> {
  return apiRequest<WorkOrderNote[]>(`/work-orders/${workOrderId}/notes`)
}

export function addWorkOrderNote(workOrderId: string, content: string): Promise<WorkOrderNote> {
  return apiRequest<WorkOrderNote>(`/work-orders/${workOrderId}/notes`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  })
}
