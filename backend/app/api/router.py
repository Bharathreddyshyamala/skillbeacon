from fastapi import APIRouter

from app.api.routes.auth_routes import router as auth_router
from app.api.routes.health_routes import router as health_router


api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)