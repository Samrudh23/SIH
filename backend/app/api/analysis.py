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

@router.get(
    "/{inspection_id}/rules/{rule_id}",
    summary="Retrieve Single Compliance Rule Result",
)
@router.get(
    "/{inspection_id}/result/rules/{rule_id}",
    summary="Retrieve Single Compliance Rule Result (Alias)",
)
def get_single_rule_result(
    inspection_id: str,
    rule_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieves the specific evaluation finding and evidence for a single rule ID
    (e.g., REQ-MVP-01, REQ-MVP-02, REQ-MVP-11).
    """
    inspection = inspection_service.get_inspection(db, inspection_id)
    result_record = db.query(ComplianceResultModel).filter(ComplianceResultModel.inspection_id == inspection_id).first()
    if not result_record:
        raise HTTPException(
            status_code=404,
            detail=f"No compliance result found for inspection '{inspection_id}'. Run analyze first."
        )

    for rule in result_record.rule_results or []:
        if rule.get("rule_id", "").upper() == rule_id.upper():
            return rule

    raise HTTPException(
        status_code=404,
        detail=f"Rule '{rule_id}' not found in compliance results for inspection '{inspection_id}'."
    )

@router.get(
    "/{inspection_id}/manual-review",
    summary="Retrieve Manual Review & Conflict Items",
)
@router.get(
    "/{inspection_id}/review",
    summary="Retrieve Manual Review & Conflict Items (Alias)",
)
def get_manual_review_items(
    inspection_id: str,
    db: Session = Depends(get_db),
):
    """
    Dedicated endpoint for the frontend Manual Review Workspace (Screen 6).
    Returns all rule findings that require human verification:
    - Findings with status NEEDS_MANUAL_REVIEW or NOT_DETECTED
    - Conflict objects across surfaces (MRP, Net Quantity)
    - Medical Device Confirmation Gate state (Fix 2)
    - Submitted surface coverage checklist
    """
    inspection = inspection_service.get_inspection(db, inspection_id)
    result_record = db.query(ComplianceResultModel).filter(ComplianceResultModel.inspection_id == inspection_id).first()
    if not result_record:
        raise HTTPException(
            status_code=404,
            detail=f"No compliance result found for inspection '{inspection_id}'. Run analyze first."
        )

    review_rules = []
    conflicts = []
    for r in result_record.rule_results or []:
        status = r.get("status")
        rule_conf = r.get("conflicts")
        if rule_conf:
            conflicts.append(rule_conf)
        if status in ("NEEDS_MANUAL_REVIEW", "NOT_DETECTED") or r.get("rule_id") == "REQ-MVP-11" or rule_conf:
            review_rules.append(r)

    return {
        "inspection_id": inspection.id,
        "product_name": inspection.product_name,
        "overall_status": result_record.overall_status,
        "is_medical_device_confirmed": inspection.is_medical_device_confirmed,
        "image_coverage": inspection.image_coverage,
        "manual_review_count": len(review_rules),
        "unresolved_rules": review_rules,
        "conflicts": conflicts,
    }
