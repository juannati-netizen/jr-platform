import AddTaskOutlinedIcon from '@mui/icons-material/AddTaskOutlined'
import AssignmentOutlinedIcon from '@mui/icons-material/AssignmentOutlined'
import NotesOutlinedIcon from '@mui/icons-material/NotesOutlined'
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation, useQuery, useQueryClient, type QueryClient } from '@tanstack/react-query'
import { useMemo, useState, type FormEvent } from 'react'

import { ApiError } from '../api/client'
import { getClients } from '../api/clients'
import type { WorkOrder, WorkOrderPriority, WorkOrderStatus } from '../api/types'
import { getAssignableUsers } from '../api/users'
import {
  addWorkOrderNote,
  createWorkOrder,
  getWorkOrderNotes,
  getWorkOrders,
  updateWorkOrder,
  type WorkOrderInput,
} from '../api/work-orders'
import {
  statusColor,
  workOrderPriorityLabel,
  workOrderPriorityOptions,
  workOrderStatusLabel,
  workOrderStatusOptions,
} from '../utils/work-orders'

const emptyForm: WorkOrderInput = {
  client_id: '',
  title: '',
  description: '',
  status: 'planned',
  priority: 'normal',
  assignee_id: null,
  scheduled_for: null,
}

export function WorkOrdersPage() {
  const queryClient = useQueryClient()
  const [createOpen, setCreateOpen] = useState(false)
  const [selected, setSelected] = useState<WorkOrder | null>(null)
  const [form, setForm] = useState<WorkOrderInput>(emptyForm)
  const [note, setNote] = useState('')

  const workOrdersQuery = useQuery({ queryKey: ['work-orders'], queryFn: getWorkOrders })
  const clientsQuery = useQuery({ queryKey: ['clients', 'active'], queryFn: () => getClients(true) })
  const usersQuery = useQuery({ queryKey: ['assignable-users'], queryFn: getAssignableUsers })
  const notesQuery = useQuery({
    queryKey: ['work-order-notes', selected?.id],
    queryFn: () => getWorkOrderNotes(selected?.id ?? ''),
    enabled: Boolean(selected),
  })

  const createMutation = useMutation({
    mutationFn: createWorkOrder,
    onSuccess: async () => {
      await invalidateOperationalQueries(queryClient)
      setForm(emptyForm)
      setCreateOpen(false)
    },
  })
  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<WorkOrderInput> }) =>
      updateWorkOrder(id, payload),
    onSuccess: async (updated) => {
      setSelected(updated)
      await invalidateOperationalQueries(queryClient)
    },
  })
  const noteMutation = useMutation({
    mutationFn: ({ id, content }: { id: string; content: string }) =>
      addWorkOrderNote(id, content),
    onSuccess: async () => {
      setNote('')
      await queryClient.invalidateQueries({ queryKey: ['work-order-notes', selected?.id] })
      await queryClient.invalidateQueries({ queryKey: ['work-orders'] })
    },
  })

  const activeUsers = useMemo(
    () => usersQuery.data?.filter((user) => user.is_active) ?? [],
    [usersQuery.data],
  )

  const submit = (event: FormEvent) => {
    event.preventDefault()
    createMutation.mutate({
      ...form,
      scheduled_for: form.scheduled_for
        ? new Date(form.scheduled_for).toISOString()
        : null,
    })
  }

  return (
    <Stack spacing={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" spacing={2}>
        <Box>
          <Typography variant="h4">Trabajos</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.75 }}>
            Planifica servicios, asigna responsables y registra el avance operativo.
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<AddTaskOutlinedIcon />} onClick={() => setCreateOpen(true)}>
          Nuevo trabajo
        </Button>
      </Stack>

      {workOrdersQuery.error && (
        <Alert severity="error">
          {workOrdersQuery.error instanceof ApiError
            ? workOrdersQuery.error.message
            : 'No se pudieron cargar los trabajos'}
        </Alert>
      )}

      <Card>
        <CardContent sx={{ p: 0 }}>
          {workOrdersQuery.isLoading && (
            <Stack alignItems="center" spacing={2} sx={{ p: 6 }}>
              <CircularProgress />
              <Typography color="text.secondary">Cargando trabajos…</Typography>
            </Stack>
          )}
          {workOrdersQuery.data && (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Trabajo</TableCell>
                    <TableCell>Cliente</TableCell>
                    <TableCell>Estado</TableCell>
                    <TableCell>Prioridad</TableCell>
                    <TableCell>Responsable</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {workOrdersQuery.data.map((item) => (
                    <TableRow key={item.id} hover onClick={() => setSelected(item)} sx={{ cursor: 'pointer' }}>
                      <TableCell>
                        <Stack direction="row" spacing={1.5} alignItems="center">
                          <AssignmentOutlinedIcon color="action" />
                          <Box>
                            <Typography fontWeight={700}>{item.title}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {item.notes_count} notas
                            </Typography>
                          </Box>
                        </Stack>
                      </TableCell>
                      <TableCell>{item.client.name}</TableCell>
                      <TableCell>
                        <Chip size="small" color={statusColor(item.status)} label={workOrderStatusLabel(item.status)} />
                      </TableCell>
                      <TableCell>{workOrderPriorityLabel(item.priority)}</TableCell>
                      <TableCell>{item.assignee?.full_name ?? 'Sin asignar'}</TableCell>
                    </TableRow>
                  ))}
                  {workOrdersQuery.data.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={5} align="center" sx={{ py: 6 }}>
                        <Typography color="text.secondary">Aún no hay trabajos.</Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} fullWidth maxWidth="sm">
        <Box component="form" onSubmit={submit}>
          <DialogTitle>Nuevo trabajo</DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ pt: 1 }}>
              {createMutation.error && (
                <Alert severity="error">
                  {createMutation.error instanceof ApiError
                    ? createMutation.error.message
                    : 'No se pudo crear el trabajo'}
                </Alert>
              )}
              <FormControl required>
                <InputLabel id="new-client-label">Cliente</InputLabel>
                <Select
                  labelId="new-client-label"
                  label="Cliente"
                  value={form.client_id}
                  onChange={(event) => setForm({ ...form, client_id: event.target.value })}
                >
                  {clientsQuery.data?.map((client) => (
                    <MenuItem key={client.id} value={client.id}>{client.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                label="Título"
                required
                value={form.title}
                onChange={(event) => setForm({ ...form, title: event.target.value })}
              />
              <TextField
                label="Descripción"
                multiline
                minRows={3}
                value={form.description}
                onChange={(event) => setForm({ ...form, description: event.target.value })}
              />
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <FormControl fullWidth>
                  <InputLabel id="new-status-label">Estado</InputLabel>
                  <Select
                    labelId="new-status-label"
                    label="Estado"
                    value={form.status}
                    onChange={(event) => setForm({ ...form, status: event.target.value as WorkOrderStatus })}
                  >
                    {workOrderStatusOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <FormControl fullWidth>
                  <InputLabel id="new-priority-label">Prioridad</InputLabel>
                  <Select
                    labelId="new-priority-label"
                    label="Prioridad"
                    value={form.priority}
                    onChange={(event) => setForm({ ...form, priority: event.target.value as WorkOrderPriority })}
                  >
                    {workOrderPriorityOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Stack>
              <FormControl>
                <InputLabel id="new-assignee-label">Responsable</InputLabel>
                <Select
                  labelId="new-assignee-label"
                  label="Responsable"
                  value={form.assignee_id ?? ''}
                  onChange={(event) => setForm({ ...form, assignee_id: event.target.value || null })}
                >
                  <MenuItem value="">Sin asignar</MenuItem>
                  {activeUsers.map((user) => (
                    <MenuItem key={user.id} value={user.id}>{user.full_name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                label="Fecha prevista"
                type="datetime-local"
                slotProps={{ inputLabel: { shrink: true } }}
                value={form.scheduled_for ?? ''}
                onChange={(event) => setForm({ ...form, scheduled_for: event.target.value || null })}
              />
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateOpen(false)}>Cancelar</Button>
            <Button type="submit" variant="contained" disabled={createMutation.isPending || !form.client_id}>
              Crear trabajo
            </Button>
          </DialogActions>
        </Box>
      </Dialog>

      <Dialog open={Boolean(selected)} onClose={() => setSelected(null)} fullWidth maxWidth="md">
        {selected && (
          <>
            <DialogTitle>{selected.title}</DialogTitle>
            <DialogContent>
              <Stack spacing={3} sx={{ pt: 1 }}>
                <Typography color="text.secondary">{selected.description || 'Sin descripción.'}</Typography>
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                  <FormControl fullWidth>
                    <InputLabel id="detail-status-label">Estado</InputLabel>
                    <Select
                      labelId="detail-status-label"
                      label="Estado"
                      value={selected.status}
                      onChange={(event) =>
                        updateMutation.mutate({
                          id: selected.id,
                          payload: { status: event.target.value as WorkOrderStatus },
                        })
                      }
                    >
                      {workOrderStatusOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <FormControl fullWidth>
                    <InputLabel id="detail-assignee-label">Responsable</InputLabel>
                    <Select
                      labelId="detail-assignee-label"
                      label="Responsable"
                      value={selected.assignee?.id ?? ''}
                      onChange={(event) =>
                        updateMutation.mutate({
                          id: selected.id,
                          payload: { assignee_id: event.target.value || null },
                        })
                      }
                    >
                      <MenuItem value="">Sin asignar</MenuItem>
                      {activeUsers.map((user) => (
                        <MenuItem key={user.id} value={user.id}>{user.full_name}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Stack>
                <Box>
                  <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.5 }}>
                    <NotesOutlinedIcon color="action" />
                    <Typography variant="h6">Notas de seguimiento</Typography>
                  </Stack>
                  <Stack spacing={1.5}>
                    {notesQuery.data?.map((item) => (
                      <Box key={item.id} sx={{ bgcolor: 'background.default', p: 2, borderRadius: 2 }}>
                        <Typography>{item.content}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {item.author.full_name} · {new Date(item.created_at).toLocaleString('es-ES')}
                        </Typography>
                      </Box>
                    ))}
                    {notesQuery.data?.length === 0 && (
                      <Typography color="text.secondary">Todavía no hay notas.</Typography>
                    )}
                  </Stack>
                  <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} sx={{ mt: 2 }}>
                    <TextField
                      fullWidth
                      label="Añadir nota"
                      value={note}
                      onChange={(event) => setNote(event.target.value)}
                    />
                    <Button
                      variant="outlined"
                      disabled={note.trim().length < 2 || noteMutation.isPending}
                      onClick={() => noteMutation.mutate({ id: selected.id, content: note })}
                    >
                      Guardar nota
                    </Button>
                  </Stack>
                </Box>
              </Stack>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelected(null)}>Cerrar</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Stack>
  )
}

async function invalidateOperationalQueries(queryClient: QueryClient) {
  await Promise.all([
    queryClient.invalidateQueries({ queryKey: ['work-orders'] }),
    queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] }),
  ])
}
