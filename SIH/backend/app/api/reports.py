from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Reports (P5 Contract)"])

@router.get("/{inspection_id}", summary="Generate/Retrieve Structured Inspection Report (JSON)")
def get_report_json(
    inspection_id: str,
    db: Session = Depends(get_db),
):
    """
    Generates and returns structured inspection report JSON.
    """
    return report_service.generate_report_data(db, inspection_id)

@router.get("/{inspection_id}/html", response_class=HTMLResponse, summary="Generate Printable HTML Inspection Report")
def get_report_html(
    inspection_id: str,
    db: Session = Depends(get_db),
):
    """
    Returns a clean, printable HTML compliance report ready for PDF export or printing.
    """
    return report_service.generate_html_report(db, inspection_id)
