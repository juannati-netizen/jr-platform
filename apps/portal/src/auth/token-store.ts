const TOKEN_KEY = 'jr-platform.access-token'

export const tokenStore = {
  get(): string | null {
    return sessionStorage.getItem(TOKEN_KEY)
  },
  set(token: string): void {
    sessionStorage.setItem(TOKEN_KEY, token)
  },
  clear(): void {
    sessionStorage.removeItem(TOKEN_KEY)
  },
}
