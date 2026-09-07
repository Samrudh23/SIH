from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.inspection import ImageUploadResponse, ImageSurfaceUpdate, CoverageUpdate, InspectionResponse
from app.services.storage_service import storage_service
from app.services.inspection_service import inspection_service
from app.models.inspection import ImageEvidenceModel

router = APIRouter(tags=["Evidence & Images"])

@router.post(
    "/inspections/{inspection_id}/image",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Package Image / Evidence",
)
@router.post(
    "/inspections/{inspection_id}/images",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Package Image / Evidence (Plural Alias)",
)
async def upload_inspection_image(
    inspection_id: str,
    request: Request,
    file: UploadFile = File(..., description="Package photograph (JPEG, PNG, WEBP, BMP)"),
    image_type: str = Form("package_image", description="Surface panel e.g. front, back, side, nutrition_label"),
    db: Session = Depends(get_db),
):
    # 1. Save file to safe storage
    evidence_id, safe_name, file_size, mime = await storage_service.save_image(file, inspection_id)
    file_path = str(storage_service.get_file_path(safe_name))

    # 2. Record evidence in DB
    evidence = inspection_service.add_image_evidence(
        db=db,
        inspection_id=inspection_id,
        evidence_id=evidence_id,
        file_name=safe_name,
        original_file_name=file.filename or "unknown",
        file_path=file_path,
        file_size_bytes=file_size,
        mime_type=mime,
        image_type=image_type,
    )

    base_url = str(request.base_url).rstrip("/")
    file_url = f"{base_url}/api/images/{safe_name}"

    return ImageUploadResponse(
        evidence_id=evidence.id,
        inspection_id=evidence.inspection_id,
        file_name=evidence.file_name,
        file_url=file_url,
        file_size_bytes=evidence.file_size_bytes,
        mime_type=evidence.mime_type,
        image_type=evidence.image_type,
        uploaded_at=evidence.uploaded_at,
    )

@router.get("/inspections/{inspection_id}/evidence", summary="Retrieve Inspection Evidence")
@router.get("/inspections/{inspection_id}/images", summary="Retrieve Inspection Evidence (Plural Alias)")
def get_inspection_evidence(
    inspection_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    inspection = inspection_service.get_inspection(db, inspection_id)
    images: List[ImageEvidenceModel] = inspection.images or []
    base_url = str(request.base_url).rstrip("/")

    evidence_items = []
    for img in images:
        evidence_items.append({
            "evidence_id": img.id,
            "inspection_id": img.inspection_id,
            "file_name": img.file_name,
            "image_type": img.image_type,
            "mime_type": img.mime_type,
            "file_size_bytes": img.file_size_bytes,
            "url": f"{base_url}/api/images/{img.file_name}",
            "uploaded_at": img.uploaded_at,
        })

    # Include compliance rule evidence if available
    result = inspection.compliance_result
    rule_evidence = []
    if result and result.rule_results:
        for r in result.rule_results:
            if r.get("evidence"):
                rule_evidence.append({
                    "rule_id": r.get("rule_id"),
                    "status": r.get("status"),
                    "evidence": r.get("evidence"),
                    "explanation": r.get("explanation_for_inspector"),
                })

    return {
        "inspection_id": inspection.id,
        "images": evidence_items,
        "rule_evidence": rule_evidence,
    }

@router.patch(
    "/inspections/{inspection_id}/images/{evidence_id}/surface",
    summary="Assign or Update Package Surface on Uploaded Image",
)
@router.post(
    "/inspections/{inspection_id}/images/{evidence_id}/surface",
    summary="Assign or Update Package Surface on Uploaded Image (POST Alias)",
)
def update_image_surface(
    inspection_id: str,
    evidence_id: str,
    payload: ImageSurfaceUpdate,
    db: Session = Depends(get_db),
):
    evidence = inspection_service.update_image_surface(
        db=db,
        inspection_id=inspection_id,
        evidence_id=evidence_id,
        surface=payload.surface,
    )
    return {
        "status": "success",
        "evidence_id": evidence.id,
        "inspection_id": evidence.inspection_id,
        "image_type": evidence.image_type,
    }

@router.put(
    "/inspections/{inspection_id}/coverage",
    response_model=InspectionResponse,
    summary="Update Package Surface Coverage Checklist",
)
def update_inspection_coverage(
    inspection_id: str,
    payload: CoverageUpdate,
    db: Session = Depends(get_db),
):
    record = inspection_service.update_image_coverage(db, inspection_id, payload.coverage)
    return inspection_service.to_response(record)

@router.get("/images/{file_name}", summary="Serve Stored Image File")
def get_image_file(file_name: str):
    file_path = storage_service.get_file_path(file_name)
    return FileResponse(file_path)
