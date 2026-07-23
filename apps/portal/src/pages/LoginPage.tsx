import LockOutlinedIcon from '@mui/icons-material/LockOutlined'
import {
  Alert,
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { Navigate, useNavigate } from '@tanstack/react-router'
import { useState, type FormEvent } from 'react'

import { ApiError } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import { LoadingScreen } from '../components/LoadingScreen'

export function LoginPage() {
  const { user, isLoading, login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('admin@jrplatform.com')
  const [password, setPassword] = useState('ChangeMe123!')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (isLoading) {
    return <LoadingScreen />
  }

  if (user) {
    return <Navigate to="/" />
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      await login(email, password)
      await navigate({ to: '/' })
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : 'No se pudo iniciar sesión')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        p: 2,
        background:
          'radial-gradient(circle at 10% 20%, rgba(20, 184, 166, 0.24), transparent 35%), linear-gradient(135deg, #0f172a 0%, #134e4a 55%, #1f2937 100%)',
      }}
    >
      <Card sx={{ width: '100%', maxWidth: 440, overflow: 'visible' }}>
        <CardContent sx={{ p: { xs: 3, sm: 5 } }}>
          <Stack alignItems="center" spacing={1.5} sx={{ mb: 4 }}>
            <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
              <LockOutlinedIcon />
            </Avatar>
            <Typography variant="h4" textAlign="center">
              JR Platform
            </Typography>
            <Typography color="text.secondary" textAlign="center">
              Accede al portal operativo de tu organización
            </Typography>
          </Stack>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <Stack spacing={2.25}>
              <TextField
                label="Correo electrónico"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="username"
                required
                fullWidth
              />
              <TextField
                label="Contraseña"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                required
                fullWidth
              />
              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={isSubmitting}
                startIcon={isSubmitting ? <CircularProgress size={18} color="inherit" /> : undefined}
              >
                {isSubmitting ? 'Entrando…' : 'Iniciar sesión'}
              </Button>
            </Stack>
          </Box>

          <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 3 }}>
            Las credenciales precargadas son solo para el entorno local. Cámbialas antes de publicar.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  )
}
