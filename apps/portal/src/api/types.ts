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
  active_suppliers: number
  active_catalog_items: number
  low_stock_items: number
  inventory_value: string
  pending_expenses: number
  expenses_total: string
  material_costs: string
  gross_margin: string
  realized_margin: string
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

export type ExpenseCategory =
  | 'materials'
  | 'subcontracting'
  | 'travel'
  | 'tools'
  | 'services'
  | 'taxes'
  | 'other'

export type ExpenseStatus = 'pending' | 'paid' | 'cancelled'

export interface Supplier {
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

export interface SupplierReference {
  id: string
  name: string
}

export interface WorkOrderReference {
  id: string
  title: string
  client_name: string
}

export interface Expense {
  id: string
  supplier: SupplierReference | null
  work_order: WorkOrderReference | null
  created_by: UserReference
  description: string
  category: ExpenseCategory
  status: ExpenseStatus
  expense_date: string
  subtotal: string
  tax_rate: string
  tax_total: string
  total: string
  reference: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface WorkOrderProfitability {
  id: string
  title: string
  client_name: string
  invoiced_revenue: string
  collected_revenue: string
  expenses_total: string
  gross_margin: string
  realized_margin: string
}

export interface ClientProfitability {
  id: string
  name: string
  invoiced_revenue: string
  collected_revenue: string
  expenses_total: string
  gross_margin: string
  realized_margin: string
}

export interface ProfitabilitySummary {
  invoiced_revenue: string
  collected_revenue: string
  expenses_total: string
  material_costs: string
  gross_margin: string
  realized_margin: string
  gross_margin_percent: string
  work_orders: WorkOrderProfitability[]
  clients: ClientProfitability[]
}

export type StockMovementType = 'entry' | 'exit' | 'assignment' | 'return' | 'adjustment'

export interface CatalogItem {
  id: string
  legacy_id: number | null
  code: string
  family: string
  description: string
  unit: string
  purchase_price: string
  sale_price: string
  labor_hours: string
  supplier_name: string | null
  tax_rate: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Warehouse {
  id: string
  name: string
  kind: string
  location: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface InventoryLevel {
  id: string
  catalog_item: {
    id: string
    code: string
    description: string
    unit: string
    purchase_price: string
  }
  warehouse: {
    id: string
    name: string
  }
  stock: string
  reserved: string
  available: string
  min_stock: string
  low_stock: boolean
  shelf: string | null
  barcode: string | null
  inventory_value: string
  updated_at: string
}

export interface StockMovement {
  id: string
  catalog_item: {
    id: string
    code: string
    description: string
    unit: string
    purchase_price: string
  }
  warehouse: {
    id: string
    name: string
  }
  work_order_id: string | null
  created_by: UserReference
  movement_type: StockMovementType
  quantity: string
  unit_cost: string
  total_cost: string
  reference: string | null
  notes: string | null
  movement_date: string
  created_at: string
}

export interface LegacyTariffImportResult {
  source_file: string
  created: number
  updated: number
  skipped: number
  total_rows: number
  warehouse_created: boolean
}
