import AddIcon from '@mui/icons-material/Add'
import AssignmentTurnedInOutlinedIcon from '@mui/icons-material/AssignmentTurnedInOutlined'
import PersonAddAltOutlinedIcon from '@mui/icons-material/PersonAddAltOutlined'
import RequestQuoteOutlinedIcon from '@mui/icons-material/RequestQuoteOutlined'
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
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { type FormEvent, useMemo, useState } from 'react'

import { ApiError } from '../api/client'
import { getClients } from '../api/clients'
import {
  convertLeadToClient,
  convertOpportunityToQuote,
  createCrmActivity,
  createLead,
  createOpportunity,
  getCrmActivities,
  getCrmSummary,
  getLeads,
  getOpportunities,
  updateCrmActivity,
  updateOpportunity,
} from '../api/crm'
import type {
  CrmActivityInput,
  LeadInput,
  OpportunityInput,
} from '../api/crm'
import type { OpportunityStage } from '../api/types'
import { getAssignableUsers } from '../api/users'
import { euro } from '../utils/finance'
import {
  activityTypes,
  leadSources,
  leadStatuses,
  opportunityStageLabel,
  opportunityStages,
} from '../utils/crm'

const emptyLead: LeadInput = {
  name: '',
  company: '',
  email: '',
  phone: '',
  source: 'other',
  status: 'new',
  owner_id: null,
  notes: '',
}

const emptyOpportunity: OpportunityInput = {
  title: '',
  client_id: null,
  lead_id: null,
  owner_id: null,
  stage: 'prospecting',
  estimated_value: '0.00',
  probability: 10,
  expected_close: null,
  notes: '',
}

const emptyActivity: CrmActivityInput = {
  lead_id: null,
  opportunity_id: null,
  assigned_to_id: null,
  activity_type: 'task',
  subject: '',
  due_at: null,
  notes: '',
}

export function CrmPage() {
  const queryClient = useQueryClient()
  const [tab, setTab] = useState(0)
  const [leadOpen, setLeadOpen] = useState(false)
  const [opportunityOpen, setOpportunityOpen] = useState(false)
  const [activityOpen, setActivityOpen] = useState(false)
  const [leadForm, setLeadForm] = useState<LeadInput>(emptyLead)
  const [opportunityForm, setOpportunityForm] = useState<OpportunityInput>(emptyOpportunity)
  const [activityForm, setActivityForm] = useState<CrmActivityInput>(emptyActivity)

  const leadsQuery = useQuery({ queryKey: ['crm-leads'], queryFn: getLeads })
  const opportunitiesQuery = useQuery({ queryKey: ['crm-opportunities'], queryFn: getOpportunities })
  const activitiesQuery = useQuery({ queryKey: ['crm-activities'], queryFn: getCrmActivities })
  const summaryQuery = useQuery({ queryKey: ['crm-summary'], queryFn: getCrmSummary })
  const clientsQuery = useQuery({ queryKey: ['clients', true], queryFn: () => getClients(true) })
  const usersQuery = useQuery({ queryKey: ['assignable-users'], queryFn: getAssignableUsers })

  const refresh = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['crm-leads'] }),
      queryClient.invalidateQueries({ queryKey: ['crm-opportunities'] }),
      queryClient.invalidateQueries({ queryKey: ['crm-activities'] }),
      queryClient.invalidateQueries({ queryKey: ['crm-summary'] }),
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] }),
      queryClient.invalidateQueries({ queryKey: ['clients'] }),
      queryClient.invalidateQueries({ queryKey: ['quotes'] }),
    ])
  }

  const leadMutation = useMutation({
    mutationFn: createLead,
    onSuccess: async () => { setLeadOpen(false); setLeadForm(emptyLead); await refresh() },
  })
  const opportunityMutation = useMutation({
    mutationFn: createOpportunity,
    onSuccess: async () => { setOpportunityOpen(false); setOpportunityForm(emptyOpportunity); await refresh() },
  })
  const activityMutation = useMutation({
    mutationFn: createCrmActivity,
    onSuccess: async () => { setActivityOpen(false); setActivityForm(emptyActivity); await refresh() },
  })
  const stageMutation = useMutation({
    mutationFn: ({ id, stage }: { id: string; stage: OpportunityStage }) =>
      updateOpportunity(id, { stage, change_source: 'kanban' }),
    onSuccess: refresh,
  })
  const conversionMutation = useMutation({
    mutationFn: ({ kind, id }: { kind: 'lead' | 'quote'; id: string }) =>
      kind === 'lead' ? convertLeadToClient(id) : convertOpportunityToQuote(id),
    onSuccess: refresh,
  })
  const activityCompleteMutation = useMutation({
    mutationFn: (id: string) => updateCrmActivity(id, { completed: true }),
    onSuccess: refresh,
  })

  const error = [leadMutation.error, opportunityMutation.error, activityMutation.error,
    stageMutation.error, conversionMutation.error, activityCompleteMutation.error]
    .find(Boolean)

  const byStage = useMemo(() => {
    const map = new Map<OpportunityStage, NonNullable<typeof opportunitiesQuery.data>>()
    for (const stage of opportunityStages) map.set(stage.value, [])
    for (const item of opportunitiesQuery.data ?? []) map.get(item.stage)?.push(item)
    return map
  }, [opportunitiesQuery.data])

  return (
    <Stack spacing={2}>
      <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" gap={1}>
        <Box>
          <Typography variant="h5" fontWeight={800}>CRM comercial</Typography>
          <Typography color="text.secondary">Leads, oportunidades, actividades y pipeline.</Typography>
        </Box>
        <Stack direction="row" spacing={1} flexWrap="wrap">
          <Button startIcon={<PersonAddAltOutlinedIcon />} variant="outlined" onClick={() => setLeadOpen(true)}>Nuevo lead</Button>
          <Button startIcon={<AddIcon />} variant="contained" onClick={() => setOpportunityOpen(true)}>Nueva oportunidad</Button>
          <Button startIcon={<AssignmentTurnedInOutlinedIcon />} variant="outlined" onClick={() => setActivityOpen(true)}>Nueva actividad</Button>
        </Stack>
      </Stack>

      {error && <Alert severity="error">{error instanceof ApiError ? error.message : 'No se pudo completar la operación'}</Alert>}

      <Grid container spacing={1.2}>
        {[
          ['Leads', summaryQuery.data?.total_leads ?? 0],
          ['Oportunidades abiertas', summaryQuery.data?.open_opportunities ?? 0],
          ['Pipeline', euro(summaryQuery.data?.pipeline_value ?? '0')],
          ['Pipeline ponderado', euro(summaryQuery.data?.weighted_pipeline ?? '0')],
          ['Actividades pendientes', summaryQuery.data?.pending_activities ?? 0],
          ['Ganadas', summaryQuery.data?.won_opportunities ?? 0],
        ].map(([label, value]) => (
          <Grid key={String(label)} size={{ xs: 6, md: 2 }}>
            <Card><CardContent><Typography variant="caption" color="text.secondary">{label}</Typography><Typography variant="h6" fontWeight={800}>{value}</Typography></CardContent></Card>
          </Grid>
        ))}
      </Grid>

      <Card>
        <Tabs value={tab} onChange={(_, value: number) => setTab(value)}>
          <Tab label="Pipeline Kanban" />
          <Tab label="Leads" />
          <Tab label="Actividades" />
        </Tabs>
        <CardContent>
          {tab === 0 && (
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: 'repeat(6, minmax(210px, 1fr))' }, gap: 1, overflowX: 'auto' }}>
              {opportunityStages.map((stage) => (
                <Box key={stage.value} sx={{ bgcolor: '#16212b', border: '1px solid', borderColor: 'divider', borderRadius: 1, p: 1, minHeight: 280 }}>
                  <Stack direction="row" justifyContent="space-between" mb={1}>
                    <Typography fontWeight={750} variant="subtitle2">{stage.label}</Typography>
                    <Chip size="small" label={byStage.get(stage.value)?.length ?? 0} />
                  </Stack>
                  <Stack spacing={1}>
                    {(byStage.get(stage.value) ?? []).map((item) => (
                      <Card key={item.id} variant="outlined" sx={{ bgcolor: '#202c38' }}>
                        <CardContent sx={{ p: '10px !important' }}>
                          <Typography fontWeight={750} variant="body2">{item.title}</Typography>
                          <Typography variant="caption" color="text.secondary" display="block">{item.client?.name ?? item.lead?.company ?? item.lead?.name ?? 'Sin contacto'}</Typography>
                          <Typography variant="body2" mt={0.5}>{euro(item.estimated_value)} · {item.probability}%</Typography>
                          <FormControl fullWidth size="small" sx={{ mt: 1 }}>
                            <Select value={item.stage} onChange={(event) => stageMutation.mutate({ id: item.id, stage: event.target.value as OpportunityStage })}>
                              {opportunityStages.map((option) => <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>)}
                            </Select>
                          </FormControl>
                          {item.client && !item.quote_id && item.stage !== 'lost' && (
                            <Button size="small" startIcon={<RequestQuoteOutlinedIcon />} sx={{ mt: 0.5 }} onClick={() => conversionMutation.mutate({ kind: 'quote', id: item.id })}>Crear presupuesto</Button>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </Stack>
                </Box>
              ))}
            </Box>
          )}
          {tab === 1 && (
            <Stack spacing={1}>
              {(leadsQuery.data ?? []).map((lead) => (
                <Box key={lead.id} sx={{ p: 1.5, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                  <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" gap={1}>
                    <Box><Typography fontWeight={750}>{lead.company || lead.name}</Typography><Typography variant="body2" color="text.secondary">{lead.name} · {lead.email || lead.phone || 'Sin contacto'}</Typography></Box>
                    <Stack direction="row" spacing={1} alignItems="center"><Chip size="small" label={leadStatuses.find((item) => item.value === lead.status)?.label ?? lead.status} />{!lead.converted_client && <Button size="small" onClick={() => conversionMutation.mutate({ kind: 'lead', id: lead.id })}>Convertir en cliente</Button>}</Stack>
                  </Stack>
                </Box>
              ))}
            </Stack>
          )}
          {tab === 2 && (
            <Stack spacing={1}>
              {(activitiesQuery.data ?? []).map((activity) => (
                <Box key={activity.id} sx={{ p: 1.5, border: '1px solid', borderColor: 'divider', borderRadius: 1, opacity: activity.completed ? 0.65 : 1 }}>
                  <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" gap={1}>
                    <Box><Typography fontWeight={750}>{activity.subject}</Typography><Typography variant="caption" color="text.secondary">{activityTypes.find((item) => item.value === activity.activity_type)?.label} · {activity.due_at ? new Date(activity.due_at).toLocaleString('es-ES') : 'Sin fecha'}</Typography></Box>
                    {!activity.completed && <Button size="small" onClick={() => activityCompleteMutation.mutate(activity.id)}>Completar</Button>}
                  </Stack>
                </Box>
              ))}
            </Stack>
          )}
        </CardContent>
      </Card>

      <LeadDialog open={leadOpen} form={leadForm} setForm={setLeadForm} onClose={() => setLeadOpen(false)} onSubmit={(event: FormEvent<HTMLFormElement>) => { event.preventDefault(); leadMutation.mutate(leadForm) }} users={usersQuery.data ?? []} />
      <OpportunityDialog open={opportunityOpen} form={opportunityForm} setForm={setOpportunityForm} onClose={() => setOpportunityOpen(false)} onSubmit={(event: FormEvent<HTMLFormElement>) => { event.preventDefault(); opportunityMutation.mutate(opportunityForm) }} clients={clientsQuery.data ?? []} leads={leadsQuery.data ?? []} users={usersQuery.data ?? []} />
      <ActivityDialog open={activityOpen} form={activityForm} setForm={setActivityForm} onClose={() => setActivityOpen(false)} onSubmit={(event: FormEvent<HTMLFormElement>) => { event.preventDefault(); activityMutation.mutate(activityForm) }} leads={leadsQuery.data ?? []} opportunities={opportunitiesQuery.data ?? []} users={usersQuery.data ?? []} />
    </Stack>
  )
}

function LeadDialog({ open, form, setForm, onClose, onSubmit, users }: any) {
  return <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm"><Box component="form" onSubmit={onSubmit}><DialogTitle>Nuevo lead</DialogTitle><DialogContent><Stack spacing={2} pt={1}><TextField required label="Nombre" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /><TextField label="Empresa" value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} /><Stack direction="row" spacing={1}><TextField fullWidth label="Correo" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /><TextField fullWidth label="Teléfono" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></Stack><Stack direction="row" spacing={1}><FormControl fullWidth><InputLabel>Origen</InputLabel><Select label="Origen" value={form.source} onChange={(e) => setForm({ ...form, source: e.target.value })}>{leadSources.map((x) => <MenuItem key={x.value} value={x.value}>{x.label}</MenuItem>)}</Select></FormControl><FormControl fullWidth><InputLabel>Responsable</InputLabel><Select label="Responsable" value={form.owner_id ?? ''} onChange={(e) => setForm({ ...form, owner_id: e.target.value || null })}><MenuItem value="">Sin asignar</MenuItem>{users.map((u: any) => <MenuItem key={u.id} value={u.id}>{u.full_name}</MenuItem>)}</Select></FormControl></Stack><TextField multiline minRows={2} label="Notas" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></Stack></DialogContent><DialogActions><Button onClick={onClose}>Cancelar</Button><Button type="submit" variant="contained">Crear</Button></DialogActions></Box></Dialog>
}

function OpportunityDialog({ open, form, setForm, onClose, onSubmit, clients, leads, users }: any) {
  return <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm"><Box component="form" onSubmit={onSubmit}><DialogTitle>Nueva oportunidad</DialogTitle><DialogContent><Stack spacing={2} pt={1}><TextField required label="Título" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /><FormControl><InputLabel>Cliente</InputLabel><Select label="Cliente" value={form.client_id ?? ''} onChange={(e) => setForm({ ...form, client_id: e.target.value || null })}><MenuItem value="">Sin cliente</MenuItem>{clients.map((x: any) => <MenuItem key={x.id} value={x.id}>{x.name}</MenuItem>)}</Select></FormControl><FormControl><InputLabel>Lead</InputLabel><Select label="Lead" value={form.lead_id ?? ''} onChange={(e) => setForm({ ...form, lead_id: e.target.value || null })}><MenuItem value="">Sin lead</MenuItem>{leads.map((x: any) => <MenuItem key={x.id} value={x.id}>{x.company || x.name}</MenuItem>)}</Select></FormControl><Stack direction="row" spacing={1}><TextField fullWidth type="number" label="Valor estimado" value={form.estimated_value} onChange={(e) => setForm({ ...form, estimated_value: e.target.value })} /><TextField fullWidth type="number" label="Probabilidad %" value={form.probability} onChange={(e) => setForm({ ...form, probability: Number(e.target.value) })} /></Stack><FormControl><InputLabel>Etapa</InputLabel><Select label="Etapa" value={form.stage} onChange={(e) => setForm({ ...form, stage: e.target.value })}>{opportunityStages.map((x) => <MenuItem key={x.value} value={x.value}>{x.label}</MenuItem>)}</Select></FormControl><TextField type="date" label="Cierre previsto" slotProps={{ inputLabel: { shrink: true } }} value={form.expected_close ?? ''} onChange={(e) => setForm({ ...form, expected_close: e.target.value || null })} /><FormControl><InputLabel>Responsable</InputLabel><Select label="Responsable" value={form.owner_id ?? ''} onChange={(e) => setForm({ ...form, owner_id: e.target.value || null })}><MenuItem value="">Sin asignar</MenuItem>{users.map((u: any) => <MenuItem key={u.id} value={u.id}>{u.full_name}</MenuItem>)}</Select></FormControl></Stack></DialogContent><DialogActions><Button onClick={onClose}>Cancelar</Button><Button type="submit" variant="contained">Crear</Button></DialogActions></Box></Dialog>
}

function ActivityDialog({ open, form, setForm, onClose, onSubmit, leads, opportunities, users }: any) {
  return <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm"><Box component="form" onSubmit={onSubmit}><DialogTitle>Nueva actividad</DialogTitle><DialogContent><Stack spacing={2} pt={1}><TextField required label="Asunto" value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} /><FormControl><InputLabel>Tipo</InputLabel><Select label="Tipo" value={form.activity_type} onChange={(e) => setForm({ ...form, activity_type: e.target.value })}>{activityTypes.map((x) => <MenuItem key={x.value} value={x.value}>{x.label}</MenuItem>)}</Select></FormControl><FormControl><InputLabel>Oportunidad</InputLabel><Select label="Oportunidad" value={form.opportunity_id ?? ''} onChange={(e) => setForm({ ...form, opportunity_id: e.target.value || null, lead_id: null })}><MenuItem value="">Ninguna</MenuItem>{opportunities.map((x: any) => <MenuItem key={x.id} value={x.id}>{x.title}</MenuItem>)}</Select></FormControl><FormControl><InputLabel>Lead</InputLabel><Select label="Lead" value={form.lead_id ?? ''} onChange={(e) => setForm({ ...form, lead_id: e.target.value || null, opportunity_id: null })}><MenuItem value="">Ninguno</MenuItem>{leads.map((x: any) => <MenuItem key={x.id} value={x.id}>{x.company || x.name}</MenuItem>)}</Select></FormControl><TextField type="datetime-local" label="Fecha" slotProps={{ inputLabel: { shrink: true } }} value={form.due_at ?? ''} onChange={(e) => setForm({ ...form, due_at: e.target.value || null })} /><FormControl><InputLabel>Asignada a</InputLabel><Select label="Asignada a" value={form.assigned_to_id ?? ''} onChange={(e) => setForm({ ...form, assigned_to_id: e.target.value || null })}><MenuItem value="">Sin asignar</MenuItem>{users.map((u: any) => <MenuItem key={u.id} value={u.id}>{u.full_name}</MenuItem>)}</Select></FormControl></Stack></DialogContent><DialogActions><Button onClick={onClose}>Cancelar</Button><Button type="submit" variant="contained" disabled={!form.lead_id && !form.opportunity_id}>Crear</Button></DialogActions></Box></Dialog>
}
