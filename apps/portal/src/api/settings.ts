import { apiRequest } from './client'

export interface CompanyProfile {
  id: string
  legal_name: string
  trade_name: string | null
  tax_id: string
  legal_form: string | null
  tax_regime: string | null
  address: string | null
  postal_code: string | null
  city: string | null
  province: string | null
  country: string
  email: string | null
  phone: string | null
  website: string | null
  iban: string | null
  invoice_prefix: string
  quote_prefix: string
  currency: string
  timezone: string
  logo_data_url: string | null
  brand_color: string
  document_footer: string | null
  created_at: string
  updated_at: string
}


export interface CompanyPublicProfile {
  legal_name: string
  trade_name: string | null
  tax_id: string
  address: string | null
  postal_code: string | null
  city: string | null
  province: string | null
  country: string
  email: string | null
  phone: string | null
  website: string | null
  logo_data_url: string | null
  brand_color: string
  document_footer: string | null
}

export type CompanyProfilePayload = Omit<CompanyProfile, 'id' | 'created_at' | 'updated_at'>

export interface UserSummary {
  id: string
  full_name: string
  email: string
}

export interface FiscalYear {
  id: string
  year: number
  start_date: string
  end_date: string
  status: 'open' | 'closed'
  opened_at: string
  opened_by: UserSummary | null
  closed_at: string | null
  closed_by: UserSummary | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface FiscalYearPayload {
  year: number
  start_date: string
  end_date: string
  notes: string | null
}

export type VerifactuMode = 'disabled' | 'preparation' | 'test'

export interface VerifactuConfiguration {
  id: string
  mode: VerifactuMode
  system_name: string
  system_version: string
  producer_name: string | null
  producer_tax_id: string | null
  qr_enabled: boolean
  hash_chain_enabled: boolean
  event_log_enabled: boolean
  aeat_transmission_enabled: boolean
  responsible_declaration_signed: boolean
  certificate_alias: string | null
  notes: string | null
  reviewed_at: string | null
  created_at: string
  updated_at: string
}

export type VerifactuPayload = Omit<
  VerifactuConfiguration,
  'id' | 'reviewed_at' | 'created_at' | 'updated_at'
>

export interface ReadinessItem {
  key: string
  label: string
  completed: boolean
  detail: string
}

export interface VerifactuReadiness {
  status: string
  completed: number
  total: number
  items: ReadinessItem[]
  transmission_active: boolean
  legal_notice: string
}

export type AiProvider = 'disabled' | 'openai' | 'azure_openai' | 'local' | 'custom'

export interface AiConfiguration {
  id: string
  enabled: boolean
  provider: AiProvider
  model: string | null
  assistant_name: string
  system_prompt: string | null
  allow_customer_data: boolean
  allow_financial_data: boolean
  allow_document_content: boolean
  human_review_required: boolean
  retention_days: number
  notes: string | null
  api_key_configured: boolean
  base_url_configured: boolean
  created_at: string
  updated_at: string
}

export type AiConfigurationPayload = Omit<
  AiConfiguration,
  'id' | 'api_key_configured' | 'base_url_configured' | 'created_at' | 'updated_at'
>

export interface AiReadiness {
  status: string
  ready: boolean
  items: ReadinessItem[]
  security_notice: string
}

export interface ConfigurationEvent {
  id: string
  category: string
  action: string
  summary: string
  actor: UserSummary | null
  created_at: string
}

export const getCompanyProfile = () => apiRequest<CompanyProfile>('/settings/company')

export const getPublicCompanyProfile = () =>
  apiRequest<CompanyPublicProfile>('/settings/company/public')

export const updateCompanyProfile = (payload: CompanyProfilePayload) =>
  apiRequest<CompanyProfile>('/settings/company', {
    method: 'PUT',
    body: JSON.stringify(payload),
  })

export const getFiscalYears = () => apiRequest<FiscalYear[]>('/settings/fiscal-years')

export const createFiscalYear = (payload: FiscalYearPayload) =>
  apiRequest<FiscalYear>('/settings/fiscal-years', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const openFiscalYear = (id: string) =>
  apiRequest<FiscalYear>(`/settings/fiscal-years/${id}/open`, { method: 'POST' })

export const closeFiscalYear = (id: string) =>
  apiRequest<FiscalYear>(`/settings/fiscal-years/${id}/close`, { method: 'POST' })

export const getVerifactuConfiguration = () =>
  apiRequest<VerifactuConfiguration>('/settings/verifactu')

export const updateVerifactuConfiguration = (payload: VerifactuPayload) =>
  apiRequest<VerifactuConfiguration>('/settings/verifactu', {
    method: 'PUT',
    body: JSON.stringify(payload),
  })

export const getVerifactuReadiness = () =>
  apiRequest<VerifactuReadiness>('/settings/verifactu/readiness')

export const getAiConfiguration = () => apiRequest<AiConfiguration>('/settings/ai')

export const updateAiConfiguration = (payload: AiConfigurationPayload) =>
  apiRequest<AiConfiguration>('/settings/ai', {
    method: 'PUT',
    body: JSON.stringify(payload),
  })

export const getAiReadiness = () => apiRequest<AiReadiness>('/settings/ai/readiness')

export const getConfigurationEvents = () =>
  apiRequest<ConfigurationEvent[]>('/settings/events?limit=100')
