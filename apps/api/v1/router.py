from fastapi import APIRouter

from apps.api.v1.routes.auth import router as auth_router
from apps.api.v1.routes.users import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
