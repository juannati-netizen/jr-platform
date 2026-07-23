import { apiRequest } from './client'
import type { User, UserRole } from './types'

export function getUsers(): Promise<User[]> {
  return apiRequest<User[]>('/users')
}

export function updateUserRole(userId: string, role: UserRole): Promise<User> {
  return apiRequest<User>(`/users/${userId}/role`, {
    method: 'PATCH',
    body: JSON.stringify({ role }),
  })
}
