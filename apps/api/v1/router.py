from fastapi import APIRouter

from apps.api.v1.routes.auth import router as auth_router
from apps.api.v1.routes.catalog import router as catalog_router
from apps.api.v1.routes.clients import router as clients_router
from apps.api.v1.routes.dashboard import router as dashboard_router
from apps.api.v1.routes.expenses import router as expenses_router
from apps.api.v1.routes.inventory import router as inventory_router
from apps.api.v1.routes.invoices import router as invoices_router
from apps.api.v1.routes.profitability import router as profitability_router
from apps.api.v1.routes.quotes import router as quotes_router
from apps.api.v1.routes.suppliers import router as suppliers_router
from apps.api.v1.routes.users import router as users_router
from apps.api.v1.routes.warehouses import router as warehouses_router
from apps.api.v1.routes.work_orders import router as work_orders_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(clients_router, prefix="/clients", tags=["clients"])
api_router.include_router(catalog_router, prefix="/catalog", tags=["catalog"])
api_router.include_router(warehouses_router, prefix="/warehouses", tags=["warehouses"])
api_router.include_router(inventory_router, prefix="/inventory", tags=["inventory"])
api_router.include_router(work_orders_router, prefix="/work-orders", tags=["work orders"])
api_router.include_router(quotes_router, prefix="/quotes", tags=["quotes"])
api_router.include_router(invoices_router, prefix="/invoices", tags=["invoices"])
api_router.include_router(suppliers_router, prefix="/suppliers", tags=["suppliers"])
api_router.include_router(expenses_router, prefix="/expenses", tags=["expenses"])
api_router.include_router(
    profitability_router,
    prefix="/profitability",
    tags=["profitability"],
)
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
