# JR Platform

JR Platform es una base modular con API FastAPI, PostgreSQL y un portal React protegido por autenticación JWT.

## Sprint 2

Esta entrega incorpora:

- Portal React + TypeScript + Vite.
- Material UI.
- TanStack Router y TanStack Query.
- Inicio y cierre de sesión.
- Rutas protegidas.
- Panel principal y perfil.
- Gestión de roles para administradores.
- Docker para API, base de datos y portal.
- CI independiente para backend y frontend.

## Requisitos

- Docker Desktop.
- Git.

## Arranque rápido

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

## Credenciales de desarrollo

```text
Correo: admin@jrplatform.com
Contraseña: ChangeMe123!
```

Cámbialas antes de publicar el sistema.

## Calidad del backend

```bash
python -m venv .venv
pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy apps
pytest
```

## Calidad del portal

```bash
cd apps/portal
npm install
npm run check
npm test
npm run build
```

Consulta `docs/sprint-2.md` para ver la arquitectura y los criterios de aceptación.
