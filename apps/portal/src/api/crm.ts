import { apiRequest } from './client'
import type {
  CrmActivity,
  CrmActivityType,
  CrmSummary,
  Lead,
  LeadSource,
  LeadStatus,
  Opportunity,
  OpportunityStage,
  Quote,
} from './types'

export interface LeadInput {
  name: string
  company?: string
  phone?: string
  email?: string
  source: LeadSource
  status: LeadStatus
  owner_id?: string | null
  notes?: string
}

export interface OpportunityInput {
  title: string
  lead_id?: string | null
  client_id?: string | null
  owner_id?: string | null
  stage: OpportunityStage
  estimated_value: string
  probability: number
  expected_close?: string | null
  notes?: string
}

export interface CrmActivityInput {
  opportunity_id?: string | null
  lead_id?: string | null
  assigned_to_id?: string | null
  activity_type: CrmActivityType
  subject: string
  due_at?: string | null
  notes?: string
}

export function getCrmSummary(): Promise<CrmSummary> {
  return apiRequest<CrmSummary>('/crm/summary')
}

export function getLeads(): Promise<Lead[]> {
  return apiRequest<Lead[]>('/crm/leads')
}

export function createLead(payload: LeadInput): Promise<Lead> {
  return apiRequest<Lead>('/crm/leads', { method: 'POST', body: JSON.stringify(payload) })
}

export function updateLead(leadId: string, payload: Partial<LeadInput>): Promise<Lead> {
  return apiRequest<Lead>(`/crm/leads/${leadId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function convertLeadToClient(leadId: string): Promise<unknown> {
  return apiRequest(`/crm/leads/${leadId}/convert-to-client`, { method: 'POST' })
}

export function getOpportunities(): Promise<Opportunity[]> {
  return apiRequest<Opportunity[]>('/crm/opportunities')
}

export function createOpportunity(payload: OpportunityInput): Promise<Opportunity> {
  return apiRequest<Opportunity>('/crm/opportunities', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateOpportunity(
  opportunityId: string,
  payload: Partial<OpportunityInput> & { change_source?: string },
): Promise<Opportunity> {
  return apiRequest<Opportunity>(`/crm/opportunities/${opportunityId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function convertOpportunityToQuote(opportunityId: string): Promise<Quote> {
  return apiRequest<Quote>(`/crm/opportunities/${opportunityId}/convert-to-quote`, {
    method: 'POST',
    body: JSON.stringify({ tax_rate: '7.00' }),
  })
}

export function getCrmActivities(): Promise<CrmActivity[]> {
  return apiRequest<CrmActivity[]>('/crm/activities')
}

export function createCrmActivity(payload: CrmActivityInput): Promise<CrmActivity> {
  return apiRequest<CrmActivity>('/crm/activities', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateCrmActivity(
  activityId: string,
  payload: Partial<CrmActivityInput> & { completed?: boolean },
): Promise<CrmActivity> {
  return apiRequest<CrmActivity>(`/crm/activities/${activityId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}
