# Migración desde JR Platform Desktop

El objetivo es trasladar la operativa de la aplicación de escritorio a JR Platform Web sin perder datos.

## Qué necesitamos localizar

1. Exportaciones CSV o Excel.
2. Bases de datos `.db`, `.sqlite`, `.sqlite3`, `.mdb` o `.accdb`.
3. Carpetas de copias de seguridad.
4. PDFs, imágenes y documentos asociados a clientes, trabajos, presupuestos y facturas.
5. Una lista de usuarios y permisos.

## Orden de importación

1. Usuarios.
2. Clientes y proveedores.
3. Trabajos.
4. Presupuestos y facturas.
5. Pagos y gastos.
6. Documentos adjuntos.

## Procedimiento seguro

- Trabajar primero con una copia de los datos.
- Importar una muestra pequeña.
- Comparar totales con la aplicación de escritorio.
- Hacer una copia de seguridad antes de la importación definitiva.
- Mantener la aplicación antigua en modo consulta durante la transición.

Las plantillas de `docs/import-templates` definen el formato esperado para cada conjunto de datos.
