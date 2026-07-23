import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren,
} from 'react'

import { getCurrentUser, loginRequest } from '../api/auth'
import type { User } from '../api/types'
import { tokenStore } from './token-store'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    const nextUser = await getCurrentUser()
    setUser(nextUser)
  }, [])

  useEffect(() => {
    const restoreSession = async () => {
      if (!tokenStore.get()) {
        setIsLoading(false)
        return
      }

      try {
        await refreshUser()
      } catch {
        tokenStore.clear()
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }

    void restoreSession()
  }, [refreshUser])

  const login = useCallback(
    async (email: string, password: string) => {
      const token = await loginRequest(email, password)
      tokenStore.set(token.access_token)
      try {
        await refreshUser()
      } catch (error) {
        tokenStore.clear()
        throw error
      }
    },
    [refreshUser],
  )

  const logout = useCallback(() => {
    tokenStore.clear()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, isLoading, login, logout, refreshUser }),
    [isLoading, login, logout, refreshUser, user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth debe utilizarse dentro de AuthProvider')
  }
  return context
}
