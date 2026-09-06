from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.inspection_service import inspection_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Metrics (P4/P5 Contract)"])

@router.get("/summary", response_model=DashboardSummaryResponse, summary="Enforcement Dashboard Summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
):
    """
    Returns aggregated metrics calculated live from stored inspection records:
    - Total inspections
    - Compliant vs Violations vs Needs Review
    - Top violated compliance rules
    - Recent inspections list
    """
    return inspection_service.get_dashboard_summary(db)
