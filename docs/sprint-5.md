# Sprint 5 — Proveedores, gastos y rentabilidad

## Alcance

- Proveedores con datos fiscales y de contacto.
- Gastos clasificados por categoría y estado.
- Asociación opcional de gastos a proveedor y trabajo.
- Cálculo automático de impuestos y total.
- Informe de ingresos, gastos y margen.
- Rentabilidad por trabajo y cliente.
- Exportación CSV desde el portal.

## Endpoints

- `GET/POST /api/v1/suppliers`
- `GET/PATCH /api/v1/suppliers/{supplier_id}`
- `GET/POST /api/v1/expenses`
- `GET/PATCH /api/v1/expenses/{expense_id}`
- `GET /api/v1/profitability/summary`

Las operaciones de compras y rentabilidad requieren rol de administrador.
