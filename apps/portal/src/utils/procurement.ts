import type { ExpenseCategory, ExpenseStatus } from '../api/types'

export const expenseCategoryOptions: Array<{ value: ExpenseCategory; label: string }> = [
  { value: 'materials', label: 'Materiales' },
  { value: 'subcontracting', label: 'Subcontratación' },
  { value: 'travel', label: 'Desplazamientos' },
  { value: 'tools', label: 'Herramientas' },
  { value: 'services', label: 'Servicios' },
  { value: 'taxes', label: 'Impuestos y tasas' },
  { value: 'other', label: 'Otros' },
]

export const expenseStatusOptions: Array<{ value: ExpenseStatus; label: string }> = [
  { value: 'pending', label: 'Pendiente' },
  { value: 'paid', label: 'Pagado' },
  { value: 'cancelled', label: 'Cancelado' },
]

export function expenseCategoryLabel(category: ExpenseCategory): string {
  return expenseCategoryOptions.find((item) => item.value === category)?.label ?? category
}

export function expenseStatusLabel(status: ExpenseStatus): string {
  return expenseStatusOptions.find((item) => item.value === status)?.label ?? status
}

export function expenseStatusColor(
  status: ExpenseStatus,
): 'warning' | 'success' | 'default' {
  if (status === 'paid') {
    return 'success'
  }
  if (status === 'pending') {
    return 'warning'
  }
  return 'default'
}
