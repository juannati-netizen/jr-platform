import AddBusinessOutlinedIcon from '@mui/icons-material/AddBusinessOutlined'
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline'
import Inventory2OutlinedIcon from '@mui/icons-material/Inventory2Outlined'
import WarningAmberOutlinedIcon from '@mui/icons-material/WarningAmberOutlined'
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
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  TextField,
  Typography,
} from '@mui/material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { type FormEvent, useMemo, useState } from 'react'

import { ApiError } from '../api/client'
import {
  createStockMovement,
  createWarehouse,
  getCatalog,
  getInventory,
  getStockMovements,
  getWarehouses,
  type StockMovementInput,
  type WarehouseInput,
} from '../api/inventory'
import type { StockMovementType } from '../api/types'
import { getWorkOrders } from '../api/work-orders'
import { euro } from '../utils/finance'

const movementLabels: Record<StockMovementType, string> = {
  entry: 'Entrada',
  exit: 'Salida',
  assignment: 'Asignación a trabajo',
  return: 'Devolución',
  adjustment: 'Ajuste',
}

export function InventoryPage() {
  const queryClient = useQueryClient()
  const [tab, setTab] = useState(0)
  const [warehouseFilter, setWarehouseFilter] = useState('')
  const [lowStockOnly, setLowStockOnly] = useState(false)
  const [movementOpen, setMovementOpen] = useState(false)
  const [warehouseOpen, setWarehouseOpen] = useState(false)
  const [warehouseForm, setWarehouseForm] = useState<WarehouseInput>({ name: '', kind: 'Almacén', location: '' })
  const [movementForm, setMovementForm] = useState<StockMovementInput>({
    catalog_item_id: '',
    warehouse_id: '',
    work_order_id: '',
    movement_type: 'entry',
    quantity: '1.000',
    unit_cost: '',
    reference: '',
    notes: '',
  })

  const warehousesQuery = useQuery({ queryKey: ['warehouses'], queryFn: () => getWarehouses(false) })
  const catalogQuery = useQuery({ queryKey: ['catalog', 'active'], queryFn: () => getCatalog({ activeOnly: true, limit: 2000 }) })
  const workOrdersQuery = useQuery({ queryKey: ['work-orders'], queryFn: getWorkOrders })
  const inventoryQuery = useQuery({
    queryKey: ['inventory', warehouseFilter, lowStockOnly],
    queryFn: () => getInventory({ warehouseId: warehouseFilter, lowStockOnly, limit: 2000 }),
  })
  const movementsQuery = useQuery({ queryKey: ['stock-movements'], queryFn: () => getStockMovements(200) })

  const inventoryValue = useMemo(
    () => (inventoryQuery.data ?? []).reduce((sum, item) => sum + Number(item.inventory_value), 0),
    [inventoryQuery.data],
  )
  const lowStockCount = (inventoryQuery.data ?? []).filter((item) => item.low_stock).length

  const invalidate = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['inventory'] }),
      queryClient.invalidateQueries({ queryKey: ['stock-movements'] }),
      queryClient.invalidateQueries({ queryKey: ['warehouses'] }),
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] }),
      queryClient.invalidateQueries({ queryKey: ['profitability-summary'] }),
    ])
  }

  const warehouseMutation = useMutation({
    mutationFn: createWarehouse,
    onSuccess: async () => {
      await invalidate()
      setWarehouseForm({ name: '', kind: 'Almacén', location: '' })
      setWarehouseOpen(false)
    },
  })
  const movementMutation = useMutation({
    mutationFn: createStockMovement,
    onSuccess: async () => {
      await invalidate()
      setMovementOpen(false)
      setMovementForm({
        catalog_item_id: '', warehouse_id: '', work_order_id: '', movement_type: 'entry',
        quantity: '1.000', unit_cost: '', reference: '', notes: '',
      })
    },
  })

  const submitWarehouse = (event: FormEvent) => {
    event.preventDefault()
    warehouseMutation.mutate(warehouseForm)
  }
  const submitMovement = (event: FormEvent) => {
    event.preventDefault()
    movementMutation.mutate({
      ...movementForm,
      work_order_id: movementForm.work_order_id || null,
      unit_cost: movementForm.unit_cost || undefined,
    })
  }

  const selectedCatalogItem = catalogQuery.data?.find((item) => item.id === movementForm.catalog_item_id)

  return (
    <Stack spacing={2}>
      <Stack direction={{ xs: 'column', lg: 'row' }} justifyContent="space-between" gap={1.5}>
        <Box>
          <Typography variant="h4">Almacén e inventario</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.5 }}>
            Existencias, movimientos, alertas de mínimos y materiales asignados a trabajos.
          </Typography>
        </Box>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
          <Button variant="outlined" startIcon={<AddBusinessOutlinedIcon />} onClick={() => setWarehouseOpen(true)}>
            Nuevo almacén
          </Button>
          <Button variant="contained" startIcon={<AddCircleOutlineIcon />} onClick={() => setMovementOpen(true)}>
            Registrar movimiento
          </Button>
        </Stack>
      </Stack>

      {(inventoryQuery.error || movementsQuery.error) && (
        <Alert severity="error">
          {inventoryQuery.error instanceof ApiError
            ? inventoryQuery.error.message
            : movementsQuery.error instanceof ApiError
              ? movementsQuery.error.message
              : 'No se pudo cargar el inventario'}
        </Alert>
      )}

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.2}>
        <Card sx={{ flex: 1 }}><CardContent><Typography color="text.secondary">Valor de inventario</Typography><Typography variant="h5">{euro(inventoryValue)}</Typography></CardContent></Card>
        <Card sx={{ flex: 1 }}><CardContent><Typography color="text.secondary">Referencias en almacén</Typography><Typography variant="h5">{inventoryQuery.data?.length ?? 0}</Typography></CardContent></Card>
        <Card sx={{ flex: 1 }}><CardContent><Typography color="text.secondary">Alertas de stock</Typography><Typography variant="h5" color={lowStockCount > 0 ? 'warning.main' : 'success.main'}>{lowStockCount}</Typography></CardContent></Card>
      </Stack>

      <Card>
        <Tabs value={tab} onChange={(_, value: number) => setTab(value)}>
          <Tab label="Existencias" icon={<Inventory2OutlinedIcon />} iconPosition="start" />
          <Tab label="Movimientos" icon={<AddCircleOutlineIcon />} iconPosition="start" />
        </Tabs>
      </Card>

      {tab === 0 && (
        <>
          <Card><CardContent><Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.2} alignItems={{ sm: 'center' }}>
            <FormControl size="small" sx={{ minWidth: 240 }}>
              <InputLabel>Almacén</InputLabel>
              <Select label="Almacén" value={warehouseFilter} onChange={(event) => setWarehouseFilter(event.target.value)}>
                <MenuItem value="">Todos</MenuItem>
                {(warehousesQuery.data ?? []).map((warehouse) => <MenuItem key={warehouse.id} value={warehouse.id}>{warehouse.name}</MenuItem>)}
              </Select>
            </FormControl>
            <Button variant={lowStockOnly ? 'contained' : 'outlined'} color="warning" startIcon={<WarningAmberOutlinedIcon />} onClick={() => setLowStockOnly((value) => !value)}>
              Solo stock bajo
            </Button>
          </Stack></CardContent></Card>
          <Card><CardContent sx={{ p: 0 }}>
            {inventoryQuery.isLoading && <Stack alignItems="center" sx={{ p: 5 }}><CircularProgress /></Stack>}
            {inventoryQuery.data && <TableContainer sx={{ maxHeight: 620 }}><Table stickyHeader size="small"><TableHead><TableRow>
              <TableCell>Artículo</TableCell><TableCell>Almacén</TableCell><TableCell align="right">Stock</TableCell><TableCell align="right">Disponible</TableCell><TableCell align="right">Mínimo</TableCell><TableCell>Ubicación</TableCell><TableCell align="right">Valor</TableCell><TableCell>Estado</TableCell>
            </TableRow></TableHead><TableBody>
              {inventoryQuery.data.map((level) => <TableRow key={level.id} hover>
                <TableCell><Typography fontWeight={750}>{level.catalog_item.code}</Typography><Typography variant="caption" color="text.secondary">{level.catalog_item.description}</Typography></TableCell>
                <TableCell>{level.warehouse.name}</TableCell>
                <TableCell align="right">{level.stock} {level.catalog_item.unit}</TableCell>
                <TableCell align="right">{level.available}</TableCell>
                <TableCell align="right">{level.min_stock}</TableCell>
                <TableCell>{level.shelf ?? '—'}</TableCell>
                <TableCell align="right">{euro(level.inventory_value)}</TableCell>
                <TableCell><Chip size="small" color={level.low_stock ? 'warning' : 'success'} label={level.low_stock ? 'Reponer' : 'Correcto'} /></TableCell>
              </TableRow>)}
              {inventoryQuery.data.length === 0 && <TableRow><TableCell colSpan={8} align="center" sx={{ py: 5 }}><Typography color="text.secondary">No hay existencias. Importa el tarifario o registra una entrada.</Typography></TableCell></TableRow>}
            </TableBody></Table></TableContainer>}
          </CardContent></Card>
        </>
      )}

      {tab === 1 && (
        <Card><CardContent sx={{ p: 0 }}><TableContainer sx={{ maxHeight: 620 }}><Table stickyHeader size="small"><TableHead><TableRow>
          <TableCell>Fecha</TableCell><TableCell>Artículo</TableCell><TableCell>Almacén</TableCell><TableCell>Tipo</TableCell><TableCell align="right">Cantidad</TableCell><TableCell align="right">Coste</TableCell><TableCell>Referencia</TableCell>
        </TableRow></TableHead><TableBody>
          {(movementsQuery.data ?? []).map((movement) => <TableRow key={movement.id} hover>
            <TableCell>{new Intl.DateTimeFormat('es-ES', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(movement.movement_date))}</TableCell>
            <TableCell><Typography fontWeight={750}>{movement.catalog_item.code}</Typography><Typography variant="caption" color="text.secondary">{movement.catalog_item.description}</Typography></TableCell>
            <TableCell>{movement.warehouse.name}</TableCell>
            <TableCell>{movementLabels[movement.movement_type]}</TableCell>
            <TableCell align="right" sx={{ color: Number(movement.quantity) < 0 ? 'warning.main' : 'success.main' }}>{movement.quantity} {movement.catalog_item.unit}</TableCell>
            <TableCell align="right">{euro(movement.total_cost)}</TableCell>
            <TableCell>{movement.reference ?? '—'}</TableCell>
          </TableRow>)}
          {(movementsQuery.data ?? []).length === 0 && <TableRow><TableCell colSpan={7} align="center" sx={{ py: 5 }}><Typography color="text.secondary">Aún no hay movimientos.</Typography></TableCell></TableRow>}
        </TableBody></Table></TableContainer></CardContent></Card>
      )}

      <Dialog open={warehouseOpen} onClose={() => setWarehouseOpen(false)} fullWidth maxWidth="sm">
        <Box component="form" onSubmit={submitWarehouse}><DialogTitle>Nuevo almacén</DialogTitle><DialogContent><Stack spacing={2} sx={{ pt: 1 }}>
          {warehouseMutation.error && <Alert severity="error">{warehouseMutation.error instanceof ApiError ? warehouseMutation.error.message : 'No se pudo crear el almacén'}</Alert>}
          <TextField required label="Nombre" value={warehouseForm.name} onChange={(event) => setWarehouseForm({ ...warehouseForm, name: event.target.value })} />
          <TextField required label="Tipo" value={warehouseForm.kind} onChange={(event) => setWarehouseForm({ ...warehouseForm, kind: event.target.value })} />
          <TextField label="Ubicación" value={warehouseForm.location} onChange={(event) => setWarehouseForm({ ...warehouseForm, location: event.target.value })} />
        </Stack></DialogContent><DialogActions><Button onClick={() => setWarehouseOpen(false)}>Cancelar</Button><Button type="submit" variant="contained">Guardar</Button></DialogActions></Box>
      </Dialog>

      <Dialog open={movementOpen} onClose={() => setMovementOpen(false)} fullWidth maxWidth="md">
        <Box component="form" onSubmit={submitMovement}><DialogTitle>Registrar movimiento de stock</DialogTitle><DialogContent><Stack spacing={2} sx={{ pt: 1 }}>
          {movementMutation.error && <Alert severity="error">{movementMutation.error instanceof ApiError ? movementMutation.error.message : 'No se pudo registrar el movimiento'}</Alert>}
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <FormControl required fullWidth><InputLabel>Artículo</InputLabel><Select label="Artículo" value={movementForm.catalog_item_id} onChange={(event) => {
              const item = catalogQuery.data?.find((candidate) => candidate.id === event.target.value)
              setMovementForm({ ...movementForm, catalog_item_id: event.target.value, unit_cost: item?.purchase_price ?? '' })
            }}>
              {(catalogQuery.data ?? []).map((item) => <MenuItem key={item.id} value={item.id}>{item.code} · {item.description}</MenuItem>)}
            </Select></FormControl>
            <FormControl required fullWidth><InputLabel>Almacén</InputLabel><Select label="Almacén" value={movementForm.warehouse_id} onChange={(event) => setMovementForm({ ...movementForm, warehouse_id: event.target.value })}>
              {(warehousesQuery.data ?? []).filter((item) => item.is_active).map((item) => <MenuItem key={item.id} value={item.id}>{item.name}</MenuItem>)}
            </Select></FormControl>
          </Stack>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <FormControl required fullWidth><InputLabel>Tipo</InputLabel><Select label="Tipo" value={movementForm.movement_type} onChange={(event) => setMovementForm({ ...movementForm, movement_type: event.target.value as StockMovementType })}>
              {(Object.keys(movementLabels) as StockMovementType[]).map((type) => <MenuItem key={type} value={type}>{movementLabels[type]}</MenuItem>)}
            </Select></FormControl>
            <TextField required fullWidth type="number" label={`Cantidad${selectedCatalogItem ? ` (${selectedCatalogItem.unit})` : ''}`} value={movementForm.quantity} onChange={(event) => setMovementForm({ ...movementForm, quantity: event.target.value })} />
            <TextField fullWidth type="number" label="Coste unitario" value={movementForm.unit_cost} onChange={(event) => setMovementForm({ ...movementForm, unit_cost: event.target.value })} />
          </Stack>
          {movementForm.movement_type === 'assignment' && <FormControl required fullWidth><InputLabel>Trabajo</InputLabel><Select label="Trabajo" value={movementForm.work_order_id} onChange={(event) => setMovementForm({ ...movementForm, work_order_id: event.target.value })}>
            {(workOrdersQuery.data ?? []).map((item) => <MenuItem key={item.id} value={item.id}>{item.title} · {item.client.name}</MenuItem>)}
          </Select></FormControl>}
          <TextField label="Referencia" value={movementForm.reference} onChange={(event) => setMovementForm({ ...movementForm, reference: event.target.value })} />
          <TextField label="Notas" multiline minRows={2} value={movementForm.notes} onChange={(event) => setMovementForm({ ...movementForm, notes: event.target.value })} />
        </Stack></DialogContent><DialogActions><Button onClick={() => setMovementOpen(false)}>Cancelar</Button><Button type="submit" variant="contained" disabled={movementMutation.isPending}>Registrar</Button></DialogActions></Box>
      </Dialog>
    </Stack>
  )
}
