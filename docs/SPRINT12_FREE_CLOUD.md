# Sprint 12 — Nube gratuita con Render y Supabase

JR Platform puede publicarse sin contratar inicialmente recursos de pago:

- **Render Free Web Service** ejecuta el contenedor de FastAPI y React.
- **Supabase Free** proporciona PostgreSQL externo.
- Alembic aplica las migraciones al arrancar una versión nueva.
- El logotipo se conserva en PostgreSQL porque se almacena en la configuración empresarial.

## Arquitectura

```text
Navegador HTTPS
      |
      v
Render Free (FastAPI + React)
      |
      v
Supabase Free (PostgreSQL)
```

## Límites que debes conocer

Esta configuración es adecuada para pruebas, uso personal y una primera puesta en marcha, pero no ofrece garantías de producción:

- Render puede suspender el servicio web tras un periodo sin tráfico y el primer acceso posterior será más lento.
- El servicio gratuito de Render no dispone de disco persistente.
- Supabase Free limita la base de datos a 500 MB.
- Supabase puede pausar proyectos gratuitos con poca actividad durante una semana.
- Supabase Free no incluye copias automáticas descargables.

Mantén siempre copias locales periódicas de la base de datos.

## 1. Crear el proyecto gratuito de Supabase

1. Entra en el panel de Supabase y crea una cuenta.
2. Crea una organización con plan **Free**.
3. Pulsa **New project**.
4. Usa un nombre como `jr-platform`.
5. Genera una contraseña robusta para PostgreSQL y guárdala en tu gestor de contraseñas.
6. Selecciona una región europea cercana a Frankfurt.
7. Espera a que el proyecto termine de prepararse.

## 2. Obtener la URL correcta de PostgreSQL

En el proyecto de Supabase:

1. Pulsa **Connect**.
2. Selecciona la conexión **Session pooler** de Supavisor.
3. Usa el puerto `5432`.
4. Copia la cadena completa de conexión.
5. Sustituye el marcador de contraseña por la contraseña real cuando el panel lo solicite.

La aplicación necesita la cadena completa en la variable `DATABASE_URL`. No uses la clave pública `anon`, la clave `service_role` ni una URL HTTP de Supabase.

Antes de desplegar, puedes comprobar la conexión desde PowerShell:

```powershell
.\scripts\cloud\check-supabase-connection.ps1 `
  -DatabaseUrl 'postgresql://CADENA_COPIADA_DE_SUPABASE'
```

Usa comillas simples para evitar que PowerShell interprete caracteres especiales de la contraseña.

## 3. Crear el servicio gratuito de Render

1. En Render, pulsa **New > Blueprint**.
2. Conecta `juannati-netizen/jr-platform`.
3. Selecciona la rama `main`.
4. Render detectará `render.yaml`.
5. Comprueba que el servicio `jr-platform` muestra el plan **Free**.
6. Introduce las variables privadas:

| Variable | Valor |
|---|---|
| `DATABASE_URL` | Cadena **Session pooler** copiada de Supabase |
| `INITIAL_ADMIN_EMAIL` | Tu correo de acceso |
| `INITIAL_ADMIN_PASSWORD` | Una contraseña nueva y robusta |
| `AI_API_KEY` | Vacía por ahora |
| `AI_BASE_URL` | Vacía por ahora |

7. Confirma el Blueprint.
8. Espera a que la compilación finalice y `/health` esté correcto.
9. Abre la dirección terminada en `.onrender.com`.

## 4. Copiar la base local a Supabase

Primero exporta PostgreSQL local:

```powershell
.\scripts\cloud\export-local-database.ps1
```

Después restaura la copia en Supabase:

```powershell
.\scripts\cloud\restore-supabase-database.ps1 `
  -DatabaseUrl 'postgresql://CADENA_COPIADA_DE_SUPABASE' `
  -BackupPath '.\backups\jr-platform-FECHA.dump'
```

Cuando termine:

1. En Render, ejecuta **Manual Deploy > Deploy latest commit** o reinicia el servicio.
2. Abre `/health`.
3. Comprueba clientes, facturas, inventario, documentos, logotipo e IGIC.

## 5. Copias periódicas de Supabase

Crea una copia manual con:

```powershell
.\scripts\cloud\backup-supabase-database.ps1 `
  -DatabaseUrl 'postgresql://CADENA_COPIADA_DE_SUPABASE'
```

Los archivos se guardan en `backups/`, una carpeta excluida de Git.

## Seguridad

- No publiques `DATABASE_URL`, contraseñas ni claves privadas.
- No pegues secretos en incidencias, capturas o mensajes.
- No subas `.env`, `backups/`, `.dump` ni `.backup` a GitHub.
- Cambia la contraseña inicial después del primer acceso.
- Activa MFA en GitHub, Render y Supabase.
- Usa una contraseña distinta para Render, Supabase y JR Platform.

## Paso futuro

Cuando el sistema pase a utilizarse de forma continua con información fiscal real, conviene contratar una infraestructura con copias automáticas, disponibilidad garantizada y supervisión profesional.
