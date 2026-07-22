# JR Platform

Base técnica inicial de JR Platform.

## Requisitos

- Docker Desktop
- Git

## Arranque rápido

1. Copia `.env.example` como `.env`.
2. Ejecuta:

```bash
docker compose up --build
```

3. Abre:

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Pruebas locales

```bash
python -m venv .venv
```

En Windows:

```bash
.venv\Scripts\activate
```

En Linux o macOS:

```bash
source .venv/bin/activate
```

Después:

```bash
pip install -e ".[dev]"
pytest
```

## Calidad

```bash
ruff check .
ruff format --check .
mypy apps
pytest
```
