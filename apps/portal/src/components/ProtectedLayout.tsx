import { Navigate } from '@tanstack/react-router'

import { useAuth } from '../auth/AuthContext'
import { AppShell } from './AppShell'
import { LoadingScreen } from './LoadingScreen'

export function ProtectedLayout() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return <LoadingScreen />
  }

  if (!user) {
    return <Navigate to="/login" />
  }

  return <AppShell />
}
