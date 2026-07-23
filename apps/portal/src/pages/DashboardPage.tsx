import AssignmentLateOutlinedIcon from '@mui/icons-material/AssignmentLateOutlined'
import AssignmentTurnedInOutlinedIcon from '@mui/icons-material/AssignmentTurnedInOutlined'
import BusinessOutlinedIcon from '@mui/icons-material/BusinessOutlined'
import EngineeringOutlinedIcon from '@mui/icons-material/EngineeringOutlined'
import PersonOffOutlinedIcon from '@mui/icons-material/PersonOffOutlined'
import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  LinearProgress,
  Stack,
  Typography,
} from '@mui/material'
import { useQuery } from '@tanstack/react-query'

import { ApiError } from '../api/client'
import { getDashboardSummary } from '../api/dashboard'
import { useAuth } from '../auth/AuthContext'
import { workOrderStatusLabel } from '../utils/work-orders'

export function DashboardPage() {
  const { user } = useAuth()
  const summaryQuery = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: getDashboardSummary,
  })

  const summary = summaryQuery.data
  const cards = [
    {
      title: 'Clientes activos',
      value: summary?.active_clients ?? 0,
      detail: `${summary?.total_clients ?? 0} clientes registrados`,
      icon: <BusinessOutlinedIcon fontSize="large" />,
    },
    {
      title: 'Trabajos abiertos',
      value: summary?.open_work_orders ?? 0,
      detail: 'Pendientes de cierre',
      icon: <EngineeringOutlinedIcon fontSize="large" />,
    },
    {
      title: 'Completados',
      value: summary?.completed_work_orders ?? 0,
      detail: 'Histórico finalizado',
      icon: <AssignmentTurnedInOutlinedIcon fontSize="large" />,
    },
    {
      title: 'Vencidos',
      value: summary?.overdue_work_orders ?? 0,
      detail: 'Requieren revisión',
      icon: <AssignmentLateOutlinedIcon fontSize="large" />,
    },
    {
      title: 'Sin responsable',
      value: summary?.unassigned_work_orders ?? 0,
      detail: 'Trabajos abiertos sin asignar',
      icon: <PersonOffOutlinedIcon fontSize="large" />,
    },
  ]

  return (
    <Stack spacing={3}>
      <Box>
        <Chip label="Sprint 3 · Gestión operativa" color="primary" variant="outlined" />
        <Typography variant="h4" sx={{ mt: 1.5 }}>
          Bienvenido, {user?.full_name}
        </Typography>
        <Typography color="text.secondary" sx={{ mt: 0.75 }}>
          Resumen de clientes, trabajos y carga operativa de JR Platform.
        </Typography>
      </Box>

      {summaryQuery.isLoading && <LinearProgress />}
      {summaryQuery.error && (
        <Alert severity="error">
          {summaryQuery.error instanceof ApiError
            ? summaryQuery.error.message
            : 'No se pudo cargar el resumen'}
        </Alert>
      )}

      <Grid container spacing={2.5}>
        {cards.map((card) => (
          <Grid key={card.title} size={{ xs: 12, sm: 6, lg: 4 }}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ p: 3 }}>
                <Stack direction="row" justifyContent="space-between" spacing={2}>
                  <Box>
                    <Typography variant="overline" color="text.secondary">
                      {card.title}
                    </Typography>
                    <Typography variant="h4" sx={{ mt: 0.5 }}>{card.value}</Typography>
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
          <Typography variant="h6">Distribución por estado</Typography>
          {summaryQuery.isLoading && (
            <Stack alignItems="center" sx={{ py: 3 }}><CircularProgress size={28} /></Stack>
          )}
          <Stack spacing={1.5} sx={{ mt: 2 }}>
            {summary?.status_breakdown.map((metric) => (
              <Stack key={metric.status} direction="row" justifyContent="space-between">
                <Typography color="text.secondary">{workOrderStatusLabel(metric.status)}</Typography>
                <Typography fontWeight={800}>{metric.count}</Typography>
              </Stack>
            ))}
          </Stack>
        </CardContent>
      </Card>
    </Stack>
  )
}
