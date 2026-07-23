import AdminPanelSettingsOutlinedIcon from '@mui/icons-material/AdminPanelSettingsOutlined'
import ApiOutlinedIcon from '@mui/icons-material/ApiOutlined'
import PersonOutlineIcon from '@mui/icons-material/PersonOutline'
import {
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  Stack,
  Typography,
} from '@mui/material'

import { useAuth } from '../auth/AuthContext'
import { roleLabel } from '../utils/roles'

export function DashboardPage() {
  const { user } = useAuth()

  const cards = [
    {
      title: 'Sesión activa',
      value: user?.full_name ?? 'Usuario',
      detail: user?.email ?? '',
      icon: <PersonOutlineIcon fontSize="large" />,
    },
    {
      title: 'Rol operativo',
      value: roleLabel(user?.role),
      detail: user?.role === 'admin' ? 'Acceso completo al portal' : 'Acceso estándar',
      icon: <AdminPanelSettingsOutlinedIcon fontSize="large" />,
    },
    {
      title: 'API conectada',
      value: 'Disponible',
      detail: 'FastAPI · PostgreSQL · JWT',
      icon: <ApiOutlinedIcon fontSize="large" />,
    },
  ]

  return (
    <Stack spacing={3}>
      <Box>
        <Chip label="Sprint 2 · Portal web" color="primary" variant="outlined" />
        <Typography variant="h4" sx={{ mt: 1.5 }}>
          Bienvenido, {user?.full_name}
        </Typography>
        <Typography color="text.secondary" sx={{ mt: 0.75 }}>
          Tu espacio central para consultar el estado de JR Platform y gestionar el acceso.
        </Typography>
      </Box>

      <Grid container spacing={2.5}>
        {cards.map((card) => (
          <Grid key={card.title} size={{ xs: 12, md: 4 }}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ p: 3 }}>
                <Stack direction="row" justifyContent="space-between" spacing={2}>
                  <Box>
                    <Typography variant="overline" color="text.secondary">
                      {card.title}
                    </Typography>
                    <Typography variant="h5" sx={{ mt: 0.5 }}>
                      {card.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {card.detail}
                    </Typography>
                  </Box>
                  <Box sx={{ color: 'primary.main' }}>{card.icon}</Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Card>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6">Estado del producto</Typography>
          <Typography color="text.secondary" sx={{ mt: 1 }}>
            La base de identidad ya está conectada al portal. Los próximos módulos se añadirán sobre
            esta navegación sin romper la autenticación ni los permisos existentes.
          </Typography>
        </CardContent>
      </Card>
    </Stack>
  )
}
