import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined'
import TrendingUpOutlinedIcon from '@mui/icons-material/TrendingUpOutlined'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material'
import { useQuery } from '@tanstack/react-query'

import { ApiError } from '../api/client'
import { getProfitabilitySummary } from '../api/procurement'
import type { ProfitabilitySummary } from '../api/types'
import { euro } from '../utils/finance'

function downloadCsv(summary: ProfitabilitySummary): void {
  const rows = [
    ['Tipo', 'Nombre', 'Cliente', 'Facturado', 'Cobrado', 'Gastos', 'Margen', 'Margen realizado'],
    ...summary.work_orders.map((item) => [
      'Trabajo',
      item.title,
      item.client_name,
      item.invoiced_revenue,
      item.collected_revenue,
      item.expenses_total,
      item.gross_margin,
      item.realized_margin,
    ]),
    ...summary.clients.map((item) => [
      'Cliente',
      item.name,
      item.name,
      item.invoiced_revenue,
      item.collected_revenue,
      item.expenses_total,
      item.gross_margin,
      item.realized_margin,
    ]),
  ]
  const content = rows
    .map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(';'))
    .join('\n')
  const blob = new Blob([`\uFEFF${content}`], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `rentabilidad-${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

export function ProfitabilityPage() {
  const summaryQuery = useQuery({
    queryKey: ['profitability-summary'],
    queryFn: getProfitabilitySummary,
  })
  const summary = summaryQuery.data

  const cards = [
    { title: 'Ingresos facturados', value: euro(summary?.invoiced_revenue ?? '0') },
    { title: 'Ingresos cobrados', value: euro(summary?.collected_revenue ?? '0') },
    { title: 'Gastos', value: euro(summary?.expenses_total ?? '0') },
    { title: 'Coste de materiales', value: euro(summary?.material_costs ?? '0') },
    { title: 'Margen bruto', value: euro(summary?.gross_margin ?? '0') },
    { title: 'Margen realizado', value: euro(summary?.realized_margin ?? '0') },
  ]

  return (
    <Stack spacing={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" spacing={2}>
        <Box>
          <Typography variant="h4">Rentabilidad</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.75 }}>
            Comparativa de ingresos, costes y margen por trabajo y cliente.
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<DownloadOutlinedIcon />}
          disabled={!summary}
          onClick={() => summary && downloadCsv(summary)}
        >
          Exportar CSV
        </Button>
      </Stack>

      {summaryQuery.error && (
        <Alert severity="error">
          {summaryQuery.error instanceof ApiError
            ? summaryQuery.error.message
            : 'No se pudo cargar el informe de rentabilidad'}
        </Alert>
      )}
      {summaryQuery.isLoading && (
        <Stack alignItems="center" spacing={2} sx={{ py: 6 }}>
          <CircularProgress />
          <Typography color="text.secondary">Calculando rentabilidad…</Typography>
        </Stack>
      )}

      {summary && (
        <>
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
                        <Typography variant="h5" sx={{ mt: 0.5 }}>{card.value}</Typography>
                      </Box>
                      <TrendingUpOutlinedIcon color="primary" fontSize="large" />
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          <Card>
            <CardContent sx={{ p: 0 }}>
              <Box sx={{ p: 3, pb: 1 }}>
                <Typography variant="h6">Rentabilidad por trabajo</Typography>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Trabajo</TableCell>
                      <TableCell>Cliente</TableCell>
                      <TableCell align="right">Facturado</TableCell>
                      <TableCell align="right">Cobrado</TableCell>
                      <TableCell align="right">Gastos</TableCell>
                      <TableCell align="right">Margen</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {summary.work_orders.map((item) => (
                      <TableRow key={item.id} hover>
                        <TableCell><Typography fontWeight={700}>{item.title}</Typography></TableCell>
                        <TableCell>{item.client_name}</TableCell>
                        <TableCell align="right">{euro(item.invoiced_revenue)}</TableCell>
                        <TableCell align="right">{euro(item.collected_revenue)}</TableCell>
                        <TableCell align="right">{euro(item.expenses_total)}</TableCell>
                        <TableCell align="right">
                          <Typography
                            fontWeight={800}
                            color={Number(item.gross_margin) >= 0 ? 'success.main' : 'error.main'}
                          >
                            {euro(item.gross_margin)}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                    {summary.work_orders.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={6} align="center" sx={{ py: 5 }}>
                          <Typography color="text.secondary">No hay trabajos para analizar.</Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>

          <Card>
            <CardContent sx={{ p: 0 }}>
              <Box sx={{ p: 3, pb: 1 }}>
                <Typography variant="h6">Rentabilidad por cliente</Typography>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Cliente</TableCell>
                      <TableCell align="right">Facturado</TableCell>
                      <TableCell align="right">Cobrado</TableCell>
                      <TableCell align="right">Gastos</TableCell>
                      <TableCell align="right">Margen realizado</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {summary.clients.map((item) => (
                      <TableRow key={item.id} hover>
                        <TableCell><Typography fontWeight={700}>{item.name}</Typography></TableCell>
                        <TableCell align="right">{euro(item.invoiced_revenue)}</TableCell>
                        <TableCell align="right">{euro(item.collected_revenue)}</TableCell>
                        <TableCell align="right">{euro(item.expenses_total)}</TableCell>
                        <TableCell align="right">
                          <Typography
                            fontWeight={800}
                            color={Number(item.realized_margin) >= 0 ? 'success.main' : 'error.main'}
                          >
                            {euro(item.realized_margin)}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </>
      )}
    </Stack>
  )
}
