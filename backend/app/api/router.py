from fastapi import APIRouter

from app.api.routes.auth_routes import router as auth_router
from app.api.routes.health_routes import router as health_router
from app.api.routes.profile_routes import router as profile_router
from app.api.routes.skill_routes import router as skill_router
from app.api.routes.opportunity_routes import router as opportunity_router
from app.api.routes.application_routes import router as application_router




api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(skill_router)
api_router.include_router(opportunity_router)
api_router.include_router( application_router)