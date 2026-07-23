# Sprint 8 — CRM comercial, pipeline y expedientes de obra

## Objetivo

Trasladar a JR Platform web las capacidades comerciales y de seguimiento de obras de la aplicación de escritorio.

## CRM comercial

- Leads con origen, estado, contacto, responsable y notas.
- Conversión controlada de lead en cliente.
- Oportunidades vinculadas a leads o clientes.
- Pipeline Kanban con historial de cambios de etapa.
- Valor estimado, probabilidad y pipeline ponderado.
- Actividades comerciales: tareas, llamadas, correos, reuniones y seguimientos.
- Conversión de oportunidades con cliente en presupuestos.

## Obras y expedientes

- Obras vinculadas a clientes, oportunidades y trabajos.
- Código de obra automático por ejercicio.
- Responsable, ubicación, fechas previstas, presupuesto objetivo y estado.
- Expediente agregado con trabajo, presupuestos, facturas, gastos y movimientos de material.
- Resumen financiero por obra.
- Documentos adjuntos almacenados de forma privada en PostgreSQL.
- Límite de 5 MB por documento.
- Descarga autenticada y eliminación restringida a administradores.

## Endpoints principales

```text
GET    /api/v1/crm/summary
GET    /api/v1/crm/leads
POST   /api/v1/crm/leads
POST   /api/v1/crm/leads/{id}/convert-to-client
GET    /api/v1/crm/opportunities
POST   /api/v1/crm/opportunities
PATCH  /api/v1/crm/opportunities/{id}
POST   /api/v1/crm/opportunities/{id}/convert-to-quote
GET    /api/v1/crm/activities
POST   /api/v1/crm/activities

GET    /api/v1/projects
POST   /api/v1/projects
GET    /api/v1/projects/{id}/file
POST   /api/v1/projects/{id}/documents
GET    /api/v1/projects/documents/{document_id}/download
DELETE /api/v1/projects/documents/{document_id}
```

## Pruebas manuales recomendadas

1. Crear un lead y convertirlo en cliente.
2. Crear una oportunidad para ese cliente.
3. Moverla por el pipeline y revisar el historial mediante Swagger.
4. Convertirla en presupuesto.
5. Crear un trabajo y una obra vinculada.
6. Abrir el expediente y comprobar sus métricas.
7. Subir y descargar un documento de prueba.

## Datos y seguridad

Los documentos de obra no se guardan en carpetas públicas del portal. Se almacenan en la base de datos y todos los accesos pasan por autenticación JWT.
