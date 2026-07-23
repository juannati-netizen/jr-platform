import AccountBalanceWalletOutlinedIcon from '@mui/icons-material/AccountBalanceWalletOutlined'
import AssignmentLateOutlinedIcon from '@mui/icons-material/AssignmentLateOutlined'
import AssignmentTurnedInOutlinedIcon from '@mui/icons-material/AssignmentTurnedInOutlined'
import BusinessOutlinedIcon from '@mui/icons-material/BusinessOutlined'
import EngineeringOutlinedIcon from '@mui/icons-material/EngineeringOutlined'
import PaidOutlinedIcon from '@mui/icons-material/PaidOutlined'
import PaymentsOutlinedIcon from '@mui/icons-material/PaymentsOutlined'
import PersonOffOutlinedIcon from '@mui/icons-material/PersonOffOutlined'
import RequestQuoteOutlinedIcon from '@mui/icons-material/RequestQuoteOutlined'
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
import { euro } from '../utils/finance'
import { workOrderStatusLabel } from '../utils/work-orders'

export function DashboardPage() {
  const { user } = useAuth()
  const summaryQuery = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: getDashboardSummary,
  })

  const summary = summaryQuery.data
  const operationalCards = [
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

  const financialCards = [
    {
      title: 'Presupuestado',
      value: euro(summary?.quoted_total ?? '0'),
      detail: `${summary?.accepted_quotes ?? 0} aceptados`,
      icon: <RequestQuoteOutlinedIcon fontSize="large" />,
    },
    {
      title: 'Facturado',
      value: euro(summary?.invoiced_total ?? '0'),
      detail: 'Importe emitido',
      icon: <AccountBalanceWalletOutlinedIcon fontSize="large" />,
    },
    {
      title: 'Cobrado',
      value: euro(summary?.collected_total ?? '0'),
      detail: 'Pagos registrados',
      icon: <PaidOutlinedIcon fontSize="large" />,
    },
    {
      title: 'Pendiente',
      value: euro(summary?.pending_total ?? '0'),
      detail: `${summary?.overdue_invoices ?? 0} facturas vencidas`,
      icon: <PaymentsOutlinedIcon fontSize="large" />,
    },
  ]

  return (
    <Stack spacing={3}>
      <Box>
        <Chip label="Sprint 4 · Presupuestos y facturación" color="primary" variant="outlined" />
        <Typography variant="h4" sx={{ mt: 1.5 }}>
          Bienvenido, {user?.full_name}
        </Typography>
        <Typography color="text.secondary" sx={{ mt: 0.75 }}>
          Resumen operativo y financiero de JR Platform.
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

      <Typography variant="h5">Operaciones</Typography>
      <Grid container spacing={2.5}>
        {operationalCards.map((card) => (
          <Grid key={card.title} size={{ xs: 12, sm: 6, lg: 4 }}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ p: 3 }}>
                <Stack direction="row" justifyContent="space-between" spacing={2}>
                  <Box>
                    <Typography variant="overline" color="text.secondary">{card.title}</Typography>
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

      <Typography variant="h5">Finanzas</Typography>
      <Grid container spacing={2.5}>
        {financialCards.map((card) => (
          <Grid key={card.title} size={{ xs: 12, sm: 6, lg: 3 }}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ p: 3 }}>
                <Stack direction="row" justifyContent="space-between" spacing={2}>
                  <Box>
                    <Typography variant="overline" color="text.secondary">{card.title}</Typography>
                    <Typography variant="h5" sx={{ mt: 0.5 }}>{card.value}</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {card.detail}
                    </Typography>
                  </Box>
                  <Box sx={{ color: 'secondary.main' }}>{card.icon}</Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Card>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6">Distribución de trabajos por estado</Typography>
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
