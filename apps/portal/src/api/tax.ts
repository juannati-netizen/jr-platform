import { apiRequest, authenticatedDownload } from './client'

export type TaxSystem = 'igic' | 'iva'
export type TaxPeriodStatus = 'open' | 'closed'
export type TaxAdjustmentDirection = 'output' | 'input'

export interface TaxConfiguration {
  id: string
  tax_system: TaxSystem
  filing_model: '420'
  filing_frequency: 'quarterly'
  monthly_tracking_enabled: boolean
  default_tax_rate: string
  notes: string | null
  created_at: string
  updated_at: string
}

export type TaxConfigurationPayload = Omit<TaxConfiguration, 'id' | 'created_at' | 'updated_at'>

export interface TaxRateBreakdown {
  tax_rate: string
  taxable_base: string
  tax_amount: string
}

export interface TaxAdjustment {
  id: string
  year: number
  month: number
  direction: TaxAdjustmentDirection
  amount: string
  description: string
  created_at: string
}

export interface TaxMonthSummary {
  year: number
  month: number
  month_label: string
  status: TaxPeriodStatus
  output_base: string
  output_tax: string
  input_base: string
  input_tax: string
  output_adjustments: string
  input_adjustments: string
  result: string
  result_type: 'to_pay' | 'to_compensate' | 'zero'
  output_breakdown: TaxRateBreakdown[]
  input_breakdown: TaxRateBreakdown[]
  adjustments: TaxAdjustment[]
  closed_at: string | null
  legal_notice: string
}

export interface TaxQuarterSummary {
  year: number
  quarter: number
  period_label: string
  months: TaxMonthSummary[]
  output_base: string
  output_tax: string
  input_base: string
  input_tax: string
  output_adjustments: string
  input_adjustments: string
  result: string
  result_type: 'to_pay' | 'to_compensate' | 'zero'
  model: string
  filing_window: string
  all_months_closed: boolean
  legal_notice: string
}

export interface TaxAdjustmentPayload {
  year: number
  month: number
  direction: TaxAdjustmentDirection
  amount: string
  description: string
}

export const getTaxConfiguration = () =>
  apiRequest<TaxConfiguration>('/tax/configuration')

export const updateTaxConfiguration = (payload: TaxConfigurationPayload) =>
  apiRequest<TaxConfiguration>('/tax/configuration', {
    method: 'PUT',
    body: JSON.stringify(payload),
  })

export const getTaxMonths = (year: number) =>
  apiRequest<TaxMonthSummary[]>(`/tax/months?year=${year}`)

export const getModel420 = (year: number, quarter: number) =>
  apiRequest<TaxQuarterSummary>(`/tax/model-420/${year}/${quarter}`)

export const closeTaxMonth = (year: number, month: number, notes: string | null = null) =>
  apiRequest<TaxMonthSummary>(`/tax/months/${year}/${month}/close`, {
    method: 'POST',
    body: JSON.stringify({ notes }),
  })

export const reopenTaxMonth = (year: number, month: number) =>
  apiRequest<TaxMonthSummary>(`/tax/months/${year}/${month}/open`, { method: 'POST' })

export const createTaxAdjustment = (payload: TaxAdjustmentPayload) =>
  apiRequest<TaxAdjustment>('/tax/adjustments', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const downloadModel420Csv = (year: number, quarter: number) =>
  authenticatedDownload(
    `/tax/model-420/${year}/${quarter}/csv`,
    `modelo-420-${year}-T${quarter}-borrador.csv`,
  )
