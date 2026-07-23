import AddCardOutlinedIcon from '@mui/icons-material/AddCardOutlined'
import PaidOutlinedIcon from '@mui/icons-material/PaidOutlined'
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
import { useState, type FormEvent } from 'react'

import { ApiError } from '../api/client'
import {
  createExpense,
  getExpenses,
  getSuppliers,
  updateExpense,
  type ExpenseInput,
} from '../api/procurement'
import type { ExpenseCategory, ExpenseStatus } from '../api/types'
import { getWorkOrders } from '../api/work-orders'
import { euro } from '../utils/finance'
import {
  expenseCategoryLabel,
  expenseCategoryOptions,
  expenseStatusColor,
  expenseStatusLabel,
  expenseStatusOptions,
} from '../utils/procurement'

function today(): string {
  return new Date().toISOString().slice(0, 10)
}

const emptyForm: ExpenseInput = {
  supplier_id: '',
  work_order_id: '',
  description: '',
  category: 'materials',
  status: 'pending',
  expense_date: today(),
  subtotal: '',
  tax_rate: '21.00',
  reference: '',
  notes: '',
}

export function ExpensesPage() {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState<ExpenseInput>(emptyForm)
  const expensesQuery = useQuery({ queryKey: ['expenses'], queryFn: getExpenses })
  const suppliersQuery = useQuery({
    queryKey: ['suppliers', 'active'],
    queryFn: () => getSuppliers(true),
  })
  const workOrdersQuery = useQuery({ queryKey: ['work-orders'], queryFn: getWorkOrders })

  const invalidate = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['expenses'] }),
      queryClient.invalidateQueries({ queryKey: ['profitability-summary'] }),
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] }),
    ])
  }

  const createMutation = useMutation({
    mutationFn: createExpense,
    onSuccess: async () => {
      await invalidate()
      setForm({ ...emptyForm, expense_date: today() })
      setOpen(false)
    },
  })
  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: ExpenseStatus }) =>
      updateExpense(id, { status }),
    onSuccess: invalidate,
  })

  const submit = (event: FormEvent) => {
    event.preventDefault()
    createMutation.mutate({
      ...form,
      supplier_id: form.supplier_id || null,
      work_order_id: form.work_order_id || null,
    })
  }

  return (
    <Stack spacing={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" spacing={2}>
        <Box>
          <Typography variant="h4">Gastos y compras</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.75 }}>
            Costes de materiales, subcontratas y servicios vinculados a la operación.
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddCardOutlinedIcon />}
          onClick={() => setOpen(true)}
        >
          Registrar gasto
        </Button>
      </Stack>

      {expensesQuery.error && (
        <Alert severity="error">
          {expensesQuery.error instanceof ApiError
            ? expensesQuery.error.message
            : 'No se pudieron cargar los gastos'}
        </Alert>
      )}

      <Card>
        <CardContent sx={{ p: 0 }}>
          {expensesQuery.isLoading && (
            <Stack alignItems="center" spacing={2} sx={{ p: 6 }}>
              <CircularProgress />
              <Typography color="text.secondary">Cargando gastos…</Typography>
            </Stack>
          )}
          {expensesQuery.data && (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Fecha</TableCell>
                    <TableCell>Concepto</TableCell>
                    <TableCell>Proveedor / trabajo</TableCell>
                    <TableCell>Categoría</TableCell>
                    <TableCell align="right">Total</TableCell>
                    <TableCell>Estado</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {expensesQuery.data.map((expense) => (
                    <TableRow key={expense.id} hover>
                      <TableCell>
                        {new Intl.DateTimeFormat('es-ES').format(new Date(expense.expense_date))}
                      </TableCell>
                      <TableCell>
                        <Typography fontWeight={700}>{expense.description}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {expense.reference ?? 'Sin referencia'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{expense.supplier?.name ?? '—'}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {expense.work_order
                            ? `${expense.work_order.title} · ${expense.work_order.client_name}`
                            : 'Sin trabajo asociado'}
                        </Typography>
                      </TableCell>
                      <TableCell>{expenseCategoryLabel(expense.category)}</TableCell>
                      <TableCell align="right">
                        <Typography fontWeight={800}>{euro(expense.total)}</Typography>
                      </TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1} alignItems="center">
                          <Chip
                            size="small"
                            color={expenseStatusColor(expense.status)}
                            label={expenseStatusLabel(expense.status)}
                          />
                          {expense.status === 'pending' && (
                            <Button
                              size="small"
                              startIcon={<PaidOutlinedIcon />}
                              disabled={statusMutation.isPending}
                              onClick={() => statusMutation.mutate({ id: expense.id, status: 'paid' })}
                            >
                              Pagar
                            </Button>
                          )}
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                  {expensesQuery.data.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} align="center" sx={{ py: 6 }}>
                        <Typography color="text.secondary">Aún no hay gastos.</Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="md">
        <Box component="form" onSubmit={submit}>
          <DialogTitle>Registrar gasto</DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ pt: 1 }}>
              {createMutation.error && (
                <Alert severity="error">
                  {createMutation.error instanceof ApiError
                    ? createMutation.error.message
                    : 'No se pudo registrar el gasto'}
                </Alert>
              )}
              <TextField
                label="Concepto"
                required
                value={form.description}
                onChange={(event) => setForm({ ...form, description: event.target.value })}
              />
              <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
                <FormControl fullWidth>
                  <InputLabel id="supplier-label">Proveedor</InputLabel>
                  <Select
                    labelId="supplier-label"
                    label="Proveedor"
                    value={form.supplier_id ?? ''}
                    onChange={(event) => setForm({ ...form, supplier_id: event.target.value })}
                  >
                    <MenuItem value="">Sin proveedor</MenuItem>
                    {suppliersQuery.data?.map((supplier) => (
                      <MenuItem key={supplier.id} value={supplier.id}>{supplier.name}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <FormControl fullWidth>
                  <InputLabel id="work-order-label">Trabajo</InputLabel>
                  <Select
                    labelId="work-order-label"
                    label="Trabajo"
                    value={form.work_order_id ?? ''}
                    onChange={(event) => setForm({ ...form, work_order_id: event.target.value })}
                  >
                    <MenuItem value="">Sin trabajo</MenuItem>
                    {workOrdersQuery.data?.map((workOrder) => (
                      <MenuItem key={workOrder.id} value={workOrder.id}>
                        {workOrder.title} · {workOrder.client.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Stack>
              <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
                <FormControl fullWidth>
                  <InputLabel id="category-label">Categoría</InputLabel>
                  <Select
                    labelId="category-label"
                    label="Categoría"
                    value={form.category}
                    onChange={(event) =>
                      setForm({ ...form, category: event.target.value as ExpenseCategory })}
                  >
                    {expenseCategoryOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <FormControl fullWidth>
                  <InputLabel id="expense-status-label">Estado</InputLabel>
                  <Select
                    labelId="expense-status-label"
                    label="Estado"
                    value={form.status}
                    onChange={(event) =>
                      setForm({ ...form, status: event.target.value as ExpenseStatus })}
                  >
                    {expenseStatusOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>{option.label}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <TextField
                  label="Fecha"
                  type="date"
                  fullWidth
                  slotProps={{ inputLabel: { shrink: true } }}
                  value={form.expense_date}
                  onChange={(event) => setForm({ ...form, expense_date: event.target.value })}
                />
              </Stack>
              <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
                <TextField
                  label="Base imponible"
                  type="number"
                  required
                  fullWidth
                  slotProps={{ htmlInput: { min: 0.01, step: 0.01 } }}
                  value={form.subtotal}
                  onChange={(event) => setForm({ ...form, subtotal: event.target.value })}
                />
                <TextField
                  label="Impuesto (%)"
                  type="number"
                  fullWidth
                  slotProps={{ htmlInput: { min: 0, max: 100, step: 0.01 } }}
                  value={form.tax_rate}
                  onChange={(event) => setForm({ ...form, tax_rate: event.target.value })}
                />
                <TextField
                  label="Referencia"
                  fullWidth
                  value={form.reference}
                  onChange={(event) => setForm({ ...form, reference: event.target.value })}
                />
              </Stack>
              <TextField
                label="Notas"
                multiline
                minRows={3}
                value={form.notes}
                onChange={(event) => setForm({ ...form, notes: event.target.value })}
              />
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>Cancelar</Button>
            <Button type="submit" variant="contained" disabled={createMutation.isPending}>
              Guardar gasto
            </Button>
          </DialogActions>
        </Box>
      </Dialog>
    </Stack>
  )
}
