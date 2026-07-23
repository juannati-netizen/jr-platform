import { apiRequest } from './client'
import type { Client } from './types'

export interface ClientInput {
  name: string
  tax_id?: string
  email?: string
  phone?: string
  address?: string
  notes?: string
}

export function getClients(activeOnly = false): Promise<Client[]> {
  return apiRequest<Client[]>(`/clients?active_only=${activeOnly}`)
}

export function createClient(payload: ClientInput): Promise<Client> {
  return apiRequest<Client>('/clients', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateClient(
  clientId: string,
  payload: Partial<ClientInput> & { is_active?: boolean },
): Promise<Client> {
  return apiRequest<Client>(`/clients/${clientId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}
