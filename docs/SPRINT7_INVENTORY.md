# Sprint 7 — Tarifario, almacén e inventario

## Componentes

- `catalog_items`: referencias técnicas y comerciales.
- `warehouses`: almacenes y ubicaciones.
- `inventory_levels`: stock, reservas, mínimos, estantería y código de barras.
- `stock_movements`: historial de entradas, salidas, asignaciones, devoluciones y ajustes.

## Reglas operativas

- No se permiten salidas que dejen stock negativo.
- Una asignación requiere una orden de trabajo.
- El coste asignado a un trabajo se incorpora a la rentabilidad como coste de material.
- Los ajustes pueden ser positivos o negativos, pero nunca pueden dejar stock negativo.
- El importador del tarifario es idempotente.

## Privacidad

`private-import/` está ignorado por Git. No elimines esta regla ni publiques el CSV de precios en un repositorio público.
