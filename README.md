# JR Platform

JR Platform es una API base construida con FastAPI, PostgreSQL, SQLAlchemy y Alembic.

## Sprint 1

Esta entrega incorpora:

- Registro de usuarios.
- Inicio de sesión con JWT.
- Contraseñas protegidas con PBKDF2-SHA256.
- Roles `admin` y `user`.
- Endpoints protegidos.
- Creación automática de un administrador inicial.
- Migración de la tabla `users`.
- Pruebas automáticas de autenticación y autorización.

## Requisitos

- Docker Desktop en funcionamiento.
- Git.

## Instalación

Copia el archivo de entorno si todavía no existe:

```powershell
Copy-Item .env.example .env
```

Abre `.env` y cambia al menos:

```text
JWT_SECRET_KEY
INITIAL_ADMIN_PASSWORD
```

Arranca el proyecto:

```powershell
docker compose up --build
```

## Direcciones

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Estado: http://localhost:8000/health

## Administrador inicial

Al iniciar la API, se crea el administrador definido en `.env` cuando todavía no existe:

```text
INITIAL_ADMIN_EMAIL=admin@jrplatform.local
INITIAL_ADMIN_PASSWORD=ChangeMe123!
```

Cambia esa contraseña antes de utilizar el proyecto fuera de desarrollo.

## Endpoints principales

```text
POST  /api/v1/auth/register
POST  /api/v1/auth/login
GET   /api/v1/users/me
GET   /api/v1/users
PATCH /api/v1/users/{user_id}/role
```

Los dos últimos endpoints requieren el rol `admin`.

## Pruebas locales

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
```

## Calidad

```powershell
ruff check .
ruff format --check .
mypy apps
pytest
```
