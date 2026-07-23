import type { WorkOrderPriority, WorkOrderStatus } from '../api/types'

export const workOrderStatusOptions: Array<{ value: WorkOrderStatus; label: string }> = [
  { value: 'draft', label: 'Borrador' },
  { value: 'planned', label: 'Planificado' },
  { value: 'in_progress', label: 'En curso' },
  { value: 'blocked', label: 'Bloqueado' },
  { value: 'completed', label: 'Completado' },
  { value: 'cancelled', label: 'Cancelado' },
]

export const workOrderPriorityOptions: Array<{ value: WorkOrderPriority; label: string }> = [
  { value: 'low', label: 'Baja' },
  { value: 'normal', label: 'Normal' },
  { value: 'high', label: 'Alta' },
  { value: 'urgent', label: 'Urgente' },
]

export function workOrderStatusLabel(status: WorkOrderStatus): string {
  return workOrderStatusOptions.find((item) => item.value === status)?.label ?? status
}

export function workOrderPriorityLabel(priority: WorkOrderPriority): string {
  return workOrderPriorityOptions.find((item) => item.value === priority)?.label ?? priority
}

type StatusChipColor = 'default' | 'primary' | 'warning' | 'error' | 'success' | 'info'

export function statusColor(status: WorkOrderStatus): StatusChipColor {
  const colors: Record<WorkOrderStatus, StatusChipColor> = {
    draft: 'default',
    planned: 'info',
    in_progress: 'primary',
    blocked: 'warning',
    completed: 'success',
    cancelled: 'error',
  }
  return colors[status]
}
