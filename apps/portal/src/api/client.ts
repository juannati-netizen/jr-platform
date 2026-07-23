import { tokenStore } from '../auth/token-store'

const API_BASE_URL = import.meta.env.VITE_API_URL ?? '/api/v1'

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers)
  const token = tokenStore.get()

  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  if (options.body && !(options.body instanceof URLSearchParams) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  })

  const payload = await readPayload(response)

  if (!response.ok) {
    const detail = extractErrorDetail(payload)
    throw new ApiError(detail, response.status)
  }

  return payload as T
}

async function readPayload(response: Response): Promise<unknown> {
  const contentType = response.headers.get('content-type') ?? ''
  if (contentType.includes('application/json')) {
    return response.json()
  }
  return response.text()
}

function extractErrorDetail(payload: unknown): string {
  if (
    typeof payload === 'object' &&
    payload !== null &&
    'detail' in payload &&
    typeof payload.detail === 'string'
  ) {
    return payload.detail
  }
  return 'No se pudo completar la operación'
}
