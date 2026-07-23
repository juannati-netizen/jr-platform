import AutoAwesomeOutlinedIcon from '@mui/icons-material/AutoAwesomeOutlined'
import BusinessOutlinedIcon from '@mui/icons-material/BusinessOutlined'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import EventAvailableOutlinedIcon from '@mui/icons-material/EventAvailableOutlined'
import GppMaybeOutlinedIcon from '@mui/icons-material/GppMaybeOutlined'
import HistoryOutlinedIcon from '@mui/icons-material/HistoryOutlined'
import WarningAmberOutlinedIcon from '@mui/icons-material/WarningAmberOutlined'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Checkbox,
  Chip,
  CircularProgress,
  FormControlLabel,
  Grid,
  LinearProgress,
  MenuItem,
  Stack,
  Switch,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { type FormEvent, useEffect, useMemo, useState } from 'react'

import { ApiError } from '../api/client'
import {
  type AiConfigurationPayload,
  type CompanyProfilePayload,
  type FiscalYearPayload,
  type VerifactuPayload,
  closeFiscalYear,
  createFiscalYear,
  getAiConfiguration,
  getAiReadiness,
  getCompanyProfile,
  getConfigurationEvents,
  getFiscalYears,
  getVerifactuConfiguration,
  getVerifactuReadiness,
  openFiscalYear,
  updateAiConfiguration,
  updateCompanyProfile,
  updateVerifactuConfiguration,
} from '../api/settings'

const emptyCompany: CompanyProfilePayload = {
  legal_name: '',
  trade_name: '',
  tax_id: '',
  legal_form: '',
  tax_regime: '',
  address: '',
  postal_code: '',
  city: '',
  province: '',
  country: 'España',
  email: '',
  phone: '',
  website: '',
  iban: '',
  invoice_prefix: 'F',
  quote_prefix: 'P',
  currency: 'EUR',
  timezone: 'Europe/Madrid',
  logo_data_url: null,
  brand_color: '#1976d2',
  document_footer: '',
}

const emptyFiscalYear: FiscalYearPayload = {
  year: new Date().getFullYear(),
  start_date: `${new Date().getFullYear()}-01-01`,
  end_date: `${new Date().getFullYear()}-12-31`,
  notes: '',
}

const emptyVerifactu: VerifactuPayload = {
  mode: 'disabled',
  system_name: 'JR Platform',
  system_version: '0.11.0',
  producer_name: '',
  producer_tax_id: '',
  qr_enabled: false,
  hash_chain_enabled: false,
  event_log_enabled: false,
  aeat_transmission_enabled: false,
  responsible_declaration_signed: false,
  certificate_alias: '',
  notes: '',
}

const emptyAi: AiConfigurationPayload = {
  enabled: false,
  provider: 'disabled',
  model: '',
  assistant_name: 'Asistente JR',
  system_prompt: '',
  allow_customer_data: false,
  allow_financial_data: false,
  allow_document_content: false,
  human_review_required: true,
  retention_days: 0,
  notes: '',
}

function errorMessage(error: unknown) {
  return error instanceof ApiError ? error.message : 'No se pudo completar la operación'
}

function ReadinessList({
  items,
}: {
  items: Array<{ key: string; label: string; completed: boolean; detail: string }>
}) {
  return (
    <Stack spacing={1}>
      {items.map((item) => (
        <Box
          key={item.key}
          sx={{
            border: '1px solid',
            borderColor: 'divider',
            bgcolor: '#141d26',
            p: 1.2,
            borderRadius: 1,
          }}
        >
          <Stack direction="row" spacing={1} alignItems="flex-start">
            {item.completed ? (
              <CheckCircleOutlineIcon color="success" fontSize="small" />
            ) : (
              <WarningAmberOutlinedIcon color="warning" fontSize="small" />
            )}
            <Box>
              <Typography fontWeight={750} variant="body2">
                {item.label}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {item.detail}
              </Typography>
            </Box>
          </Stack>
        </Box>
      ))}
    </Stack>
  )
}

export function SettingsPage() {
  const queryClient = useQueryClient()
  const [tab, setTab] = useState(0)
  const [company, setCompany] = useState<CompanyProfilePayload>(emptyCompany)
  const [fiscalYear, setFiscalYear] = useState<FiscalYearPayload>(emptyFiscalYear)
  const [verifactu, setVerifactu] = useState<VerifactuPayload>(emptyVerifactu)
  const [ai, setAi] = useState<AiConfigurationPayload>(emptyAi)

  const companyQuery = useQuery({
    queryKey: ['company-profile'],
    queryFn: getCompanyProfile,
  })
  const yearsQuery = useQuery({
    queryKey: ['fiscal-years'],
    queryFn: getFiscalYears,
  })
  const verifactuQuery = useQuery({
    queryKey: ['verifactu-config'],
    queryFn: getVerifactuConfiguration,
  })
  const verifactuReadinessQuery = useQuery({
    queryKey: ['verifactu-readiness'],
    queryFn: getVerifactuReadiness,
  })
  const aiQuery = useQuery({
    queryKey: ['ai-config'],
    queryFn: getAiConfiguration,
  })
  const aiReadinessQuery = useQuery({
    queryKey: ['ai-readiness'],
    queryFn: getAiReadiness,
  })
  const eventsQuery = useQuery({
    queryKey: ['configuration-events'],
    queryFn: getConfigurationEvents,
  })

  useEffect(() => {
    if (companyQuery.data) {
      const { id: _id, created_at: _created, updated_at: _updated, ...payload } =
        companyQuery.data
      setCompany(payload)
    }
  }, [companyQuery.data])

  useEffect(() => {
    if (verifactuQuery.data) {
      const {
        id: _id,
        reviewed_at: _reviewed,
        created_at: _created,
        updated_at: _updated,
        ...payload
      } = verifactuQuery.data
      setVerifactu(payload)
    }
  }, [verifactuQuery.data])

  useEffect(() => {
    if (aiQuery.data) {
      const {
        id: _id,
        api_key_configured: _key,
        base_url_configured: _url,
        created_at: _created,
        updated_at: _updated,
        ...payload
      } = aiQuery.data
      setAi(payload)
    }
  }, [aiQuery.data])

  const refreshSettings = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['company-profile'] }),
      queryClient.invalidateQueries({ queryKey: ['company-public-profile'] }),
      queryClient.invalidateQueries({ queryKey: ['fiscal-years'] }),
      queryClient.invalidateQueries({ queryKey: ['verifactu-config'] }),
      queryClient.invalidateQueries({ queryKey: ['verifactu-readiness'] }),
      queryClient.invalidateQueries({ queryKey: ['ai-config'] }),
      queryClient.invalidateQueries({ queryKey: ['ai-readiness'] }),
      queryClient.invalidateQueries({ queryKey: ['configuration-events'] }),
    ])
  }

  const companyMutation = useMutation({
    mutationFn: updateCompanyProfile,
    onSuccess: refreshSettings,
  })
  const yearMutation = useMutation({
    mutationFn: createFiscalYear,
    onSuccess: async () => {
      setFiscalYear(emptyFiscalYear)
      await refreshSettings()
    },
  })
  const yearStatusMutation = useMutation({
    mutationFn: ({ id, action }: { id: string; action: 'open' | 'close' }) =>
      action === 'open' ? openFiscalYear(id) : closeFiscalYear(id),
    onSuccess: refreshSettings,
  })
  const verifactuMutation = useMutation({
    mutationFn: updateVerifactuConfiguration,
    onSuccess: refreshSettings,
  })
  const aiMutation = useMutation({
    mutationFn: updateAiConfiguration,
    onSuccess: refreshSettings,
  })

  const handleLogoFile = (file: File | undefined) => {
    if (!file) return
    if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type)) {
      window.alert('Selecciona un archivo PNG, JPG o WebP.')
      return
    }
    if (file.size > 1_500_000) {
      window.alert('El logotipo no puede superar 1,5 MB.')
      return
    }
    const reader = new FileReader()
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        setCompany((current) => ({ ...current, logo_data_url: reader.result as string }))
      }
    }
    reader.readAsDataURL(file)
  }

  const busy =
    companyQuery.isLoading ||
    yearsQuery.isLoading ||
    verifactuQuery.isLoading ||
    aiQuery.isLoading

  const tabLabels = useMemo(
    () => [
      { label: 'Empresa', icon: <BusinessOutlinedIcon /> },
      { label: 'Ejercicios fiscales', icon: <EventAvailableOutlinedIcon /> },
      { label: 'VERI*FACTU', icon: <GppMaybeOutlinedIcon /> },
      { label: 'Centro de IA', icon: <AutoAwesomeOutlinedIcon /> },
      { label: 'Historial', icon: <HistoryOutlinedIcon /> },
    ],
    [],
  )

  if (busy) {
    return (
      <Box sx={{ display: 'grid', placeItems: 'center', minHeight: 360 }}>
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Stack spacing={2}>
      <Box>
        <Chip label="Administración y cumplimiento" color="primary" variant="outlined" />
        <Typography variant="h4" sx={{ mt: 1.2 }}>
          Configuración empresarial
        </Typography>
        <Typography color="text.secondary" sx={{ mt: 0.6 }}>
          Datos fiscales, ejercicios, preparación VERI*FACTU y gobierno del Centro de IA.
        </Typography>
      </Box>

      <Card>
        <Tabs
          value={tab}
          onChange={(_, value: number) => setTab(value)}
          variant="scrollable"
          scrollButtons="auto"
        >
          {tabLabels.map((item) => (
            <Tab key={item.label} label={item.label} icon={item.icon} iconPosition="start" />
          ))}
        </Tabs>
      </Card>

      {tab === 0 && (
        <Card component="form" onSubmit={(event: FormEvent) => {
          event.preventDefault()
          companyMutation.mutate(company)
        }}>
          <CardContent>
            <Typography variant="h6">Identificación, marca y datos fiscales</Typography>
            <Grid container spacing={1.5} sx={{ mt: 0.4 }}>
              <Grid size={{ xs: 12 }}>
                <Card variant="outlined" sx={{ bgcolor: '#141d26' }}>
                  <CardContent>
                    <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems={{ md: 'center' }}>
                      <Box
                        sx={{
                          width: 150,
                          height: 90,
                          border: '1px dashed',
                          borderColor: 'divider',
                          borderRadius: 1,
                          display: 'grid',
                          placeItems: 'center',
                          bgcolor: '#fff',
                          overflow: 'hidden',
                        }}
                      >
                        {company.logo_data_url ? (
                          <Box component="img" src={company.logo_data_url} alt="Logotipo de la empresa" sx={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} />
                        ) : (
                          <Typography variant="caption" color="text.secondary">Sin logotipo</Typography>
                        )}
                      </Box>
                      <Stack spacing={1} sx={{ flex: 1 }}>
                        <Typography fontWeight={750}>Identidad visual</Typography>
                        <Typography variant="body2" color="text.secondary">
                          El logotipo aparecerá en la cabecera y en los documentos imprimibles.
                        </Typography>
                        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
                          <Button component="label" variant="outlined">
                            Seleccionar logo
                            <input hidden type="file" accept="image/png,image/jpeg,image/webp" onChange={(event) => handleLogoFile(event.target.files?.[0])} />
                          </Button>
                          <Button color="warning" disabled={!company.logo_data_url} onClick={() => setCompany({ ...company, logo_data_url: null })}>
                            Quitar logo
                          </Button>
                        </Stack>
                      </Stack>
                      <TextField
                        label="Color corporativo"
                        type="color"
                        value={company.brand_color}
                        onChange={(event) => setCompany({ ...company, brand_color: event.target.value })}
                        sx={{ width: 150 }}
                        slotProps={{ inputLabel: { shrink: true } }}
                      />
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField fullWidth required label="Razón social" value={company.legal_name} onChange={(event) => setCompany({ ...company, legal_name: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField fullWidth label="Nombre comercial" value={company.trade_name ?? ''} onChange={(event) => setCompany({ ...company, trade_name: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <TextField fullWidth required label="NIF/CIF" value={company.tax_id} onChange={(event) => setCompany({ ...company, tax_id: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <TextField fullWidth label="Forma jurídica" value={company.legal_form ?? ''} onChange={(event) => setCompany({ ...company, legal_form: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <TextField fullWidth label="Régimen fiscal" value={company.tax_regime ?? ''} onChange={(event) => setCompany({ ...company, tax_regime: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField fullWidth label="Domicilio fiscal" value={company.address ?? ''} onChange={(event) => setCompany({ ...company, address: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 12, md: 3 }}>
                <TextField fullWidth label="Código postal" value={company.postal_code ?? ''} onChange={(event) => setCompany({ ...company, postal_code: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 12, md: 3 }}>
                <TextField fullWidth label="Población" value={company.city ?? ''} onChange={(event) => setCompany({ ...company, city: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 12, md: 3 }}>
                <TextField fullWidth label="Provincia" value={company.province ?? ''} onChange={(event) => setCompany({ ...company, province: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 12, md: 3 }}>
                <TextField fullWidth label="País" value={company.country} onChange={(event) => setCompany({ ...company, country: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <TextField fullWidth type="email" label="Correo" value={company.email ?? ''} onChange={(event) => setCompany({ ...company, email: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <TextField fullWidth label="Teléfono" value={company.phone ?? ''} onChange={(event) => setCompany({ ...company, phone: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <TextField fullWidth label="Web" value={company.website ?? ''} onChange={(event) => setCompany({ ...company, website: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <TextField fullWidth label="IBAN" value={company.iban ?? ''} onChange={(event) => setCompany({ ...company, iban: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 6, md: 2 }}>
                <TextField fullWidth label="Serie facturas" value={company.invoice_prefix} onChange={(event) => setCompany({ ...company, invoice_prefix: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 6, md: 2 }}>
                <TextField fullWidth label="Serie presupuestos" value={company.quote_prefix} onChange={(event) => setCompany({ ...company, quote_prefix: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 6, md: 1 }}>
                <TextField fullWidth label="Moneda" value={company.currency} onChange={(event) => setCompany({ ...company, currency: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 6, md: 1 }}>
                <TextField fullWidth label="Zona" value={company.timezone} onChange={(event) => setCompany({ ...company, timezone: event.target.value })} />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField fullWidth multiline minRows={2} label="Pie de presupuestos y facturas" value={company.document_footer ?? ''} onChange={(event) => setCompany({ ...company, document_footer: event.target.value })} />
              </Grid>
            </Grid>
            {companyMutation.error && <Alert severity="error" sx={{ mt: 2 }}>{errorMessage(companyMutation.error)}</Alert>}
            {companyMutation.isSuccess && <Alert severity="success" sx={{ mt: 2 }}>Datos de empresa guardados.</Alert>}
            <Button type="submit" variant="contained" sx={{ mt: 2 }} disabled={companyMutation.isPending}>
              Guardar datos de empresa
            </Button>
          </CardContent>
        </Card>
      )}

      {tab === 1 && (
        <Grid container spacing={1.5}>
          <Grid size={{ xs: 12, lg: 4 }}>
            <Card component="form" onSubmit={(event: FormEvent) => {
              event.preventDefault()
              yearMutation.mutate(fiscalYear)
            }}>
              <CardContent>
                <Typography variant="h6">Abrir ejercicio</Typography>
                <Stack spacing={1.3} sx={{ mt: 1.5 }}>
                  <TextField type="number" label="Año" value={fiscalYear.year} onChange={(event) => setFiscalYear({ ...fiscalYear, year: Number(event.target.value) })} />
                  <TextField type="date" label="Fecha de apertura" slotProps={{ inputLabel: { shrink: true } }} value={fiscalYear.start_date} onChange={(event) => setFiscalYear({ ...fiscalYear, start_date: event.target.value })} />
                  <TextField type="date" label="Fecha de cierre" slotProps={{ inputLabel: { shrink: true } }} value={fiscalYear.end_date} onChange={(event) => setFiscalYear({ ...fiscalYear, end_date: event.target.value })} />
                  <TextField multiline minRows={3} label="Notas" value={fiscalYear.notes ?? ''} onChange={(event) => setFiscalYear({ ...fiscalYear, notes: event.target.value })} />
                  <Button type="submit" variant="contained" disabled={yearMutation.isPending}>Abrir ejercicio</Button>
                  {yearMutation.error && <Alert severity="error">{errorMessage(yearMutation.error)}</Alert>}
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, lg: 8 }}>
            <Stack spacing={1}>
              {(yearsQuery.data ?? []).map((item) => (
                <Card key={item.id}>
                  <CardContent>
                    <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" gap={1.5}>
                      <Box>
                        <Stack direction="row" spacing={1} alignItems="center">
                          <Typography variant="h6">Ejercicio {item.year}</Typography>
                          <Chip size="small" color={item.status === 'open' ? 'success' : 'default'} label={item.status === 'open' ? 'Abierto' : 'Cerrado'} />
                        </Stack>
                        <Typography variant="body2" color="text.secondary">
                          {item.start_date} — {item.end_date}
                        </Typography>
                        {item.notes && <Typography variant="body2" sx={{ mt: 0.7 }}>{item.notes}</Typography>}
                      </Box>
                      <Button
                        variant="outlined"
                        color={item.status === 'open' ? 'warning' : 'success'}
                        onClick={() => yearStatusMutation.mutate({ id: item.id, action: item.status === 'open' ? 'close' : 'open' })}
                      >
                        {item.status === 'open' ? 'Cerrar ejercicio' : 'Reabrir ejercicio'}
                      </Button>
                    </Stack>
                  </CardContent>
                </Card>
              ))}
              {(yearsQuery.data ?? []).length === 0 && <Alert severity="info">Todavía no hay ejercicios fiscales.</Alert>}
            </Stack>
          </Grid>
        </Grid>
      )}

      {tab === 2 && (
        <Grid container spacing={1.5}>
          <Grid size={{ xs: 12, lg: 7 }}>
            <Card component="form" onSubmit={(event: FormEvent) => {
              event.preventDefault()
              verifactuMutation.mutate(verifactu)
            }}>
              <CardContent>
                <Typography variant="h6">Preparación VERI*FACTU</Typography>
                <Alert severity="warning" sx={{ mt: 1.2 }}>
                  Este panel no activa ni certifica la remisión real. Sirve para preparar y documentar la configuración.
                </Alert>
                <Grid container spacing={1.3} sx={{ mt: 0.5 }}>
                  <Grid size={{ xs: 12, md: 4 }}>
                    <TextField select fullWidth label="Modo" value={verifactu.mode} onChange={(event) => setVerifactu({ ...verifactu, mode: event.target.value as VerifactuPayload['mode'] })}>
                      <MenuItem value="disabled">Desactivado</MenuItem>
                      <MenuItem value="preparation">Preparación</MenuItem>
                      <MenuItem value="test">Pruebas</MenuItem>
                    </TextField>
                  </Grid>
                  <Grid size={{ xs: 12, md: 4 }}>
                    <TextField fullWidth label="Sistema" value={verifactu.system_name} onChange={(event) => setVerifactu({ ...verifactu, system_name: event.target.value })} />
                  </Grid>
                  <Grid size={{ xs: 12, md: 4 }}>
                    <TextField fullWidth label="Versión" value={verifactu.system_version} onChange={(event) => setVerifactu({ ...verifactu, system_version: event.target.value })} />
                  </Grid>
                  <Grid size={{ xs: 12, md: 6 }}>
                    <TextField fullWidth label="Productor/fabricante" value={verifactu.producer_name ?? ''} onChange={(event) => setVerifactu({ ...verifactu, producer_name: event.target.value })} />
                  </Grid>
                  <Grid size={{ xs: 12, md: 6 }}>
                    <TextField fullWidth label="NIF del productor" value={verifactu.producer_tax_id ?? ''} onChange={(event) => setVerifactu({ ...verifactu, producer_tax_id: event.target.value })} />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <Stack>
                      <FormControlLabel control={<Checkbox checked={verifactu.qr_enabled} onChange={(event) => setVerifactu({ ...verifactu, qr_enabled: event.target.checked })} />} label="Preparación de código QR" />
                      <FormControlLabel control={<Checkbox checked={verifactu.hash_chain_enabled} onChange={(event) => setVerifactu({ ...verifactu, hash_chain_enabled: event.target.checked })} />} label="Huella y encadenamiento de registros" />
                      <FormControlLabel control={<Checkbox checked={verifactu.event_log_enabled} onChange={(event) => setVerifactu({ ...verifactu, event_log_enabled: event.target.checked })} />} label="Registro técnico de eventos" />
                      <FormControlLabel control={<Checkbox checked={verifactu.responsible_declaration_signed} onChange={(event) => setVerifactu({ ...verifactu, responsible_declaration_signed: event.target.checked })} />} label="Declaración responsable revisada y firmada" />
                      <FormControlLabel control={<Checkbox checked={verifactu.aeat_transmission_enabled} disabled={verifactu.mode !== 'test'} onChange={(event) => setVerifactu({ ...verifactu, aeat_transmission_enabled: event.target.checked })} />} label="Simular remisión en entorno de pruebas" />
                    </Stack>
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <TextField fullWidth label="Alias de certificado" value={verifactu.certificate_alias ?? ''} onChange={(event) => setVerifactu({ ...verifactu, certificate_alias: event.target.value })} />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <TextField fullWidth multiline minRows={3} label="Notas de cumplimiento" value={verifactu.notes ?? ''} onChange={(event) => setVerifactu({ ...verifactu, notes: event.target.value })} />
                  </Grid>
                </Grid>
                {verifactuMutation.error && <Alert severity="error" sx={{ mt: 2 }}>{errorMessage(verifactuMutation.error)}</Alert>}
                <Button type="submit" variant="contained" sx={{ mt: 2 }}>Guardar configuración</Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, lg: 5 }}>
            <Card>
              <CardContent>
                <Typography variant="h6">Estado de preparación</Typography>
                {verifactuReadinessQuery.data && (
                  <>
                    <LinearProgress
                      variant="determinate"
                      value={(verifactuReadinessQuery.data.completed / verifactuReadinessQuery.data.total) * 100}
                      sx={{ my: 1.5 }}
                    />
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
                      {verifactuReadinessQuery.data.completed} de {verifactuReadinessQuery.data.total} controles preparados
                    </Typography>
                    <ReadinessList items={verifactuReadinessQuery.data.items} />
                    <Alert severity="info" sx={{ mt: 1.5 }}>{verifactuReadinessQuery.data.legal_notice}</Alert>
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {tab === 3 && (
        <Grid container spacing={1.5}>
          <Grid size={{ xs: 12, lg: 7 }}>
            <Card component="form" onSubmit={(event: FormEvent) => {
              event.preventDefault()
              aiMutation.mutate(ai)
            }}>
              <CardContent>
                <Typography variant="h6">Gobierno del Centro de IA</Typography>
                <Alert severity="info" sx={{ mt: 1.2 }}>
                  Este sprint guarda preferencias, no claves. Tampoco envía todavía datos a ningún proveedor.
                </Alert>
                <Stack spacing={1.3} sx={{ mt: 1.5 }}>
                  <FormControlLabel control={<Switch checked={ai.enabled} onChange={(event) => setAi({ ...ai, enabled: event.target.checked })} />} label="Activar Centro de IA" />
                  <TextField select label="Proveedor" value={ai.provider} onChange={(event) => setAi({ ...ai, provider: event.target.value as AiConfigurationPayload['provider'] })}>
                    <MenuItem value="disabled">Desactivado</MenuItem>
                    <MenuItem value="openai">OpenAI</MenuItem>
                    <MenuItem value="azure_openai">Azure OpenAI</MenuItem>
                    <MenuItem value="local">Modelo local</MenuItem>
                    <MenuItem value="custom">Proveedor compatible</MenuItem>
                  </TextField>
                  <TextField label="Modelo" value={ai.model ?? ''} onChange={(event) => setAi({ ...ai, model: event.target.value })} />
                  <TextField label="Nombre del asistente" value={ai.assistant_name} onChange={(event) => setAi({ ...ai, assistant_name: event.target.value })} />
                  <TextField multiline minRows={5} label="Instrucciones del asistente" value={ai.system_prompt ?? ''} onChange={(event) => setAi({ ...ai, system_prompt: event.target.value })} />
                  <Stack>
                    <FormControlLabel control={<Checkbox checked={ai.allow_customer_data} onChange={(event) => setAi({ ...ai, allow_customer_data: event.target.checked })} />} label="Permitir datos de clientes" />
                    <FormControlLabel control={<Checkbox checked={ai.allow_financial_data} onChange={(event) => setAi({ ...ai, allow_financial_data: event.target.checked })} />} label="Permitir datos financieros" />
                    <FormControlLabel control={<Checkbox checked={ai.allow_document_content} onChange={(event) => setAi({ ...ai, allow_document_content: event.target.checked })} />} label="Permitir contenido de documentos" />
                    <FormControlLabel control={<Checkbox checked={ai.human_review_required} onChange={(event) => setAi({ ...ai, human_review_required: event.target.checked })} />} label="Exigir revisión humana" />
                  </Stack>
                  <TextField type="number" label="Retención de contexto (días)" value={ai.retention_days} onChange={(event) => setAi({ ...ai, retention_days: Number(event.target.value) })} />
                  <TextField multiline minRows={3} label="Notas internas" value={ai.notes ?? ''} onChange={(event) => setAi({ ...ai, notes: event.target.value })} />
                  {aiQuery.data && (
                    <Stack direction="row" spacing={1}>
                      <Chip color={aiQuery.data.api_key_configured ? 'success' : 'default'} label={aiQuery.data.api_key_configured ? 'Clave configurada' : 'Clave no configurada'} />
                      <Chip color={aiQuery.data.base_url_configured ? 'success' : 'default'} label={aiQuery.data.base_url_configured ? 'URL configurada' : 'URL no configurada'} />
                    </Stack>
                  )}
                  {aiMutation.error && <Alert severity="error">{errorMessage(aiMutation.error)}</Alert>}
                  <Button type="submit" variant="contained">Guardar Centro de IA</Button>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, lg: 5 }}>
            <Card>
              <CardContent>
                <Typography variant="h6">Estado de seguridad</Typography>
                {aiReadinessQuery.data && (
                  <>
                    <Chip
                      sx={{ my: 1.3 }}
                      color={aiReadinessQuery.data.ready ? 'success' : 'warning'}
                      label={aiReadinessQuery.data.ready ? 'Preparado' : 'Configuración incompleta'}
                    />
                    <ReadinessList items={aiReadinessQuery.data.items} />
                    <Alert severity="info" sx={{ mt: 1.5 }}>{aiReadinessQuery.data.security_notice}</Alert>
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {tab === 4 && (
        <Card>
          <CardContent>
            <Typography variant="h6">Historial de configuración</Typography>
            <Stack spacing={1} sx={{ mt: 1.5 }}>
              {(eventsQuery.data ?? []).map((event) => (
                <Box key={event.id} sx={{ borderBottom: '1px solid', borderColor: 'divider', pb: 1 }}>
                  <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" gap={0.5}>
                    <Typography fontWeight={700}>{event.summary}</Typography>
                    <Typography variant="caption" color="text.secondary">{new Date(event.created_at).toLocaleString()}</Typography>
                  </Stack>
                  <Typography variant="caption" color="text.secondary">
                    {event.category} · {event.action} · {event.actor?.full_name ?? 'Sistema'}
                  </Typography>
                </Box>
              ))}
              {(eventsQuery.data ?? []).length === 0 && <Alert severity="info">Todavía no hay cambios registrados.</Alert>}
            </Stack>
          </CardContent>
        </Card>
      )}
    </Stack>
  )
}
