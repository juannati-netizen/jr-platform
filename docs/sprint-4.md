# Sprint 4 — Presupuestos y facturación

## Alcance

- Presupuestos con conceptos, cantidades, precios e IVA.
- Estados de presupuesto: borrador, enviado, aceptado, rechazado y caducado.
- Conversión controlada de presupuesto aceptado a factura.
- Facturas directas para administradores.
- Registro de pagos parciales o completos.
- Estados de factura: emitida, cobro parcial, cobrada y cancelada.
- Panel financiero con importes presupuestados, facturados, cobrados y pendientes.
- Vista imprimible de presupuestos y facturas.

## Permisos

- Todo usuario autenticado puede consultar y crear presupuestos.
- Solo administradores pueden crear facturas directas, convertir presupuestos y registrar pagos.
- Todo usuario autenticado puede consultar facturas.

## API

- `GET/POST /api/v1/quotes`
- `GET/PATCH /api/v1/quotes/{quote_id}`
- `POST /api/v1/quotes/{quote_id}/convert-to-invoice`
- `GET/POST /api/v1/invoices`
- `GET/PATCH /api/v1/invoices/{invoice_id}`
- `POST /api/v1/invoices/{invoice_id}/payments`
