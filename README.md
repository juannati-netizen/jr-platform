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
- Interfaz Enterprise Workspace inspirada en la aplicación de escritorio.
- Centro de migración y plantillas CSV para preparar el traslado de datos.
- Tarifario técnico y comercial con 1.135 artículos heredados.
- Almacenes, existencias, movimientos, alertas de stock y materiales asignados a trabajos.
- CRM comercial con leads, oportunidades, actividades y pipeline Kanban.
- Conversión de leads en clientes y de oportunidades en presupuestos.
- Obras y expedientes digitales con documentos y resumen financiero.

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

## Importar el tarifario antiguo

La entrega del Sprint 7 incluye el archivo privado `private-import/tariff_items.csv`.
La carpeta está excluida por `.gitignore`, por lo que no se publica en GitHub.

1. Inicia la plataforma.
2. Entra como administrador.
3. Abre **Sistema → Centro de migración**.
4. Pulsa **Importar tarifario**.

También puedes iniciar la importación desde **Compras y almacén → Tarifario y materiales**.

## Configuración empresarial

Los administradores pueden gestionar empresa, ejercicios fiscales, preparación VERI*FACTU e IA desde **Sistema → Configuración empresarial**.
