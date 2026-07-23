import { apiRequest } from './client'
import type { TokenResponse, User } from './types'

export function loginRequest(email: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams({
    username: email,
    password,
  })

  return apiRequest<TokenResponse>('/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body,
  })
}

export function getCurrentUser(): Promise<User> {
  return apiRequest<User>('/users/me')
}
