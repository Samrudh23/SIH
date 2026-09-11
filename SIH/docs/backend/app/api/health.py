from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health", summary="Service Health Check")
def health_check():
    return {
        "status": "ok",
        "service": "sih26034-backend",
        "compliance_engine": settings.COMPLIANCE_ENGINE_TYPE,
        "environment": settings.APP_ENV,
    }
