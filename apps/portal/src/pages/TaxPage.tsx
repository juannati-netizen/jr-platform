import AddOutlinedIcon from '@mui/icons-material/AddOutlined'
import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined'
import LockOpenOutlinedIcon from '@mui/icons-material/LockOpenOutlined'
import LockOutlinedIcon from '@mui/icons-material/LockOutlined'
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  Grid,
  MenuItem,
  Stack,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { type FormEvent, useEffect, useMemo, useState } from 'react'

import { ApiError } from '../api/client'
import {
  type TaxAdjustmentDirection,
  type TaxConfigurationPayload,
  closeTaxMonth,
  createTaxAdjustment,
  downloadModel420Csv,
  getModel420,
  getTaxConfiguration,
  getTaxMonths,
  reopenTaxMonth,
  updateTaxConfiguration,
} from '../api/tax'
import { euro } from '../utils/finance'

const currentYear = new Date().getFullYear()

const emptyConfiguration: TaxConfigurationPayload = {
  tax_system: 'igic',
  filing_model: '420',
  filing_frequency: 'quarterly',
  monthly_tracking_enabled: true,
  default_tax_rate: '7.00',
  notes: '',
}

function errorMessage(error: unknown): string {
  return error instanceof ApiError ? error.message : 'No se pudo completar la operación'
}

function resultLabel(resultType: string): string {
  if (resultType === 'to_pay') return 'A ingresar'
  if (resultType === 'to_compensate') return 'A compensar'
  return 'Sin resultado'
}

export function TaxPage() {
  const queryClient = useQueryClient()
  const [year, setYear] = useState(currentYear)
  const [quarter, setQuarter] = useState(1)
  const [configuration, setConfiguration] =
    useState<TaxConfigurationPayload>(emptyConfiguration)
  const [adjustmentOpen, setAdjustmentOpen] = useState(false)
  const [adjustment, setAdjustment] = useState({
    month: 1,
    direction: 'input' as TaxAdjustmentDirection,
    amount: '',
    description: '',
  })

  const configurationQuery = useQuery({
    queryKey: ['tax-configuration'],
    queryFn: getTaxConfiguration,
  })
  const monthsQuery = useQuery({
    queryKey: ['tax-months', year],
    queryFn: () => getTaxMonths(year),
  })
  const quarterQuery = useQuery({
    queryKey: ['model-420', year, quarter],
    queryFn: () => getModel420(year, quarter),
  })

  useEffect(() => {
    if (!configurationQuery.data) return
    const { id: _id, created_at: _created, updated_at: _updated, ...payload } =
      configurationQuery.data
    setConfiguration(payload)
  }, [configurationQuery.data])

  const refresh = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['tax-configuration'] }),
      queryClient.invalidateQueries({ queryKey: ['tax-months', year] }),
      queryClient.invalidateQueries({ queryKey: ['model-420', year] }),
      queryClient.invalidateQueries({ queryKey: ['configuration-events'] }),
    ])
  }

  const configurationMutation = useMutation({
    mutationFn: updateTaxConfiguration,
    onSuccess: refresh,
  })
  const periodMutation = useMutation({
    mutationFn: ({ month, action }: { month: number; action: 'close' | 'open' }) =>
      action === 'close' ? closeTaxMonth(year, month) : reopenTaxMonth(year, month),
    onSuccess: refresh,
  })
  const adjustmentMutation = useMutation({
    mutationFn: () =>
      createTaxAdjustment({
        year,
        month: adjustment.month,
        direction: adjustment.direction,
        amount: adjustment.amount,
        description: adjustment.description,
      }),
    onSuccess: async () => {
      setAdjustmentOpen(false)
      setAdjustment({ month: 1, direction: 'input', amount: '', description: '' })
      await refresh()
    },
  })

  const quarterMonths = useMemo(
    () => new Set([quarter * 3 - 2, quarter * 3 - 1, quarter * 3]),
    [quarter],
  )

  return (
    <Stack spacing={2}>
      <Box>
        <Chip label="Fiscalidad canaria" color="primary" variant="outlined" />
        <Typography variant="h4" sx={{ mt: 1.2 }}>
          IGIC y modelo 420
        </Typography>
        <Typography color="text.secondary" sx={{ mt: 0.6 }}>
          Seguimiento mensual y borrador trimestral del régimen general del IGIC.
        </Typography>
      </Box>

      <Alert severity="warning">
        Los importes son una estimación interna basada en los datos registrados. Revisa la
        documentación contable antes de presentar la autoliquidación oficial.
      </Alert>

      <Grid container spacing={1.5}>
        <Grid size={{ xs: 12, lg: 4 }}>
          <Card
            component="form"
            onSubmit={(event: FormEvent) => {
              event.preventDefault()
              configurationMutation.mutate(configuration)
            }}
          >
            <CardContent>
              <Typography variant="h6">Configuración fiscal</Typography>
              <Stack spacing={1.3} sx={{ mt: 1.5 }}>
                <TextField select label="Impuesto" value={configuration.tax_system} disabled>
                  <MenuItem value="igic">IGIC</MenuItem>
                </TextField>
                <TextField select label="Modelo" value={configuration.filing_model} disabled>
                  <MenuItem value="420">Modelo 420</MenuItem>
                </TextField>
                <TextField
                  label="Tipo general predeterminado"
                  type="number"
                  value={configuration.default_tax_rate}
                  onChange={(event) =>
                    setConfiguration({ ...configuration, default_tax_rate: event.target.value })
                  }
                  slotProps={{ htmlInput: { min: 0, max: 100, step: 0.01 } }}
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={configuration.monthly_tracking_enabled}
                      onChange={(event) =>
                        setConfiguration({
                          ...configuration,
                          monthly_tracking_enabled: event.target.checked,
                        })
                      }
                    />
                  }
                  label="Seguimiento mensual"
                />
                <TextField
                  multiline
                  minRows={3}
                  label="Notas fiscales"
                  value={configuration.notes ?? ''}
                  onChange={(event) =>
                    setConfiguration({ ...configuration, notes: event.target.value })
                  }
                />
                <Button type="submit" variant="contained" disabled={configurationMutation.isPending}>
                  Guardar configuración
                </Button>
                {configurationMutation.error && (
                  <Alert severity="error">{errorMessage(configurationMutation.error)}</Alert>
                )}
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, lg: 8 }}>
          <Card>
            <CardContent>
              <Stack
                direction={{ xs: 'column', sm: 'row' }}
                justifyContent="space-between"
                spacing={1.5}
              >
                <Box>
                  <Typography variant="h6">Borrador trimestral</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Resumen orientativo del modelo 420.
                  </Typography>
                </Box>
                <Stack direction="row" spacing={1}>
                  <TextField
                    size="small"
                    type="number"
                    label="Ejercicio"
                    value={year}
                    onChange={(event) => setYear(Number(event.target.value))}
                    sx={{ width: 125 }}
                  />
                  <TextField
                    size="small"
                    select
                    label="Trimestre"
                    value={quarter}
                    onChange={(event) => setQuarter(Number(event.target.value))}
                    sx={{ width: 130 }}
                  >
                    {[1, 2, 3, 4].map((item) => (
                      <MenuItem key={item} value={item}>
                        T{item}
                      </MenuItem>
                    ))}
                  </TextField>
                </Stack>
              </Stack>

              {quarterQuery.data && (
                <Stack spacing={1.5} sx={{ mt: 2 }}>
                  <Grid container spacing={1}>
                    <Grid size={{ xs: 6, md: 3 }}>
                      <Card variant="outlined"><CardContent><Typography variant="caption">IGIC repercutido</Typography><Typography variant="h6">{euro(quarterQuery.data.output_tax)}</Typography></CardContent></Card>
                    </Grid>
                    <Grid size={{ xs: 6, md: 3 }}>
                      <Card variant="outlined"><CardContent><Typography variant="caption">IGIC soportado</Typography><Typography variant="h6">{euro(quarterQuery.data.input_tax)}</Typography></CardContent></Card>
                    </Grid>
                    <Grid size={{ xs: 6, md: 3 }}>
                      <Card variant="outlined"><CardContent><Typography variant="caption">Resultado</Typography><Typography variant="h6">{euro(quarterQuery.data.result)}</Typography></CardContent></Card>
                    </Grid>
                    <Grid size={{ xs: 6, md: 3 }}>
                      <Card variant="outlined"><CardContent><Typography variant="caption">Estado</Typography><Chip size="small" color={quarterQuery.data.all_months_closed ? 'success' : 'warning'} label={quarterQuery.data.all_months_closed ? 'Trimestre cerrado' : 'Pendiente de cierre'} /></CardContent></Card>
                    </Grid>
                  </Grid>
                  <Alert severity={quarterQuery.data.result_type === 'to_pay' ? 'info' : 'success'}>
                    {resultLabel(quarterQuery.data.result_type)} · Presentación: {quarterQuery.data.filing_window}
                  </Alert>
                  <Button
                    variant="outlined"
                    startIcon={<DownloadOutlinedIcon />}
                    onClick={() => downloadModel420Csv(year, quarter)}
                    sx={{ alignSelf: 'flex-start' }}
                  >
                    Descargar borrador CSV
                  </Button>
                </Stack>
              )}
              {quarterQuery.error && <Alert severity="error" sx={{ mt: 2 }}>{errorMessage(quarterQuery.error)}</Alert>}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            justifyContent="space-between"
            spacing={1}
          >
            <Box>
              <Typography variant="h6">Control mensual de {year}</Typography>
              <Typography variant="body2" color="text.secondary">
                Cierra cada mes después de revisar facturas, gastos y ajustes.
              </Typography>
            </Box>
            <Button
              variant="outlined"
              startIcon={<AddOutlinedIcon />}
              onClick={() => {
                setAdjustment((current) => ({ ...current, month: quarter * 3 - 2 }))
                setAdjustmentOpen(true)
              }}
            >
              Añadir ajuste
            </Button>
          </Stack>
          <TableContainer sx={{ mt: 1.5 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Mes</TableCell>
                  <TableCell align="right">Base emitida</TableCell>
                  <TableCell align="right">IGIC repercutido</TableCell>
                  <TableCell align="right">Base gastos</TableCell>
                  <TableCell align="right">IGIC soportado</TableCell>
                  <TableCell align="right">Resultado</TableCell>
                  <TableCell>Estado</TableCell>
                  <TableCell align="right">Acción</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(monthsQuery.data ?? []).map((month) => (
                  <TableRow
                    key={month.month}
                    sx={{ bgcolor: quarterMonths.has(month.month) ? 'rgba(25,118,210,0.06)' : undefined }}
                  >
                    <TableCell>{month.month_label}</TableCell>
                    <TableCell align="right">{euro(month.output_base)}</TableCell>
                    <TableCell align="right">{euro(month.output_tax)}</TableCell>
                    <TableCell align="right">{euro(month.input_base)}</TableCell>
                    <TableCell align="right">{euro(month.input_tax)}</TableCell>
                    <TableCell align="right">
                      <Typography fontWeight={750}>{euro(month.result)}</Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        color={month.status === 'closed' ? 'success' : 'default'}
                        label={month.status === 'closed' ? 'Cerrado' : 'Abierto'}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Button
                        size="small"
                        color={month.status === 'closed' ? 'warning' : 'primary'}
                        startIcon={month.status === 'closed' ? <LockOpenOutlinedIcon /> : <LockOutlinedIcon />}
                        onClick={() =>
                          periodMutation.mutate({
                            month: month.month,
                            action: month.status === 'closed' ? 'open' : 'close',
                          })
                        }
                      >
                        {month.status === 'closed' ? 'Reabrir' : 'Cerrar'}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          {monthsQuery.error && <Alert severity="error" sx={{ mt: 2 }}>{errorMessage(monthsQuery.error)}</Alert>}
        </CardContent>
      </Card>

      <Dialog open={adjustmentOpen} onClose={() => setAdjustmentOpen(false)} fullWidth maxWidth="sm">
        <Box
          component="form"
          onSubmit={(event: FormEvent) => {
            event.preventDefault()
            adjustmentMutation.mutate()
          }}
        >
          <DialogTitle>Ajuste manual de IGIC</DialogTitle>
          <DialogContent>
            <Alert severity="info" sx={{ mb: 2 }}>
              Úsalo únicamente para regularizaciones documentadas que no estén reflejadas en las facturas o gastos.
            </Alert>
            <Stack spacing={1.4}>
              <TextField
                select
                label="Mes"
                value={adjustment.month}
                onChange={(event) => setAdjustment({ ...adjustment, month: Number(event.target.value) })}
              >
                {(monthsQuery.data ?? []).map((month) => (
                  <MenuItem key={month.month} value={month.month} disabled={month.status === 'closed'}>
                    {month.month_label}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="Tipo de ajuste"
                value={adjustment.direction}
                onChange={(event) => setAdjustment({ ...adjustment, direction: event.target.value as TaxAdjustmentDirection })}
              >
                <MenuItem value="output">IGIC repercutido</MenuItem>
                <MenuItem value="input">IGIC soportado/deducible</MenuItem>
              </TextField>
              <TextField
                required
                type="number"
                label="Importe"
                value={adjustment.amount}
                onChange={(event) => setAdjustment({ ...adjustment, amount: event.target.value })}
                slotProps={{ htmlInput: { min: 0.01, step: 0.01 } }}
              />
              <TextField
                required
                multiline
                minRows={3}
                label="Motivo y referencia documental"
                value={adjustment.description}
                onChange={(event) => setAdjustment({ ...adjustment, description: event.target.value })}
              />
              {adjustmentMutation.error && <Alert severity="error">{errorMessage(adjustmentMutation.error)}</Alert>}
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAdjustmentOpen(false)}>Cancelar</Button>
            <Button type="submit" variant="contained" startIcon={<ReceiptLongOutlinedIcon />} disabled={adjustmentMutation.isPending}>
              Guardar ajuste
            </Button>
          </DialogActions>
        </Box>
      </Dialog>
    </Stack>
  )
}
