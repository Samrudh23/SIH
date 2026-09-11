from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.inspection import (
    InspectionCreate,
    InspectionResponse,
    InspectionListResponse,
    InspectionNotesUpdate,
    MedicalDeviceConfirmation,
)
from app.schemas.compliance import ComplianceResult
from app.services.inspection_service import inspection_service
from app.services.report_service import report_service
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/inspections", tags=["Inspections"])

@router.post("", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED, summary="Create New Inspection")
def create_inspection(
    payload: InspectionCreate,
    db: Session = Depends(get_db),
):
    record = inspection_service.create_inspection(db, payload)
    return inspection_service.to_response(record)

@router.get("", response_model=InspectionListResponse, summary="List Inspection History")
def list_inspections(
    status: Optional[str] = Query(None, description="Filter by workflow status e.g. CREATED, ANALYSIS_COMPLETE"),
    compliance_status: Optional[str] = Query(None, description="Filter by compliance result e.g. COMPLIANT, POTENTIAL_VIOLATION"),
    product: Optional[str] = Query(None, description="Search by product/brand/category name"),
    has_violations: Optional[bool] = Query(None, description="Filter specifically for potential violations"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total, items = inspection_service.list_inspections(
        db=db,
        status=status,
        compliance_status=compliance_status,
        product_query=product,
        has_violations=has_violations,
        skip=skip,
        limit=limit,
    )
    return InspectionListResponse(
        total=total,
        items=[inspection_service.to_response(item) for item in items],
    )

@router.get("/{inspection_id}", response_model=InspectionResponse, summary="Get Inspection Details")
def get_inspection(
    inspection_id: str,
    db: Session = Depends(get_db),
):
    record = inspection_service.get_inspection(db, inspection_id)
    return inspection_service.to_response(record)

@router.post("/{inspection_id}/notes", response_model=InspectionResponse, summary="Update Inspector Notes")
def update_inspection_notes(
    inspection_id: str,
    payload: InspectionNotesUpdate,
    db: Session = Depends(get_db),
):
    record = inspection_service.update_notes(db, inspection_id, payload.notes)
    return inspection_service.to_response(record)

@router.post("/{inspection_id}/medical-device-confirmation", response_model=ComplianceResult, summary="Medical Device Confirmation Gate (Fix 2)")
def confirm_medical_device_gate(
    inspection_id: str,
    payload: MedicalDeviceConfirmation,
    db: Session = Depends(get_db),
):
    """
    Enforces Fix 2 from Confidence_Status_Schema.md:
    Allows enforcement inspector to confirm or deny that the product is a medical device,
    switching standard PCR rules to NOT_APPLICABLE if confirmed.
    """
    result_record = inspection_service.run_compliance_analysis(
        db=db,
        inspection_id=inspection_id,
        is_medical_device_confirmed=payload.is_confirmed_medical_device,
    )
    return ComplianceResult(
        inspection_id=inspection_id,
        overall_status=result_record.overall_status,
        summary_counts=result_record.summary_counts,
        rule_results=result_record.rule_results,
        evaluated_at=result_record.evaluated_at,
        engine_version=result_record.engine_version,
    )

@router.get("/{inspection_id}/report", summary="Retrieve Inspection Report (JSON)")
def get_inspection_report_json(
    inspection_id: str,
    db: Session = Depends(get_db),
):
    """
    Convenience alias on /api/inspections/{id}/report for retrieving structured JSON report.
    """
    return report_service.generate_report_data(db, inspection_id)

@router.get("/{inspection_id}/report/html", response_class=HTMLResponse, summary="Retrieve Printable HTML Report")
def get_inspection_report_html(
    inspection_id: str,
    db: Session = Depends(get_db),
):
    """
    Convenience alias on /api/inspections/{id}/report/html for printable HTML report.
    """
    return report_service.generate_html_report(db, inspection_id)

