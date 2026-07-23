import AddIcon from '@mui/icons-material/Add'
import AttachFileOutlinedIcon from '@mui/icons-material/AttachFileOutlined'
import DownloadOutlinedIcon from '@mui/icons-material/DownloadOutlined'
import FolderOpenOutlinedIcon from '@mui/icons-material/FolderOpenOutlined'
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
  TextField,
  Typography,
} from '@mui/material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { type FormEvent, useState } from 'react'

import { ApiError } from '../api/client'
import { getClients } from '../api/clients'
import { getOpportunities } from '../api/crm'
import {
  createProject,
  downloadProjectDocument,
  getProjectFile,
  getProjects,
  uploadProjectDocument,
} from '../api/projects'
import type { ProjectInput } from '../api/projects'
import type { Project } from '../api/types'
import { getAssignableUsers } from '../api/users'
import { getWorkOrders } from '../api/work-orders'
import { euro } from '../utils/finance'
import { projectStatuses } from '../utils/crm'

const emptyProject: ProjectInput = {
  name: '',
  client_id: '',
  opportunity_id: null,
  work_order_id: null,
  manager_id: null,
  status: 'planned',
  location: '',
  description: '',
  planned_start: null,
  planned_end: null,
  budget: '0.00',
  notes: '',
}

export function ProjectsPage() {
  const queryClient = useQueryClient()
  const [createOpen, setCreateOpen] = useState(false)
  const [selected, setSelected] = useState<Project | null>(null)
  const [form, setForm] = useState<ProjectInput>(emptyProject)
  const [file, setFile] = useState<File | null>(null)
  const [category, setCategory] = useState('General')

  const projectsQuery = useQuery({ queryKey: ['projects'], queryFn: getProjects })
  const clientsQuery = useQuery({ queryKey: ['clients', true], queryFn: () => getClients(true) })
  const opportunitiesQuery = useQuery({ queryKey: ['crm-opportunities'], queryFn: getOpportunities })
  const workOrdersQuery = useQuery({ queryKey: ['work-orders'], queryFn: getWorkOrders })
  const usersQuery = useQuery({ queryKey: ['assignable-users'], queryFn: getAssignableUsers })
  const fileQuery = useQuery({
    queryKey: ['project-file', selected?.id],
    queryFn: () => getProjectFile(selected!.id),
    enabled: Boolean(selected),
  })

  const createMutation = useMutation({
    mutationFn: createProject,
    onSuccess: async () => {
      setCreateOpen(false)
      setForm(emptyProject)
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['projects'] }),
        queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] }),
      ])
    },
  })
  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!selected || !file) throw new Error('Selecciona un archivo')
      return uploadProjectDocument(selected.id, file, category)
    },
    onSuccess: async () => {
      setFile(null)
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['project-file', selected?.id] }),
        queryClient.invalidateQueries({ queryKey: ['projects'] }),
      ])
    },
  })

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    createMutation.mutate(form)
  }
  const error = createMutation.error ?? uploadMutation.error

  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Box><Typography variant="h5" fontWeight={800}>Obras y expedientes</Typography><Typography color="text.secondary">Expediente digital, documentos y visión financiera por obra.</Typography></Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setCreateOpen(true)}>Nueva obra</Button>
      </Stack>
      {error && <Alert severity="error">{error instanceof ApiError ? error.message : error instanceof Error ? error.message : 'Error'}</Alert>}
      <Grid container spacing={1.5}>
        {(projectsQuery.data ?? []).map((project) => (
          <Grid key={project.id} size={{ xs: 12, md: 6, xl: 4 }}>
            <Card sx={{ height: '100%' }}><CardContent><Stack direction="row" justifyContent="space-between"><Box><Typography variant="caption" color="primary.light">{project.code}</Typography><Typography variant="h6" fontWeight={780}>{project.name}</Typography></Box><Chip size="small" label={projectStatuses.find((x) => x.value === project.status)?.label ?? project.status} /></Stack><Typography variant="body2" color="text.secondary" mt={1}>{project.client.name} · {project.location || 'Sin ubicación'}</Typography><Typography variant="body2" mt={1}>Presupuesto objetivo: {euro(project.budget)}</Typography><Stack direction="row" spacing={1} mt={2}><Button size="small" startIcon={<FolderOpenOutlinedIcon />} onClick={() => setSelected(project)}>Abrir expediente</Button><Chip size="small" icon={<AttachFileOutlinedIcon />} label={`${project.documents_count} documentos`} /></Stack></CardContent></Card>
          </Grid>
        ))}
        {projectsQuery.data?.length === 0 && <Grid size={12}><Alert severity="info">Todavía no hay obras.</Alert></Grid>}
      </Grid>

      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} fullWidth maxWidth="sm"><Box component="form" onSubmit={submit}><DialogTitle>Nueva obra</DialogTitle><DialogContent><Stack spacing={2} pt={1}><TextField required label="Nombre" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /><FormControl required><InputLabel>Cliente</InputLabel><Select label="Cliente" value={form.client_id} onChange={(e) => setForm({ ...form, client_id: e.target.value, work_order_id: null, opportunity_id: null })}>{clientsQuery.data?.map((x) => <MenuItem key={x.id} value={x.id}>{x.name}</MenuItem>)}</Select></FormControl><FormControl><InputLabel>Trabajo relacionado</InputLabel><Select label="Trabajo relacionado" value={form.work_order_id ?? ''} onChange={(e) => setForm({ ...form, work_order_id: e.target.value || null })}><MenuItem value="">Ninguno</MenuItem>{workOrdersQuery.data?.filter((x) => x.client.id === form.client_id).map((x) => <MenuItem key={x.id} value={x.id}>{x.title}</MenuItem>)}</Select></FormControl><FormControl><InputLabel>Oportunidad</InputLabel><Select label="Oportunidad" value={form.opportunity_id ?? ''} onChange={(e) => setForm({ ...form, opportunity_id: e.target.value || null })}><MenuItem value="">Ninguna</MenuItem>{opportunitiesQuery.data?.filter((x) => !x.client || x.client.id === form.client_id).map((x) => <MenuItem key={x.id} value={x.id}>{x.title}</MenuItem>)}</Select></FormControl><FormControl><InputLabel>Responsable</InputLabel><Select label="Responsable" value={form.manager_id ?? ''} onChange={(e) => setForm({ ...form, manager_id: e.target.value || null })}><MenuItem value="">Sin asignar</MenuItem>{usersQuery.data?.map((x) => <MenuItem key={x.id} value={x.id}>{x.full_name}</MenuItem>)}</Select></FormControl><Stack direction="row" spacing={1}><TextField fullWidth type="date" label="Inicio previsto" slotProps={{ inputLabel: { shrink: true } }} value={form.planned_start ?? ''} onChange={(e) => setForm({ ...form, planned_start: e.target.value || null })} /><TextField fullWidth type="date" label="Fin previsto" slotProps={{ inputLabel: { shrink: true } }} value={form.planned_end ?? ''} onChange={(e) => setForm({ ...form, planned_end: e.target.value || null })} /></Stack><TextField type="number" label="Presupuesto objetivo" value={form.budget} onChange={(e) => setForm({ ...form, budget: e.target.value })} /><TextField label="Ubicación" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} /></Stack></DialogContent><DialogActions><Button onClick={() => setCreateOpen(false)}>Cancelar</Button><Button type="submit" variant="contained" disabled={!form.client_id}>Crear</Button></DialogActions></Box></Dialog>

      <Dialog open={Boolean(selected)} onClose={() => setSelected(null)} fullWidth maxWidth="lg"><DialogTitle>{selected?.code} · {selected?.name}</DialogTitle><DialogContent>{fileQuery.isLoading ? <Typography>Cargando expediente…</Typography> : fileQuery.data && <Stack spacing={2}><Grid container spacing={1}>{Object.entries({ 'Presupuestado': fileQuery.data.financial.quoted_total, 'Facturado': fileQuery.data.financial.invoiced_total, 'Cobrado': fileQuery.data.financial.collected_total, 'Gastos': fileQuery.data.financial.expenses_total, 'Materiales': fileQuery.data.financial.material_costs, 'Margen bruto': fileQuery.data.financial.gross_margin }).map(([label, value]) => <Grid key={label} size={{ xs: 6, md: 2 }}><Card variant="outlined"><CardContent><Typography variant="caption">{label}</Typography><Typography fontWeight={800}>{euro(value)}</Typography></CardContent></Card></Grid>)}</Grid><Box><Typography variant="h6">Documentos</Typography><Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} my={1}><Button component="label" variant="outlined" startIcon={<AttachFileOutlinedIcon />}>{file?.name ?? 'Seleccionar archivo'}<input hidden type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} /></Button><TextField size="small" label="Categoría" value={category} onChange={(e) => setCategory(e.target.value)} /><Button variant="contained" disabled={!file || uploadMutation.isPending} onClick={() => uploadMutation.mutate()}>Subir</Button></Stack><Stack spacing={1}>{fileQuery.data.documents.map((doc) => <Box key={doc.id} sx={{ p: 1, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}><Stack direction="row" justifyContent="space-between" alignItems="center"><Box><Typography>{doc.filename}</Typography><Typography variant="caption" color="text.secondary">{doc.category} · {(doc.size_bytes / 1024).toFixed(1)} KB</Typography></Box><Button size="small" startIcon={<DownloadOutlinedIcon />} onClick={() => void downloadProjectDocument(doc)}>Descargar</Button></Stack></Box>)}</Stack></Box><Typography variant="body2" color="text.secondary">{fileQuery.data.quotes.length} presupuestos · {fileQuery.data.invoices.length} facturas · {fileQuery.data.expenses.length} gastos · {fileQuery.data.stock_movements.length} movimientos de material.</Typography></Stack>}</DialogContent><DialogActions><Button onClick={() => setSelected(null)}>Cerrar</Button></DialogActions></Dialog>
    </Stack>
  )
}
