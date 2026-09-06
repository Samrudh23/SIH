from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.inspections import router as inspections_router
from app.api.images import router as images_router
from app.api.extractions import router as extractions_router
from app.api.analysis import router as analysis_router
from app.api.dashboard import router as dashboard_router
from app.api.reports import router as reports_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router)
api_router.include_router(inspections_router)
api_router.include_router(images_router)
api_router.include_router(extractions_router)
api_router.include_router(analysis_router)
api_router.include_router(dashboard_router)
api_router.include_router(reports_router)
