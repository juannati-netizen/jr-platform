# Sprint 11 — Despliegue cloud

> **Documento histórico:** la configuración de pago de este sprint fue sustituida por `docs/SPRINT12_FREE_CLOUD.md`.

JR Platform puede desplegarse como un único servicio web:

- FastAPI sirve la API bajo `/api/v1`.
- El portal React compilado se sirve desde la misma dirección.
- PostgreSQL se ejecuta como base de datos administrada.
- Alembic aplica las migraciones al iniciar una versión nueva.

## Arquitectura

```text
Navegador HTTPS
      |
      v
JR Platform (FastAPI + React)
      |
      v
PostgreSQL administrado
```

## Render Blueprint

El archivo `render.yaml` crea:

- `jr-platform`: servicio web Docker en Frankfurt.
- `jr-platform-db`: PostgreSQL 16 administrado.
- secreto JWT generado por Render.
- variables privadas solicitadas durante la creación.
- despliegue automático solo cuando GitHub Actions está en verde.
- comprobación HTTP en `/health`.

Los planes declarados son de pago (`starter` y `basic-256mb`). Render mostrará el coste antes de confirmar la creación. Para datos empresariales no se recomienda una base gratuita porque no incluye recuperación administrada.

## Primer despliegue

1. En Render, selecciona **New > Blueprint**.
2. Conecta `juannati-netizen/jr-platform`.
3. Render detectará `render.yaml`.
4. Introduce un correo y contraseña iniciales robustos.
5. Deja vacías las variables de IA hasta que se configure un proveedor.
6. Confirma la creación de los recursos.
7. Espera a que `/health` esté correcto.
8. Abre la dirección `https://jr-platform.onrender.com` asignada por Render.

## Copiar los datos locales

Crea primero una copia:

```powershell
.\scripts\cloud\export-local-database.ps1
```

Render muestra la URL externa de PostgreSQL en la pantalla **Connect** de la base de datos. Con la aplicación en mantenimiento, restaura la copia:

```powershell
.\scripts\cloud\restore-render-database.ps1 `
  -DatabaseUrl "URL_EXTERNA_DE_RENDER" `
  -BackupPath ".\backups\jr-platform-FECHA.dump"
```

Después reinicia manualmente el servicio web desde Render y comprueba clientes, facturas, documentos, inventario e IGIC.

## Seguridad

- No publiques la URL de PostgreSQL.
- No subas `.env`, copias `.dump` ni claves privadas a GitHub.
- Cambia la contraseña inicial después del primer acceso.
- Activa autenticación multifactor en GitHub y Render.
- Tras la migración, restringe el acceso externo a PostgreSQL desde el panel de Render.

## Copias de seguridad

Las bases de datos de pago de Render permiten recuperación y exportaciones lógicas. Mantén además copias descargadas fuera del proveedor siguiendo la política de tu empresa.
