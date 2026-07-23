FROM node:22-alpine AS portal-builder

WORKDIR /portal

COPY apps/portal/package.json ./
RUN npm install --no-audit --no-fund

COPY apps/portal ./
ENV VITE_API_URL=/api/v1
RUN npm run build

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production
ENV PORTAL_DIST_PATH=/app/static/portal

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY pyproject.toml README.md ./
COPY apps ./apps
RUN pip install --no-cache-dir .

COPY alembic.ini ./
COPY migrations ./migrations
COPY --from=portal-builder /portal/dist /app/static/portal

EXPOSE 10000

CMD ["sh", "-c", "alembic upgrade head && uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT:-10000} --proxy-headers --forwarded-allow-ips=*"]
