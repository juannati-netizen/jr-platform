import AddOutlinedIcon from '@mui/icons-material/AddOutlined'
import PaymentsOutlinedIcon from '@mui/icons-material/PaymentsOutlined'
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
import { getPublicCompanyProfile } from '../api/settings'
import { getClients } from '../api/clients'
import {
  type LineItemInput,
  addInvoicePayment,
  createInvoice,
  getInvoices,
  updateInvoice,
} from '../api/finance'
import type { Invoice, InvoiceStatus, PaymentMethod } from '../api/types'
import { useAuth } from '../auth/AuthContext'
import { LineItemsEditor } from '../components/LineItemsEditor'
import {
  euro,
  invoiceStatusColor,
  invoiceStatusLabel,
  invoiceStatusOptions,
  paymentMethodLabel,
  paymentMethodOptions,
} from '../utils/finance'
import { printFinancialDocument } from '../utils/print-document'

const firstItem: LineItemInput = {
  description: '',
  quantity: '1.00',
  unit_price: '0.00',
  tax_rate: '7.00',
}

export function InvoicesPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [createOpen, setCreateOpen] = useState(false)
  const [selected, setSelected] = useState<Invoice | null>(null)
  const [paymentOpen, setPaymentOpen] = useState(false)
  const [form, setForm] = useState({
    client_id: '',
    due_date: '',
    notes: '',
    items: [{ ...firstItem }],
  })
  const [payment, setPayment] = useState({
    amount: '',
    method: 'bank_transfer' as PaymentMethod,
    reference: '',
    notes: '',
  })

  const invoicesQuery = useQuery({ queryKey: ['invoices'], queryFn: getInvoices })
  const companyQuery = useQuery({ queryKey: ['company-public-profile'], queryFn: getPublicCompanyProfile })
  const clientsQuery = useQuery({ queryKey: ['clients', 'active'], queryFn: () => getClients(true) })

  const refresh = async () => {
    await queryClient.invalidateQueries({ queryKey: ['invoices'] })
    await queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
  }

  const createMutation = useMutation({
    mutationFn: createInvoice,
    onSuccess: async () => {
      setCreateOpen(false)
      setForm({ client_id: '', due_date: '', notes: '', items: [{ ...firstItem }] })
      await refresh()
    },
  })

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: InvoiceStatus }) =>
      updateInvoice(id, { status }),
    onSuccess: async (invoice) => {
      setSelected(invoice)
      await refresh()
    },
  })

  const paymentMutation = useMutation({
    mutationFn: ({ id }: { id: string }) =>
      addInvoicePayment(id, {
        amount: payment.amount,
        method: payment.method,
        reference: payment.reference,
        notes: payment.notes,
      }),
    onSuccess: async (invoice) => {
      setSelected(invoice)
      setPaymentOpen(false)
      setPayment({ amount: '', method: 'bank_transfer', reference: '', notes: '' })
      await refresh()
    },
  })

  const submit = (event: FormEvent) => {
    event.preventDefault()
    createMutation.mutate({
      client_id: form.client_id,
      due_date: form.due_date || null,
      notes: form.notes,
      items: form.items,
    })
  }

  return (
    <Stack spacing={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" spacing={2}>
        <Box>
          <Typography variant="h4">Facturas</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.75 }}>
            Controla la emisión, los cobros y los importes pendientes.
          </Typography>
        </Box>
        {user?.role === 'admin' && (
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={() => setCreateOpen(true)}>
            Nueva factura
          </Button>
        )}
      </Stack>

      {invoicesQuery.error && (
        <Alert severity="error">
          {invoicesQuery.error instanceof ApiError
            ? invoicesQuery.error.message
            : 'No se pudieron cargar las facturas'}
        </Alert>
      )}

      <Card>
        <CardContent sx={{ p: 0 }}>
          {invoicesQuery.isLoading && (
            <Stack alignItems="center" spacing={2} sx={{ p: 6 }}>
              <CircularProgress />
              <Typography color="text.secondary">Cargando facturas…</Typography>
            </Stack>
          )}
          {invoicesQuery.data && (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Número</TableCell>
                    <TableCell>Cliente</TableCell>
                    <TableCell>Estado</TableCell>
                    <TableCell>Vencimiento</TableCell>
                    <TableCell align="right">Total</TableCell>
                    <TableCell align="right">Pendiente</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {invoicesQuery.data.map((invoice) => (
                    <TableRow
                      key={invoice.id}
                      hover
                      onClick={() => setSelected(invoice)}
                      sx={{ cursor: 'pointer' }}
                    >
                      <TableCell>
                        <Stack direction="row" spacing={1.25} alignItems="center">
                          <ReceiptLongOutlinedIcon color="action" />
                          <Typography fontWeight={800}>{invoice.number}</Typography>
                        </Stack>
                      </TableCell>
                      <TableCell>{invoice.client.name}</TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          color={invoiceStatusColor(invoice.status)}
                          label={invoiceStatusLabel(invoice.status)}
                        />
                      </TableCell>
                      <TableCell>
                        {invoice.due_date
                          ? new Date(invoice.due_date).toLocaleDateString('es-ES')
                          : 'Sin fecha'}
                      </TableCell>
                      <TableCell align="right"><strong>{euro(invoice.total)}</strong></TableCell>
                      <TableCell align="right">{euro(invoice.pending_total)}</TableCell>
                    </TableRow>
                  ))}
                  {invoicesQuery.data.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} align="center" sx={{ py: 6 }}>
                        <Typography color="text.secondary">Aún no hay facturas.</Typography>
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
          <DialogTitle>Nueva factura</DialogTitle>
          <DialogContent>
            <Stack spacing={2.5} sx={{ pt: 1 }}>
              {createMutation.error && (
                <Alert severity="error">
                  {createMutation.error instanceof ApiError
                    ? createMutation.error.message
                    : 'No se pudo crear la factura'}
                </Alert>
              )}
              <FormControl required>
                <InputLabel id="invoice-client-label">Cliente</InputLabel>
                <Select
                  labelId="invoice-client-label"
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
                label="Fecha de vencimiento"
                value={form.due_date}
                slotProps={{ inputLabel: { shrink: true } }}
                onChange={(event) => setForm({ ...form, due_date: event.target.value })}
              />
              <TextField
                label="Notas"
                multiline
                minRows={2}
                value={form.notes}
                onChange={(event) => setForm({ ...form, notes: event.target.value })}
              />
              <LineItemsEditor items={form.items} onChange={(items) => setForm({ ...form, items })} />
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateOpen(false)}>Cancelar</Button>
            <Button type="submit" variant="contained" disabled={createMutation.isPending}>
              Crear factura
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
                {statusMutation.error && (
                  <Alert severity="error">
                    {statusMutation.error instanceof ApiError
                      ? statusMutation.error.message
                      : 'No se pudo actualizar la factura'}
                  </Alert>
                )}
                {user?.role === 'admin' && (
                  <FormControl>
                    <InputLabel id="invoice-status-label">Estado</InputLabel>
                    <Select
                      labelId="invoice-status-label"
                      label="Estado"
                      value={selected.status}
                      onChange={(event) =>
                        statusMutation.mutate({
                          id: selected.id,
                          status: event.target.value as InvoiceStatus,
                        })
                      }
                    >
                      {invoiceStatusOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Concepto</TableCell>
                      <TableCell align="right">Cantidad</TableCell>
                      <TableCell align="right">Precio</TableCell>
                      <TableCell align="right">IGIC</TableCell>
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
                  <Typography>Total: {euro(selected.total)}</Typography>
                  <Typography color="success.main">Cobrado: {euro(selected.paid_total)}</Typography>
                  <Typography variant="h6">Pendiente: {euro(selected.pending_total)}</Typography>
                </Stack>
                <Box>
                  <Typography variant="h6" sx={{ mb: 1 }}>Pagos</Typography>
                  {selected.payments.length === 0 && (
                    <Typography color="text.secondary">No se han registrado cobros.</Typography>
                  )}
                  <Stack spacing={1}>
                    {selected.payments.map((item) => (
                      <Stack
                        key={item.id}
                        direction={{ xs: 'column', sm: 'row' }}
                        justifyContent="space-between"
                        sx={{ p: 1.5, bgcolor: 'background.default', borderRadius: 2 }}
                      >
                        <Typography>
                          {new Date(item.paid_at).toLocaleDateString('es-ES')} · {paymentMethodLabel(item.method)}
                        </Typography>
                        <Typography fontWeight={800}>{euro(item.amount)}</Typography>
                      </Stack>
                    ))}
                  </Stack>
                </Box>
              </Stack>
            </DialogContent>
            <DialogActions>
              <Button startIcon={<PrintOutlinedIcon />} onClick={() => printFinancialDocument(selected, companyQuery.data)}>
                Imprimir
              </Button>
              {user?.role === 'admin' && Number(selected.pending_total) > 0 && selected.status !== 'cancelled' && (
                <Button
                  variant="contained"
                  startIcon={<PaymentsOutlinedIcon />}
                  onClick={() => {
                    setPayment({ ...payment, amount: selected.pending_total })
                    setPaymentOpen(true)
                  }}
                >
                  Registrar pago
                </Button>
              )}
              <Button onClick={() => setSelected(null)}>Cerrar</Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      <Dialog open={paymentOpen} onClose={() => setPaymentOpen(false)} fullWidth maxWidth="sm">
        <Box
          component="form"
          onSubmit={(event: FormEvent) => {
            event.preventDefault()
            if (selected) {
              paymentMutation.mutate({ id: selected.id })
            }
          }}
        >
          <DialogTitle>Registrar pago</DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ pt: 1 }}>
              {paymentMutation.error && (
                <Alert severity="error">
                  {paymentMutation.error instanceof ApiError
                    ? paymentMutation.error.message
                    : 'No se pudo registrar el pago'}
                </Alert>
              )}
              <TextField
                required
                type="number"
                label="Importe"
                value={payment.amount}
                slotProps={{ htmlInput: { min: 0.01, step: 0.01 } }}
                onChange={(event) => setPayment({ ...payment, amount: event.target.value })}
              />
              <FormControl>
                <InputLabel id="payment-method-label">Método</InputLabel>
                <Select
                  labelId="payment-method-label"
                  label="Método"
                  value={payment.method}
                  onChange={(event) =>
                    setPayment({ ...payment, method: event.target.value as PaymentMethod })
                  }
                >
                  {paymentMethodOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                label="Referencia"
                value={payment.reference}
                onChange={(event) => setPayment({ ...payment, reference: event.target.value })}
              />
              <TextField
                label="Notas"
                multiline
                minRows={2}
                value={payment.notes}
                onChange={(event) => setPayment({ ...payment, notes: event.target.value })}
              />
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setPaymentOpen(false)}>Cancelar</Button>
            <Button type="submit" variant="contained" disabled={paymentMutation.isPending}>
              Guardar pago
            </Button>
          </DialogActions>
        </Box>
      </Dialog>
    </Stack>
  )
}
