from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.extraction import ExtractionPayload
from app.services.inspection_service import inspection_service
from app.models.inspection import ExtractionModel

router = APIRouter(prefix="/inspections", tags=["Extractions (P1 Contract)"])

@router.post(
    "/{inspection_id}/extraction",
    status_code=status.HTTP_200_OK,
    summary="Submit P1 Structured Extraction JSON",
)
def submit_extraction(
    inspection_id: str,
    payload: ExtractionPayload,
    db: Session = Depends(get_db),
):
    """
    Primary integration point for P1 (AI / OCR / CV pipeline).
    Validates submitted declarations according to the Extraction Schema.
    Rejects malformed data with detailed 422 errors.
    """
    extraction_record = inspection_service.save_extraction(db, inspection_id, payload)
    return {
        "status": "success",
        "message": "Extraction received and validated successfully.",
        "inspection_id": inspection_id,
        "extraction_id": extraction_record.id,
        "created_at": extraction_record.created_at,
    }

@router.get(
    "/{inspection_id}/extraction",
    response_model=ExtractionPayload,
    summary="Get Stored Extraction Payload",
)
def get_extraction(
    inspection_id: str,
    db: Session = Depends(get_db),
):
    inspection = inspection_service.get_inspection(db, inspection_id)
    extraction = db.query(ExtractionModel).filter(ExtractionModel.inspection_id == inspection_id).first()
    if not extraction:
        raise HTTPException(
            status_code=404,
            detail=f"No extraction found for inspection '{inspection_id}'."
        )
    return ExtractionPayload.model_validate(extraction.payload)
