import AddBusinessOutlinedIcon from '@mui/icons-material/AddBusinessOutlined'
import LocalShippingOutlinedIcon from '@mui/icons-material/LocalShippingOutlined'
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
  createSupplier,
  getSuppliers,
  type SupplierInput,
} from '../api/procurement'

const emptyForm: SupplierInput = {
  name: '',
  tax_id: '',
  email: '',
  phone: '',
  address: '',
  notes: '',
}

export function SuppliersPage() {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState<SupplierInput>(emptyForm)
  const suppliersQuery = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => getSuppliers(false),
  })
  const createMutation = useMutation({
    mutationFn: createSupplier,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['suppliers'] })
      await queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] })
      setForm(emptyForm)
      setOpen(false)
    },
  })

  const submit = (event: FormEvent) => {
    event.preventDefault()
    createMutation.mutate(form)
  }

  return (
    <Stack spacing={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" spacing={2}>
        <Box>
          <Typography variant="h4">Proveedores</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.75 }}>
            Directorio de suministradores, subcontratas y servicios externos.
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddBusinessOutlinedIcon />}
          onClick={() => setOpen(true)}
        >
          Nuevo proveedor
        </Button>
      </Stack>

      {suppliersQuery.error && (
        <Alert severity="error">
          {suppliersQuery.error instanceof ApiError
            ? suppliersQuery.error.message
            : 'No se pudieron cargar los proveedores'}
        </Alert>
      )}

      <Card>
        <CardContent sx={{ p: 0 }}>
          {suppliersQuery.isLoading && (
            <Stack alignItems="center" spacing={2} sx={{ p: 6 }}>
              <CircularProgress />
              <Typography color="text.secondary">Cargando proveedores…</Typography>
            </Stack>
          )}
          {suppliersQuery.data && (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Proveedor</TableCell>
                    <TableCell>Identificador fiscal</TableCell>
                    <TableCell>Contacto</TableCell>
                    <TableCell>Estado</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {suppliersQuery.data.map((supplier) => (
                    <TableRow key={supplier.id} hover>
                      <TableCell>
                        <Stack direction="row" spacing={1.5} alignItems="center">
                          <LocalShippingOutlinedIcon color="action" />
                          <Box>
                            <Typography fontWeight={700}>{supplier.name}</Typography>
                            {supplier.address && (
                              <Typography variant="body2" color="text.secondary">
                                {supplier.address}
                              </Typography>
                            )}
                          </Box>
                        </Stack>
                      </TableCell>
                      <TableCell>{supplier.tax_id ?? '—'}</TableCell>
                      <TableCell>
                        <Typography variant="body2">{supplier.email ?? '—'}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {supplier.phone ?? ''}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          variant="outlined"
                          color={supplier.is_active ? 'success' : 'default'}
                          label={supplier.is_active ? 'Activo' : 'Inactivo'}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                  {suppliersQuery.data.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={4} align="center" sx={{ py: 6 }}>
                        <Typography color="text.secondary">Aún no hay proveedores.</Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <Box component="form" onSubmit={submit}>
          <DialogTitle>Nuevo proveedor</DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ pt: 1 }}>
              {createMutation.error && (
                <Alert severity="error">
                  {createMutation.error instanceof ApiError
                    ? createMutation.error.message
                    : 'No se pudo crear el proveedor'}
                </Alert>
              )}
              <TextField
                label="Nombre"
                required
                value={form.name}
                onChange={(event) => setForm({ ...form, name: event.target.value })}
              />
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <TextField
                  label="Identificador fiscal"
                  fullWidth
                  value={form.tax_id}
                  onChange={(event) => setForm({ ...form, tax_id: event.target.value })}
                />
                <TextField
                  label="Teléfono"
                  fullWidth
                  value={form.phone}
                  onChange={(event) => setForm({ ...form, phone: event.target.value })}
                />
              </Stack>
              <TextField
                label="Correo"
                type="email"
                value={form.email}
                onChange={(event) => setForm({ ...form, email: event.target.value })}
              />
              <TextField
                label="Dirección"
                value={form.address}
                onChange={(event) => setForm({ ...form, address: event.target.value })}
              />
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
              Guardar proveedor
            </Button>
          </DialogActions>
        </Box>
      </Dialog>
    </Stack>
  )
}
