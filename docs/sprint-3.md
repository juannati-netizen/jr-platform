# Sprint 3 · Gestión operativa

## Alcance

- Directorio de clientes con alta, consulta y actualización.
- Trabajos con estados, prioridades, cliente, responsable y planificación.
- Notas de seguimiento por trabajo.
- Métricas operativas en el panel principal.
- API REST protegida con JWT.
- Migración Alembic para clientes, trabajos y notas.
- Pruebas automáticas de backend.
- Vistas React para clientes y trabajos.

## Endpoints principales

- `GET/POST /api/v1/clients`
- `GET/PATCH /api/v1/clients/{client_id}`
- `GET/POST /api/v1/work-orders`
- `GET/PATCH /api/v1/work-orders/{work_order_id}`
- `GET/POST /api/v1/work-orders/{work_order_id}/notes`
- `GET /api/v1/dashboard/summary`
