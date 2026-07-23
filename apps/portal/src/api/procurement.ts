import { apiRequest } from './client'
import type {
  Expense,
  ExpenseCategory,
  ExpenseStatus,
  ProfitabilitySummary,
  Supplier,
} from './types'

export interface SupplierInput {
  name: string
  tax_id?: string
  email?: string
  phone?: string
  address?: string
  notes?: string
}

export interface ExpenseInput {
  supplier_id?: string | null
  work_order_id?: string | null
  description: string
  category: ExpenseCategory
  status: ExpenseStatus
  expense_date: string
  subtotal: string
  tax_rate: string
  reference?: string
  notes?: string
}

export function getSuppliers(activeOnly = false): Promise<Supplier[]> {
  return apiRequest<Supplier[]>(`/suppliers?active_only=${activeOnly}`)
}

export function createSupplier(payload: SupplierInput): Promise<Supplier> {
  return apiRequest<Supplier>('/suppliers', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateSupplier(
  supplierId: string,
  payload: Partial<SupplierInput> & { is_active?: boolean },
): Promise<Supplier> {
  return apiRequest<Supplier>(`/suppliers/${supplierId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function getExpenses(): Promise<Expense[]> {
  return apiRequest<Expense[]>('/expenses')
}

export function createExpense(payload: ExpenseInput): Promise<Expense> {
  return apiRequest<Expense>('/expenses', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateExpense(
  expenseId: string,
  payload: Partial<ExpenseInput>,
): Promise<Expense> {
  return apiRequest<Expense>(`/expenses/${expenseId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function getProfitabilitySummary(): Promise<ProfitabilitySummary> {
  return apiRequest<ProfitabilitySummary>('/profitability/summary')
}
