import AddOutlinedIcon from '@mui/icons-material/AddOutlined'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import PrintOutlinedIcon from '@mui/icons-material/PrintOutlined'
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined'
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
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { type FormEvent, useState } from 'react'

import { ApiError } from '../api/client'
import { getClients } from '../api/clients'
import {
  type LineItemInput,
  convertQuoteToInvoice,
  createQuote,
  getQuotes,
  updateQuote,
} from '../api/finance'
import type { Quote, QuoteStatus } from '../api/types'
import { useAuth } from '../auth/AuthContext'
import { LineItemsEditor } from '../components/LineItemsEditor'
import {
  euro,
  quoteStatusColor,
  quoteStatusLabel,
  quoteStatusOptions,
} from '../utils/finance'
import { printFinancialDocument } from '../utils/print-document'

const firstItem: LineItemInput = {
  description: '',
  quantity: '1.00',
  unit_price: '0.00',
  tax_rate: '21.00',
}

export function QuotesPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [createOpen, setCreateOpen] = useState(false)
  const [selected, setSelected] = useState<Quote | null>(null)
  const [dueDate, setDueDate] = useState('')
  const [form, setForm] = useState({
    client_id: '',
    valid_until: '',
    notes: '',
    items: [{ ...firstItem }],
  })

  const quotesQuery = useQuery({ queryKey: ['quotes'], queryFn: getQuotes })
  const clientsQuery = useQuery({ queryKey: ['clients', 'active'], queryFn: () => getClients(true) })

  const refresh = async () => {
    await queryClient.invalidateQueries({ queryKey: ['quotes'] })
    await queryClient.invalidateQueries({ queryKey: ['invoices'] })
    await queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
  }

  const createMutation = useMutation({
    mutationFn: createQuote,
    onSuccess: async () => {
      setCreateOpen(false)
      setForm({ client_id: '', valid_until: '', notes: '', items: [{ ...firstItem }] })
      await refresh()
    },
  })

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: QuoteStatus }) =>
      updateQuote(id, { status }),
    onSuccess: async (quote) => {
      setSelected(quote)
      await refresh()
    },
  })

  const convertMutation = useMutation({
    mutationFn: ({ id, date }: { id: string; date?: string }) =>
      convertQuoteToInvoice(id, date),
    onSuccess: async () => {
      setSelected(null)
      setDueDate('')
      await refresh()
    },
  })

  const operationError = statusMutation.error ?? convertMutation.error

  const submit = (event: FormEvent) => {
    event.preventDefault()
    createMutation.mutate({
      client_id: form.client_id,
      valid_until: form.valid_until || null,
      notes: form.notes,
      items: form.items,
    })
  }

  return (
    <Stack spacing={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" spacing={2}>
        <Box>
          <Typography variant="h4">Presupuestos</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.75 }}>
            Crea propuestas económicas, controla su aceptación y conviértelas en factura.
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={() => setCreateOpen(true)}>
          Nuevo presupuesto
        </Button>
      </Stack>

      {quotesQuery.error && (
        <Alert severity="error">
          {quotesQuery.error instanceof ApiError
            ? quotesQuery.error.message
            : 'No se pudieron cargar los presupuestos'}
        </Alert>
      )}

      <Card>
        <CardContent sx={{ p: 0 }}>
          {quotesQuery.isLoading && (
            <Stack alignItems="center" spacing={2} sx={{ p: 6 }}>
              <CircularProgress />
              <Typography color="text.secondary">Cargando presupuestos…</Typography>
            </Stack>
          )}
          {quotesQuery.data && (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Número</TableCell>
                    <TableCell>Cliente</TableCell>
                    <TableCell>Estado</TableCell>
                    <TableCell>Emisión</TableCell>
                    <TableCell align="right">Total</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {quotesQuery.data.map((quote) => (
                    <TableRow
                      key={quote.id}
                      hover
                      onClick={() => setSelected(quote)}
                      sx={{ cursor: 'pointer' }}
                    >
                      <TableCell>
                        <Stack direction="row" spacing={1.25} alignItems="center">
                          <DescriptionOutlinedIcon color="action" />
                          <Typography fontWeight={800}>{quote.number}</Typography>
                        </Stack>
                      </TableCell>
                      <TableCell>{quote.client.name}</TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          color={quoteStatusColor(quote.status)}
                          label={quoteStatusLabel(quote.status)}
                        />
                      </TableCell>
                      <TableCell>{new Date(quote.issue_date).toLocaleDateString('es-ES')}</TableCell>
                      <TableCell align="right"><strong>{euro(quote.total)}</strong></TableCell>
                    </TableRow>
                  ))}
                  {quotesQuery.data.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={5} align="center" sx={{ py: 6 }}>
                        <Typography color="text.secondary">Aún no hay presupuestos.</Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} fullWidth maxWidth="md">
        <Box component="form" onSubmit={submit}>
          <DialogTitle>Nuevo presupuesto</DialogTitle>
          <DialogContent>
            <Stack spacing={2.5} sx={{ pt: 1 }}>
              {createMutation.error && (
                <Alert severity="error">
                  {createMutation.error instanceof ApiError
                    ? createMutation.error.message
                    : 'No se pudo crear el presupuesto'}
                </Alert>
              )}
              <FormControl required>
                <InputLabel id="quote-client-label">Cliente</InputLabel>
                <Select
                  labelId="quote-client-label"
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
                type="date"
                label="Válido hasta"
                value={form.valid_until}
                slotProps={{ inputLabel: { shrink: true } }}
                onChange={(event) => setForm({ ...form, valid_until: event.target.value })}
              />
              <TextField
                label="Notas"
                multiline
                minRows={2}
                value={form.notes}
                onChange={(event) => setForm({ ...form, notes: event.target.value })}
              />
              <LineItemsEditor
                items={form.items}
                onChange={(items) => setForm({ ...form, items })}
              />
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateOpen(false)}>Cancelar</Button>
            <Button type="submit" variant="contained" disabled={createMutation.isPending}>
              Crear presupuesto
            </Button>
          </DialogActions>
        </Box>
      </Dialog>

      <Dialog open={Boolean(selected)} onClose={() => setSelected(null)} fullWidth maxWidth="md">
        {selected && (
          <>
            <DialogTitle>{selected.number} · {selected.client.name}</DialogTitle>
            <DialogContent>
              <Stack spacing={2.5} sx={{ pt: 1 }}>
                {operationError && (
                  <Alert severity="error">
                    {operationError instanceof ApiError
                      ? operationError.message
                      : 'No se pudo completar la operación'}
                  </Alert>
                )}
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                  <FormControl fullWidth>
                    <InputLabel id="quote-status-label">Estado</InputLabel>
                    <Select
                      labelId="quote-status-label"
                      label="Estado"
                      value={selected.status}
                      onChange={(event) =>
                        statusMutation.mutate({
                          id: selected.id,
                          status: event.target.value as QuoteStatus,
                        })
                      }
                    >
                      {quoteStatusOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  {user?.role === 'admin' && selected.status === 'accepted' && !selected.invoice_id && (
                    <TextField
                      fullWidth
                      type="date"
                      label="Vencimiento de factura"
                      value={dueDate}
                      slotProps={{ inputLabel: { shrink: true } }}
                      onChange={(event) => setDueDate(event.target.value)}
                    />
                  )}
                </Stack>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Concepto</TableCell>
                      <TableCell align="right">Cantidad</TableCell>
                      <TableCell align="right">Precio</TableCell>
                      <TableCell align="right">IVA</TableCell>
                      <TableCell align="right">Total</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {selected.items.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>{item.description}</TableCell>
                        <TableCell align="right">{item.quantity}</TableCell>
                        <TableCell align="right">{euro(item.unit_price)}</TableCell>
                        <TableCell align="right">{item.tax_rate}%</TableCell>
                        <TableCell align="right">{euro(item.line_total)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                <Stack alignItems="flex-end" spacing={0.5}>
                  <Typography>Base: {euro(selected.subtotal)}</Typography>
                  <Typography>IVA: {euro(selected.tax_total)}</Typography>
                  <Typography variant="h6">Total: {euro(selected.total)}</Typography>
                </Stack>
                {selected.notes && <Alert severity="info">{selected.notes}</Alert>}
              </Stack>
            </DialogContent>
            <DialogActions>
              <Button startIcon={<PrintOutlinedIcon />} onClick={() => printFinancialDocument(selected)}>
                Imprimir
              </Button>
              {user?.role === 'admin' && selected.status === 'accepted' && !selected.invoice_id && (
                <Button
                  variant="contained"
                  startIcon={<ReceiptLongOutlinedIcon />}
                  disabled={convertMutation.isPending}
                  onClick={() => convertMutation.mutate({ id: selected.id, date: dueDate || undefined })}
                >
                  Convertir en factura
                </Button>
              )}
              <Button onClick={() => setSelected(null)}>Cerrar</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Stack>
  )
}
