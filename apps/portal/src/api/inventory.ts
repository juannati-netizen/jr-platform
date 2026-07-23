import { apiRequest } from './client'
import type {
  CatalogItem,
  InventoryLevel,
  LegacyTariffImportResult,
  StockMovement,
  StockMovementType,
  Warehouse,
} from './types'

export interface CatalogItemInput {
  code: string
  family: string
  description: string
  unit: string
  purchase_price: string
  sale_price: string
  labor_hours: string
  supplier_name?: string
  tax_rate: string
}

export interface WarehouseInput {
  name: string
  kind: string
  location?: string
}

export interface StockMovementInput {
  catalog_item_id: string
  warehouse_id: string
  work_order_id?: string | null
  movement_type: StockMovementType
  quantity: string
  unit_cost?: string
  reference?: string
  notes?: string
}

export function getCatalog(params: {
  search?: string
  family?: string
  activeOnly?: boolean
  limit?: number
} = {}): Promise<CatalogItem[]> {
  const query = new URLSearchParams()
  if (params.search) query.set('search', params.search)
  if (params.family) query.set('family', params.family)
  if (params.activeOnly) query.set('active_only', 'true')
  query.set('limit', String(params.limit ?? 500))
  return apiRequest<CatalogItem[]>(`/catalog?${query.toString()}`)
}

export function getCatalogFamilies(): Promise<string[]> {
  return apiRequest<string[]>('/catalog/families')
}

export function createCatalogItem(payload: CatalogItemInput): Promise<CatalogItem> {
  return apiRequest<CatalogItem>('/catalog', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function importLegacyTariff(): Promise<LegacyTariffImportResult> {
  return apiRequest<LegacyTariffImportResult>('/catalog/import-legacy', { method: 'POST' })
}

export function getWarehouses(activeOnly = false): Promise<Warehouse[]> {
  return apiRequest<Warehouse[]>(`/warehouses?active_only=${activeOnly}`)
}

export function createWarehouse(payload: WarehouseInput): Promise<Warehouse> {
  return apiRequest<Warehouse>('/warehouses', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getInventory(params: {
  warehouseId?: string
  search?: string
  lowStockOnly?: boolean
  limit?: number
} = {}): Promise<InventoryLevel[]> {
  const query = new URLSearchParams()
  if (params.warehouseId) query.set('warehouse_id', params.warehouseId)
  if (params.search) query.set('search', params.search)
  if (params.lowStockOnly) query.set('low_stock_only', 'true')
  query.set('limit', String(params.limit ?? 500))
  return apiRequest<InventoryLevel[]>(`/inventory?${query.toString()}`)
}

export function updateInventoryLevel(
  levelId: string,
  payload: { min_stock?: string; shelf?: string; barcode?: string },
): Promise<InventoryLevel> {
  return apiRequest<InventoryLevel>(`/inventory/${levelId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function getStockMovements(limit = 100): Promise<StockMovement[]> {
  return apiRequest<StockMovement[]>(`/inventory/movements?limit=${limit}`)
}

export function createStockMovement(payload: StockMovementInput): Promise<StockMovement> {
  return apiRequest<StockMovement>('/inventory/movements', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
