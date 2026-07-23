# Changelog

## [0.12.0] - Sprint 11

- Imagen Docker de producción con FastAPI y React en un único servicio.
- Blueprint de Render con PostgreSQL administrado y despliegue tras CI.
- Compatibilidad con URLs PostgreSQL proporcionadas por proveedores cloud.
- Portal SPA servido por FastAPI en producción.
- Cabeceras HTTP de seguridad.
- Scripts de copia y restauración de la base de datos.
- Documentación de despliegue, migración y recuperación.
- Construcción de la imagen cloud validada por GitHub Actions.

## [0.11.0] - Sprint 10

- Logotipo, color corporativo y pie documental configurables.
- Identidad empresarial visible en el menú y documentos imprimibles.
- Fiscalidad IGIC configurada para el modelo 420 trimestral.
- Seguimiento mensual del IGIC repercutido y soportado.
- Ajustes fiscales documentados, cierre y reapertura de periodos.
- Borrador trimestral y exportación CSV del modelo 420.
- Tipo general predeterminado actualizado al 7 % para nuevas operaciones.
- Nueva migración y pruebas automáticas de fiscalidad y marca.

## [0.10.0] - Sprint 9

- Configuración empresarial y datos fiscales.
- Apertura, cierre y reapertura de ejercicios fiscales.
- Centro de preparación VERI*FACTU con lista de control.
- Configuración segura del Centro de IA sin almacenar credenciales.
- Historial de cambios administrativos.

## [0.9.0] - Sprint 8

- Leads, oportunidades y actividades comerciales.
- Pipeline Kanban con valor ponderado e historial de etapas.
- Conversión de leads en clientes y oportunidades en presupuestos.
- Obras vinculadas a clientes, oportunidades y trabajos.
- Expediente digital con documentos autenticados y métricas financieras.
- Métricas CRM y obras activas en el Centro de Control.
- Nueva migración y pruebas automáticas de CRM y proyectos.

## [0.8.0] - Sprint 7

- Tarifario técnico y comercial.
- Importación idempotente de 1.135 artículos desde JR Platform Desktop.
- Almacenes y existencias por artículo.
- Entradas, salidas, devoluciones, ajustes y asignaciones a trabajos.
- Alertas de stock mínimo y valoración del inventario.
- Coste de materiales de almacén integrado en la rentabilidad.
- Datos privados de importación excluidos del repositorio público.
- Nueva migración y pruebas automáticas de inventario.

## [0.7.0] - Sprint 6

- Nuevo diseño oscuro Enterprise Workspace inspirado en JR Platform Desktop.
- Navegación por áreas: visión general, comercial, compras, gestión y sistema.
- Centro de Control compacto con métricas, agenda, alertas, actividad y accesos rápidos.
- Centro de migración para preparar datos de la aplicación de escritorio.
- Plantillas CSV y guía de transición segura.

## [0.6.0] - Sprint 5

- Gestión de proveedores.
- Registro y clasificación de gastos y compras.
- Vinculación de costes con trabajos.
- Seguimiento de materiales, pagos y referencias.
- Rentabilidad por trabajo y cliente.
- Panel ampliado con gastos y márgenes.
- Exportación CSV de informes de rentabilidad.
- Migración y pruebas automáticas de compras.

## [0.5.0] - Sprint 4

- Presupuestos con líneas, impuestos y estados.
- Conversión de presupuestos aceptados en facturas.
- Facturas directas y pagos parciales/completos.
- Métricas financieras en el panel.
- Documentos imprimibles en el portal.
- Permisos administrativos para facturación y cobros.

## [0.4.0] - Sprint 3

- Gestión de clientes.
- Gestión de trabajos con estados, prioridades y responsables.
- Notas de seguimiento.
- Panel operativo con métricas reales.
- Migración de base de datos y pruebas automáticas.

## [0.3.0] - Sprint 2

- Portal React + TypeScript + Vite.
- Inicio de sesión conectado a FastAPI.
- Sesión JWT y rutas protegidas.
- Panel, perfil y gestión de usuarios.
- Material UI, TanStack Router y TanStack Query.
- Docker y CI para frontend.
- CORS configurable en la API.

## [0.2.0] - Sprint 1

- Registro e inicio de sesión.
- JWT, usuarios, roles y permisos.
- Migración de la tabla de usuarios.
- Administrador inicial configurable.

## [0.1.0] - Sprint 0

- Estructura inicial del backend.
- FastAPI, PostgreSQL, Docker Compose y Alembic.
- Endpoint `/health`.
- Pytest, Ruff, MyPy y GitHub Actions.
