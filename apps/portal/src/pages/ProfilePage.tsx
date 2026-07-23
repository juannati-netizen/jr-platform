import {
  Avatar,
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  Stack,
  Typography,
} from '@mui/material'

import { useAuth } from '../auth/AuthContext'
import { roleLabel } from '../utils/roles'

export function ProfilePage() {
  const { user } = useAuth()

  if (!user) {
    return null
  }

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4">Mi perfil</Typography>
        <Typography color="text.secondary" sx={{ mt: 0.75 }}>
          Información de identidad utilizada por la API y el portal.
        </Typography>
      </Box>

      <Card sx={{ maxWidth: 760 }}>
        <CardContent sx={{ p: { xs: 3, sm: 4 } }}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3} alignItems={{ sm: 'center' }}>
            <Avatar sx={{ width: 84, height: 84, fontSize: 32, bgcolor: 'primary.main' }}>
              {user.full_name.charAt(0).toUpperCase()}
            </Avatar>
            <Box>
              <Typography variant="h5">{user.full_name}</Typography>
              <Typography color="text.secondary">{user.email}</Typography>
              <Stack direction="row" spacing={1} sx={{ mt: 1.5 }}>
                <Chip label={roleLabel(user.role)} color="primary" size="small" />
                <Chip
                  label={user.is_active ? 'Cuenta activa' : 'Cuenta desactivada'}
                  color={user.is_active ? 'success' : 'default'}
                  size="small"
                  variant="outlined"
                />
              </Stack>
            </Box>
          </Stack>

          <Divider sx={{ my: 3 }} />

          <Stack spacing={2}>
            <ProfileRow label="Identificador" value={user.id} />
            <ProfileRow label="Fecha de alta" value={new Date(user.created_at).toLocaleString('es-ES')} />
            <ProfileRow
              label="Última actualización"
              value={new Date(user.updated_at).toLocaleString('es-ES')}
            />
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  )
}

function ProfileRow({ label, value }: { label: string; value: string }) {
  return (
    <Box>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography sx={{ overflowWrap: 'anywhere' }}>{value}</Typography>
    </Box>
  )
}
