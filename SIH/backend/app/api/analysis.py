from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.compliance import ComplianceResult
from app.services.inspection_service import inspection_service
from app.models.inspection import ComplianceResultModel

router = APIRouter(prefix="/inspections", tags=["Compliance Analysis (P2 Contract)"])

@router.post(
    "/{inspection_id}/analyze",
    response_model=ComplianceResult,
    status_code=status.HTTP_200_OK,
    summary="Trigger Compliance Analysis",
)
def analyze_inspection(
    inspection_id: str,
    db: Session = Depends(get_db),
):
    """
    Triggers compliance evaluation of stored extraction data using the compliance engine.
    Persists the result and returns the finalized Compliance Result JSON matching
    Confidence_Status_Schema.md.
    """
    result_record = inspection_service.run_compliance_analysis(db, inspection_id)
    return ComplianceResult(
        inspection_id=inspection_id,
        overall_status=result_record.overall_status,
        summary_counts=result_record.summary_counts,
        rule_results=result_record.rule_results,
        evaluated_at=result_record.evaluated_at,
        engine_version=result_record.engine_version,
    )

@router.get(
    "/{inspection_id}/result",
    response_model=ComplianceResult,
    summary="Get Compliance Result",
)
def get_compliance_result(
    inspection_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieves the compliance evaluation result for an inspection.
    """
    inspection = inspection_service.get_inspection(db, inspection_id)
    result_record = db.query(ComplianceResultModel).filter(ComplianceResultModel.inspection_id == inspection_id).first()
    if not result_record:
        raise HTTPException(
            status_code=404,
            detail=f"No compliance result has been generated yet for inspection '{inspection_id}'. Run analyze first."
        )

    return ComplianceResult(
        inspection_id=inspection_id,
        overall_status=result_record.overall_status,
        summary_counts=result_record.summary_counts,
        rule_results=result_record.rule_results,
        evaluated_at=result_record.evaluated_at,
        engine_version=result_record.engine_version,
    )
