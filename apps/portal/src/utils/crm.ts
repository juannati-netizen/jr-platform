import type { CrmActivityType, LeadSource, LeadStatus, OpportunityStage, ProjectStatus } from '../api/types'

export const opportunityStages: Array<{ value: OpportunityStage; label: string }> = [
  { value: 'prospecting', label: 'Prospección' },
  { value: 'qualification', label: 'Cualificación' },
  { value: 'proposal', label: 'Propuesta' },
  { value: 'negotiation', label: 'Negociación' },
  { value: 'won', label: 'Ganada' },
  { value: 'lost', label: 'Perdida' },
]

export const leadSources: Array<{ value: LeadSource; label: string }> = [
  { value: 'web', label: 'Web' },
  { value: 'referral', label: 'Recomendación' },
  { value: 'campaign', label: 'Campaña' },
  { value: 'call', label: 'Llamada' },
  { value: 'event', label: 'Evento' },
  { value: 'other', label: 'Otro' },
]

export const leadStatuses: Array<{ value: LeadStatus; label: string }> = [
  { value: 'new', label: 'Nuevo' },
  { value: 'contacted', label: 'Contactado' },
  { value: 'qualified', label: 'Cualificado' },
  { value: 'converted', label: 'Convertido' },
  { value: 'discarded', label: 'Descartado' },
]

export const activityTypes: Array<{ value: CrmActivityType; label: string }> = [
  { value: 'task', label: 'Tarea' },
  { value: 'call', label: 'Llamada' },
  { value: 'email', label: 'Correo' },
  { value: 'meeting', label: 'Reunión' },
  { value: 'follow_up', label: 'Seguimiento' },
]

export const projectStatuses: Array<{ value: ProjectStatus; label: string }> = [
  { value: 'planned', label: 'Planificada' },
  { value: 'active', label: 'Activa' },
  { value: 'on_hold', label: 'En pausa' },
  { value: 'completed', label: 'Completada' },
  { value: 'cancelled', label: 'Cancelada' },
]

export function opportunityStageLabel(value: OpportunityStage): string {
  return opportunityStages.find((item) => item.value === value)?.label ?? value
}
