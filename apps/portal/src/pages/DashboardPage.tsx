import AssignmentOutlinedIcon from '@mui/icons-material/AssignmentOutlined'
import BusinessOutlinedIcon from '@mui/icons-material/BusinessOutlined'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined'
import RefreshIcon from '@mui/icons-material/Refresh'
import RequestQuoteOutlinedIcon from '@mui/icons-material/RequestQuoteOutlined'
import ViewKanbanOutlinedIcon from '@mui/icons-material/ViewKanbanOutlined'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  Grid,
  LinearProgress,
  MenuItem,
  Select,
  Stack,
  Typography,
} from '@mui/material'
import { Link } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { type ReactNode, useMemo, useState } from 'react'

import { ApiError } from '../api/client'
import { getDashboardSummary } from '../api/dashboard'
import { useAuth } from '../auth/AuthContext'
import { euro } from '../utils/finance'

interface MetricCardProps {
  label: string
  value: string | number
  detail?: string
}

function MetricCard({ label, value, detail }: MetricCardProps) {
  return (
    <Card sx={{ height: '100%', bgcolor: '#1a2530' }}>
      <CardContent sx={{ p: '12px !important' }}>
        <Box sx={{ bgcolor: '#141d26', px: 1.1, py: 0.5, mb: 1, borderRadius: 0.5 }}>
          <Typography variant="caption" fontWeight={720}>
            {label}
          </Typography>
        </Box>
        <Typography variant="subtitle1" fontWeight={780} noWrap>
          {value}
        </Typography>
        {detail && (
          <Typography variant="caption" color="text.secondary" display="block" noWrap>
            {detail}
          </Typography>
        )}
      </CardContent>
    </Card>
  )
}

interface WorkspacePanelProps {
  title: string
  children: ReactNode
  minHeight?: number
}

function WorkspacePanel({ title, children, minHeight = 230 }: WorkspacePanelProps) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: '14px !important' }}>
        <Box sx={{ bgcolor: '#141d26', px: 1.1, py: 0.65, mb: 1.2, borderRadius: 0.5 }}>
          <Typography variant="subtitle2" fontWeight={720}>
            {title}
          </Typography>
        </Box>
        <Box
          sx={{
            minHeight,
            border: '1px solid',
            borderColor: 'divider',
            bgcolor: '#202c38',
            p: 1.2,
          }}
        >
          {children}
        </Box>
      </CardContent>
    </Card>
  )
}

export function DashboardPage() {
  const { user } = useAuth()
  const [period, setPeriod] = useState('7')
  const summaryQuery = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: getDashboardSummary,
  })

  const summary = summaryQuery.data
  const inProgress = summary?.status_breakdown.find((item) => item.status === 'in_progress')?.count ?? 0
  const planned = summary?.status_breakdown.find((item) => item.status === 'planned')?.count ?? 0

  const alerts = useMemo(() => {
    if (!summary) return []

    const items: string[] = []
    if (summary.overdue_invoices > 0) {
      items.push(`${summary.overdue_invoices} factura(s) vencida(s) requieren seguimiento.`)
    }
    if (summary.overdue_work_orders > 0) {
      items.push(`${summary.overdue_work_orders} trabajo(s) superaron la fecha prevista.`)
    }
    if (summary.unassigned_work_orders > 0) {
      items.push(`${summary.unassigned_work_orders} trabajo(s) no tienen responsable asignado.`)
    }
    if (summary.pending_expenses > 0) {
      items.push(`${summary.pending_expenses} gasto(s) continúan pendientes de pago.`)
    }
    return items
  }, [summary])

  const activityTime = new Intl.DateTimeFormat('es-ES', {
    dateStyle: 'short',
    timeStyle: 'medium',
  }).format(new Date())

  return (
    <Stack spacing={1.7}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" gap={1.5}>
        <Box>
          <Typography variant="subtitle1" fontWeight={780}>
            Centro de Control
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Ventas, agenda, alertas y estado del sistema en una sola vista.
          </Typography>
        </Box>
        <Stack direction="row" spacing={1} alignItems="center">
          <FormControl size="small">
            <Select value={period} onChange={(event) => setPeriod(event.target.value)} sx={{ minWidth: 84 }}>
              <MenuItem value="7">7 días</MenuItem>
              <MenuItem value="30">30 días</MenuItem>
              <MenuItem value="90">90 días</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={() => void summaryQuery.refetch()}
          >
            Actualizar
          </Button>
        </Stack>
      </Stack>

      {summaryQuery.isFetching && <LinearProgress />}
      {summaryQuery.error && (
        <Alert severity="error">
          {summaryQuery.error instanceof ApiError
            ? summaryQuery.error.message
            : 'No se pudo cargar el resumen ejecutivo'}
        </Alert>
      )}

      <Grid container spacing={1.2}>
        <Grid size={{ xs: 12, sm: 6, lg: 2 }}>
          <MetricCard label="Ventas del periodo" value={euro(summary?.collected_total ?? '0')} detail={`${period} días`} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, lg: 2 }}>
          <MetricCard label="Presupuestos abiertos" value={summary?.draft_quotes ?? 0} detail="Borradores activos" />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, lg: 2 }}>
          <MetricCard label="Pipeline comercial" value={euro(summary?.quoted_total ?? '0')} detail={`${summary?.accepted_quotes ?? 0} aceptados`} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, lg: 2 }}>
          <MetricCard label="Cobros pendientes" value={euro(summary?.pending_total ?? '0')} detail={`${summary?.overdue_invoices ?? 0} vencidos`} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, lg: 2 }}>
          <MetricCard label="Tareas pendientes" value={summary?.open_work_orders ?? 0} detail={`${planned} planificadas`} />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, lg: 2 }}>
          <MetricCard label="Obras activas" value={inProgress} detail="En ejecución" />
        </Grid>
      </Grid>

      <Grid container spacing={1.4}>
        <Grid size={{ xs: 12, lg: 6 }}>
          <WorkspacePanel title="Agenda y próximas acciones" minHeight={235}>
            {(summary?.open_work_orders ?? 0) === 0 ? (
              <Typography variant="body2">No hay actividades pendientes.</Typography>
            ) : (
              <Stack spacing={1.1}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <AssignmentOutlinedIcon color="primary" fontSize="small" />
                  <Typography variant="body2">
                    {summary?.open_work_orders} trabajos abiertos pendientes de seguimiento.
                  </Typography>
                </Stack>
                <Stack direction="row" spacing={1} alignItems="center">
                  <RequestQuoteOutlinedIcon color="primary" fontSize="small" />
                  <Typography variant="body2">
                    {summary?.draft_quotes} presupuestos están todavía en borrador.
                  </Typography>
                </Stack>
                <Stack direction="row" spacing={1} alignItems="center">
                  <BusinessOutlinedIcon color="primary" fontSize="small" />
                  <Typography variant="body2">
                    {summary?.active_clients} clientes activos en la plataforma.
                  </Typography>
                </Stack>
              </Stack>
            )}
          </WorkspacePanel>
        </Grid>
        <Grid size={{ xs: 12, lg: 6 }}>
          <WorkspacePanel title="Alertas que requieren atención" minHeight={235}>
            {alerts.length === 0 ? (
              <Stack direction="row" spacing={1} alignItems="center">
                <CheckCircleOutlineIcon color="success" fontSize="small" />
                <Typography variant="body2">
                  Operación estable · No se detectan riesgos operativos relevantes.
                </Typography>
              </Stack>
            ) : (
              <Stack spacing={1.1}>
                {alerts.map((item) => (
                  <Stack key={item} direction="row" spacing={1} alignItems="flex-start">
                    <ErrorOutlineIcon color="warning" fontSize="small" />
                    <Typography variant="body2">{item}</Typography>
                  </Stack>
                ))}
              </Stack>
            )}
          </WorkspacePanel>
        </Grid>
      </Grid>

      <Grid container spacing={1.4}>
        <Grid size={{ xs: 12, lg: 6 }}>
          <WorkspacePanel title="Actividad reciente" minHeight={185}>
            <Stack spacing={1.2}>
              <Typography variant="body2">
                Sesión iniciada por {user?.full_name} · {activityTime}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Resumen operativo actualizado desde la API central.
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {summary?.total_clients ?? 0} clientes · {summary?.open_work_orders ?? 0} trabajos abiertos ·{' '}
                {summary?.active_suppliers ?? 0} proveedores activos.
              </Typography>
            </Stack>
          </WorkspacePanel>
        </Grid>
        <Grid size={{ xs: 12, lg: 6 }}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: '14px !important' }}>
              <Box sx={{ bgcolor: '#141d26', px: 1.1, py: 0.65, mb: 1.2, borderRadius: 0.5 }}>
                <Typography variant="subtitle2" fontWeight={720}>
                  Estado del sistema
                </Typography>
              </Box>
              <Stack spacing={0.8}>
                {[
                  `API central · ${summaryQuery.isSuccess ? 'Operativa' : 'Comprobando'}`,
                  'Centro de migración · Preparado',
                  `Salud operativa · ${alerts.length === 0 ? '100/100 · riesgo Bajo' : 'Revisión requerida'}`,
                ].map((item) => (
                  <Box key={item} sx={{ bgcolor: '#141d26', px: 1.1, py: 1 }}>
                    <Typography variant="body2">{item}</Typography>
                  </Box>
                ))}
              </Stack>
              <Grid container spacing={0.7} sx={{ mt: 1.1 }}>
                <Grid size={{ xs: 6, md: 2.4 }}>
                  <Button fullWidth variant="contained" component={Link} to="/clients">
                    Nuevo cliente
                  </Button>
                </Grid>
                <Grid size={{ xs: 6, md: 2.4 }}>
                  <Button fullWidth variant="contained" component={Link} to="/work-orders">
                    Nuevo trabajo
                  </Button>
                </Grid>
                <Grid size={{ xs: 6, md: 2.4 }}>
                  <Button fullWidth variant="contained" component={Link} to="/quotes" startIcon={<RequestQuoteOutlinedIcon />}>
                    Presupuesto
                  </Button>
                </Grid>
                <Grid size={{ xs: 6, md: 2.4 }}>
                  <Button fullWidth variant="contained" component={Link} to="/invoices" startIcon={<ReceiptLongOutlinedIcon />}>
                    Factura
                  </Button>
                </Grid>
                <Grid size={{ xs: 12, md: 2.4 }}>
                  <Button fullWidth variant="contained" component={Link} to="/work-orders" startIcon={<ViewKanbanOutlinedIcon />}>
                    Ver Kanban
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Stack>
  )
}
