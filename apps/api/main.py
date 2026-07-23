from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.responses import Response

from apps.api.routes.health import router as health_router
from apps.api.v1.router import api_router
from apps.core.bootstrap import create_initial_admin
from apps.core.config import settings
from apps.core.http import SecurityHeadersMiddleware
from apps.core.portal import resolve_portal_file


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    create_initial_admin()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

if settings.security_headers_enabled:
    app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(api_router, prefix="/api/v1")

PORTAL_DIST = Path(settings.portal_dist_path)


@app.get("/", tags=["system"], response_model=None)
def root() -> Response | dict[str, str]:
    portal_index = resolve_portal_file(PORTAL_DIST, "index.html")
    if portal_index is not None:
        return FileResponse(portal_index)
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "portal": "http://localhost:5173",
    }


@app.get("/{full_path:path}", include_in_schema=False)
def portal_fallback(full_path: str) -> FileResponse:
    reserved_prefixes = ("api/", "health", "docs", "redoc", "openapi.json")
    if full_path.startswith(reserved_prefixes):
        raise HTTPException(status_code=404, detail="Ruta no encontrada")

    portal_file = resolve_portal_file(PORTAL_DIST, full_path)
    if portal_file is None:
        raise HTTPException(status_code=404, detail="Portal no disponible")
    return FileResponse(portal_file)
