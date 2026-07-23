export type UserRole = 'admin' | 'user'

export interface User {
  id: string
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface Client {
  id: string
  name: string
  tax_id: string | null
  email: string | null
  phone: string | null
  address: string | null
  notes: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export type WorkOrderStatus =
  | 'draft'
  | 'planned'
  | 'in_progress'
  | 'blocked'
  | 'completed'
  | 'cancelled'

export type WorkOrderPriority = 'low' | 'normal' | 'high' | 'urgent'

export interface UserReference {
  id: string
  full_name: string
  email: string
}

export interface ClientReference {
  id: string
  name: string
}

export interface WorkOrder {
  id: string
  title: string
  description: string | null
  status: WorkOrderStatus
  priority: WorkOrderPriority
  scheduled_for: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
  client: ClientReference
  assignee: UserReference | null
  created_by: UserReference
  notes_count: number
}

export interface WorkOrderNote {
  id: string
  content: string
  created_at: string
  author: UserReference
}

export interface StatusMetric {
  status: WorkOrderStatus
  count: number
}

export interface DashboardSummary {
  active_clients: number
  total_clients: number
  open_work_orders: number
  completed_work_orders: number
  overdue_work_orders: number
  unassigned_work_orders: number
  status_breakdown: StatusMetric[]
  draft_quotes: number
  accepted_quotes: number
  quoted_total: string
  invoiced_total: string
  collected_total: string
  pending_total: string
  overdue_invoices: number
}

export type QuoteStatus = 'draft' | 'sent' | 'accepted' | 'rejected' | 'expired'
export type InvoiceStatus = 'issued' | 'partial' | 'paid' | 'cancelled'
export type PaymentMethod = 'cash' | 'bank_transfer' | 'card' | 'direct_debit' | 'other'

export interface FinancialLineItem {
  id: string
  description: string
  quantity: string
  unit_price: string
  tax_rate: string
  position: number
  line_subtotal: string
  line_tax: string
  line_total: string
}

export interface Quote {
  id: string
  number: string
  client: ClientReference
  work_order_id: string | null
  created_by: UserReference
  status: QuoteStatus
  issue_date: string
  valid_until: string | null
  notes: string | null
  subtotal: string
  tax_total: string
  total: string
  items: FinancialLineItem[]
  invoice_id: string | null
  created_at: string
  updated_at: string
}

export interface Payment {
  id: string
  amount: string
  method: PaymentMethod
  paid_at: string
  reference: string | null
  notes: string | null
  recorded_by: UserReference
  created_at: string
}

export interface Invoice {
  id: string
  number: string
  client: ClientReference
  work_order_id: string | null
  source_quote_id: string | null
  created_by: UserReference
  status: InvoiceStatus
  issue_date: string
  due_date: string | null
  notes: string | null
  subtotal: string
  tax_total: string
  total: string
  paid_total: string
  pending_total: string
  items: FinancialLineItem[]
  payments: Payment[]
  created_at: string
  updated_at: string
}
