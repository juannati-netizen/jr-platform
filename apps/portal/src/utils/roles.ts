import type { UserRole } from '../api/types'

export function roleLabel(role: UserRole | undefined): string {
  if (role === 'admin') {
    return 'Administrador'
  }
  if (role === 'user') {
    return 'Usuario'
  }
  return 'Sin rol'
}
