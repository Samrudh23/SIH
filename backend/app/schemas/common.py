from enum import Enum
from typing import Optional, List, Any
from pydantic import BaseModel, Field

class ResultState(str, Enum):
    """
    Final Set — 6 Result States from Confidence_Status_Schema.md
    Automate wherever evidence is strong; escalate to NEEDS_MANUAL_REVIEW
    only where uncertainty genuinely matters.
    """
    COMPLIANT = "COMPLIANT"
    POTENTIAL_VIOLATION = "POTENTIAL_VIOLATION"
    NEEDS_MANUAL_REVIEW = "NEEDS_MANUAL_REVIEW"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_DETECTED = "NOT_DETECTED"
    ANALYSIS_FAILED = "ANALYSIS_FAILED"

class WorkflowStatus(str, Enum):
    """
    Inspection lifecycle state machine
    """
    CREATED = "CREATED"
    IMAGE_UPLOADED = "IMAGE_UPLOADED"
    EXTRACTION_RECEIVED = "EXTRACTION_RECEIVED"
    ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE"
    REPORT_GENERATED = "REPORT_GENERATED"
    FAILED = "FAILED"

class BoundingBox(BaseModel):
    x: float = Field(..., description="X coordinate of top-left corner")
    y: float = Field(..., description="Y coordinate of top-left corner")
    w: float = Field(..., description="Width of bounding box")
    h: float = Field(..., description="Height of bounding box")

class ImageCoverage(BaseModel):
    """
    Image-Coverage-Aware field from Confidence_Status_Schema.md Section 5.
    Inspector-confirmed checklist: front / back / side / top.
    """
    front: bool = Field(default=False, description="Front face submitted")
    back: bool = Field(default=False, description="Back face submitted")
    side: bool = Field(default=False, description="Side face(s) submitted")
    top: bool = Field(default=False, description="Top/bottom face(s) submitted")

class EvidenceObject(BaseModel):
    image_id: Optional[str] = Field(default=None, description="Identifier of image evidence")
    bounding_box: Optional[BoundingBox] = Field(default=None, description="Coordinates on package surface")
    raw_ocr_text: Optional[str] = Field(default=None, description="Exact OCR text extracted")
    crop_url: Optional[str] = Field(default=None, description="Direct URL or endpoint to evidence crop")

class ConflictItem(BaseModel):
    value: Any
    image_id: Optional[str] = None
    location: Optional[str] = None

class ConflictObject(BaseModel):
    """
    Conflict Detection per Section 6 of Confidence_Status_Schema.md.
    Phase 1 scope: MRP and Net Quantity only.
    Always routes to NEEDS_MANUAL_REVIEW if conflicting values detected across surfaces.
    """
    field: str
    values_found: List[ConflictItem]
    resolution: str = "NEEDS_MANUAL_REVIEW"
    reason: str

class RuleVersionMetadata(BaseModel):
    """
    Rule Versioning Metadata from Confidence_Status_Schema.md Section 7.
    """
    source: str = Field(..., description="Source document name")
    clause: str = Field(..., description="Legal clause or rule number")
    gsr_number: str = Field(..., description="G.S.R. notification number")
    verification_status: str = Field(..., description="Verification status e.g. VERIFIED — VERBATIM")
    last_verified: str = Field(default="2026-09-05", description="Verification date")
