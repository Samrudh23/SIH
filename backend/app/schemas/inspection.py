from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.common import WorkflowStatus, ResultState, ImageCoverage

class InspectionCreate(BaseModel):
    product_name: Optional[str] = Field(default=None, description="Known product or commodity name")
    brand_name: Optional[str] = Field(default=None, description="Brand name if known")
    commodity_category: Optional[str] = Field(default=None, description="Classified category if known in advance")
    inspector_id: str = Field(default="inspector_default", description="ID of enforcement officer")
    image_coverage: ImageCoverage = Field(default_factory=ImageCoverage, description="Surfaces provided by inspector")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional custom metadata")

class InspectionNotesUpdate(BaseModel):
    notes: str = Field(..., description="Inspector observations, physical measurements, or notes")

class MedicalDeviceConfirmation(BaseModel):
    is_confirmed_medical_device: bool = Field(
        ...,
        description="Inspector confirmation to route package out of standard PCR into Medical Devices Rules, 2017"
    )

class ImageUploadResponse(BaseModel):
    evidence_id: str = Field(..., description="Evidence ID")
    inspection_id: str = Field(..., description="Inspection ID")
    file_name: str = Field(..., description="Stored safe filename")
    file_url: str = Field(..., description="Access URL for image evidence")
    file_size_bytes: int = Field(..., description="Size of uploaded file in bytes")
    mime_type: str = Field(..., description="MIME content type")
    image_type: str = Field(..., description="Surface label e.g. front, back, side")
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ImageSurfaceUpdate(BaseModel):
    surface: str = Field(..., description="Package surface: front, back, side, top, pdp")

class CoverageUpdate(BaseModel):
    coverage: ImageCoverage = Field(..., description="Updated package surface checklist")

class InspectionResponse(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    status: WorkflowStatus
    compliance_status: Optional[str] = Field(default="PENDING", description="Overall screening result state or PENDING")
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    commodity_category: Optional[str] = None
    inspector_id: str
    image_coverage: ImageCoverage
    notes: Optional[str] = None
    is_medical_device_confirmed: Optional[bool] = Field(
        default=None,
        description="Inspector confirmation: None (pending), True (confirmed medical device), False (rejected)",
    )
    images_count: int = 0
    has_extraction: bool = False
    has_result: bool = False

class InspectionListResponse(BaseModel):
    total: int
    items: List[InspectionResponse]
