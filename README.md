# JR Platform

Plataforma operativa para clientes, trabajos, facturación, compras y rentabilidad.

## Funcionalidades actuales

- Autenticación JWT, usuarios y roles.
- Clientes y órdenes de trabajo.
- Notas, responsables, estados y prioridades.
- Presupuestos con conceptos e impuestos.
- Conversión de presupuesto aceptado en factura.
- Pagos parciales y completos.
- Proveedores y registro de gastos.
- Costes de materiales y gastos vinculados a trabajos.
- Rentabilidad por trabajo y cliente.
- Exportación CSV de informes de rentabilidad.
- Panel operativo, financiero y de margen.
- Portal React con documentos imprimibles.

## Requisitos

- Docker Desktop
- Git

## Arranque

1. Copia `.env.example` como `.env`.
2. Ejecuta:

```bash
docker compose up --build
```

3. Abre:

- Portal: http://localhost:5173
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Credenciales locales iniciales

```text
Correo: admin@jrplatform.com
Contraseña: ChangeMe123!
```

Cambia estas credenciales antes de utilizar la plataforma fuera del entorno local.

## Calidad

Backend:

```bash
ruff check .
ruff format --check .
mypy apps
pytest
```

Portal:

```bash
cd apps/portal
npm install
npm run check
npm test
npm run build
```
