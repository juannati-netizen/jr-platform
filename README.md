# JR Platform

JR Platform es una base operativa para gestionar usuarios, clientes y trabajos de servicio.

## Sprint actual

**0.4.0 · Gestión operativa**

- FastAPI y PostgreSQL.
- Autenticación JWT, usuarios y roles.
- Portal React + TypeScript.
- Clientes.
- Trabajos, estados, prioridades y responsables.
- Notas de seguimiento.
- Panel con métricas reales.

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

## Calidad

```bash
ruff check .
ruff format --check .
mypy apps
pytest

cd apps/portal
npm run check
npm test
npm run build
```

Consulta `docs/sprint-3.md` para ver el alcance funcional.
