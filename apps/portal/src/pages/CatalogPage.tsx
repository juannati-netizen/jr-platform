import AddOutlinedIcon from '@mui/icons-material/AddOutlined'
import FileUploadOutlinedIcon from '@mui/icons-material/FileUploadOutlined'
import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined'
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
  InputAdornment,
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
import {
  createCatalogItem,
  getCatalog,
  getCatalogFamilies,
  importLegacyTariff,
  type CatalogItemInput,
} from '../api/inventory'
import { euro } from '../utils/finance'

const emptyForm: CatalogItemInput = {
  code: '',
  family: 'General',
  description: '',
  unit: 'ud',
  purchase_price: '0.00',
  sale_price: '0.00',
  labor_hours: '0.00',
  supplier_name: '',
  tax_rate: '7.00',
}

export function CatalogPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [family, setFamily] = useState('')
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState<CatalogItemInput>(emptyForm)

  const catalogQuery = useQuery({
    queryKey: ['catalog', search, family],
    queryFn: () => getCatalog({ search, family, limit: 2000 }),
  })
  const familiesQuery = useQuery({ queryKey: ['catalog-families'], queryFn: getCatalogFamilies })

  const invalidate = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['catalog'] }),
      queryClient.invalidateQueries({ queryKey: ['catalog-families'] }),
      queryClient.invalidateQueries({ queryKey: ['inventory'] }),
      queryClient.invalidateQueries({ queryKey: ['warehouses'] }),
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] }),
    ])
  }

  const createMutation = useMutation({
    mutationFn: createCatalogItem,
    onSuccess: async () => {
      await invalidate()
      setForm(emptyForm)
      setOpen(false)
    },
  })
  const importMutation = useMutation({
    mutationFn: importLegacyTariff,
    onSuccess: invalidate,
  })

  const submit = (event: FormEvent) => {
    event.preventDefault()
    createMutation.mutate(form)
  }

  return (
    <Stack spacing={2}>
      <Stack direction={{ xs: 'column', lg: 'row' }} justifyContent="space-between" gap={1.5}>
        <Box>
          <Typography variant="h4">Tarifario y materiales</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.5 }}>
            Catálogo comercial y técnico con precios de compra, venta, mano de obra e impuestos.
          </Typography>
        </Box>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
          <Button
            variant="outlined"
            startIcon={<FileUploadOutlinedIcon />}
            onClick={() => importMutation.mutate()}
            disabled={importMutation.isPending}
          >
            Importar 1.135 artículos
          </Button>
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={() => setOpen(true)}>
            Nuevo artículo
          </Button>
        </Stack>
      </Stack>

      {importMutation.data && (
        <Alert severity="success">
          Importación completada: {importMutation.data.created} creados, {importMutation.data.updated}{' '}
          actualizados y {importMutation.data.skipped} omitidos.
        </Alert>
      )}
      {(catalogQuery.error || importMutation.error) && (
        <Alert severity="error">
          {catalogQuery.error instanceof ApiError
            ? catalogQuery.error.message
            : importMutation.error instanceof ApiError
              ? importMutation.error.message
              : 'No se pudo completar la operación'}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.2}>
            <TextField
              fullWidth
              size="small"
              label="Buscar por código, descripción o familia"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchOutlinedIcon fontSize="small" />
                  </InputAdornment>
                ),
              }}
            />
            <FormControl size="small" sx={{ minWidth: 220 }}>
              <InputLabel>Familia</InputLabel>
              <Select label="Familia" value={family} onChange={(event) => setFamily(event.target.value)}>
                <MenuItem value="">Todas</MenuItem>
                {(familiesQuery.data ?? []).map((item) => (
                  <MenuItem key={item} value={item}>{item}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent sx={{ p: 0 }}>
          {catalogQuery.isLoading && (
            <Stack alignItems="center" spacing={1.5} sx={{ p: 5 }}>
              <CircularProgress />
              <Typography color="text.secondary">Cargando tarifario…</Typography>
            </Stack>
          )}
          {catalogQuery.data && (
            <TableContainer sx={{ maxHeight: 620 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Código</TableCell>
                    <TableCell>Descripción</TableCell>
                    <TableCell>Familia</TableCell>
                    <TableCell>Unidad</TableCell>
                    <TableCell align="right">Compra</TableCell>
                    <TableCell align="right">Venta</TableCell>
                    <TableCell align="right">Horas</TableCell>
                    <TableCell>Estado</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {catalogQuery.data.map((item) => (
                    <TableRow key={item.id} hover>
                      <TableCell><Typography fontWeight={750}>{item.code}</Typography></TableCell>
                      <TableCell>{item.description}</TableCell>
                      <TableCell>{item.family}</TableCell>
                      <TableCell>{item.unit}</TableCell>
                      <TableCell align="right">{euro(item.purchase_price)}</TableCell>
                      <TableCell align="right">{euro(item.sale_price)}</TableCell>
                      <TableCell align="right">{item.labor_hours}</TableCell>
                      <TableCell>
                        <Chip size="small" color={item.is_active ? 'success' : 'default'} label={item.is_active ? 'Activo' : 'Inactivo'} />
                      </TableCell>
                    </TableRow>
                  ))}
                  {catalogQuery.data.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={8} align="center" sx={{ py: 5 }}>
                        <Typography color="text.secondary">No hay artículos para este filtro.</Typography>
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
          <DialogTitle>Nuevo artículo</DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ pt: 1 }}>
              {createMutation.error && (
                <Alert severity="error">
                  {createMutation.error instanceof ApiError ? createMutation.error.message : 'No se pudo crear el artículo'}
                </Alert>
              )}
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <TextField required fullWidth label="Código" value={form.code} onChange={(event) => setForm({ ...form, code: event.target.value })} />
                <TextField required fullWidth label="Familia" value={form.family} onChange={(event) => setForm({ ...form, family: event.target.value })} />
                <TextField required sx={{ width: 130 }} label="Unidad" value={form.unit} onChange={(event) => setForm({ ...form, unit: event.target.value })} />
              </Stack>
              <TextField required label="Descripción" value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} />
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <TextField fullWidth type="number" label="Precio compra" value={form.purchase_price} onChange={(event) => setForm({ ...form, purchase_price: event.target.value })} />
                <TextField fullWidth type="number" label="Precio venta" value={form.sale_price} onChange={(event) => setForm({ ...form, sale_price: event.target.value })} />
                <TextField fullWidth type="number" label="Horas" value={form.labor_hours} onChange={(event) => setForm({ ...form, labor_hours: event.target.value })} />
                <TextField fullWidth type="number" label="Impuesto %" value={form.tax_rate} onChange={(event) => setForm({ ...form, tax_rate: event.target.value })} />
              </Stack>
              <TextField label="Proveedor de referencia" value={form.supplier_name} onChange={(event) => setForm({ ...form, supplier_name: event.target.value })} />
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>Cancelar</Button>
            <Button type="submit" variant="contained" disabled={createMutation.isPending}>Guardar artículo</Button>
          </DialogActions>
        </Box>
      </Dialog>
    </Stack>
  )
}
