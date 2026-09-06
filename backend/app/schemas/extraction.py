from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator
from app.schemas.common import BoundingBox, ImageCoverage

class ExtractedField(BaseModel):
    value: Optional[Any] = Field(default=None, description="Parsed logical value")
    raw_text: str = Field(..., description="Raw text identified by OCR")
    confidence: float = Field(..., ge=0.0, le=1.0, description="OCR/model confidence (0.0 - 1.0)")
    bounding_box: Optional[BoundingBox] = Field(default=None, description="Region coordinates")
    image_id: Optional[str] = Field(default=None, description="Image ID where text was found")
    location: Optional[str] = Field(default=None, description="Surface panel e.g. front, back, pdp")

class NetQuantityExtraction(BaseModel):
    value: Optional[float] = Field(default=None, description="Numeric magnitude e.g. 500, 1.5")
    unit: Optional[str] = Field(default=None, description="Declared unit symbol e.g. g, kg, ml, l, gms, Nos.")
    raw_text: str = Field(..., description="Complete raw net quantity text e.g. 'Net Qty: 500g'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    bounding_box: Optional[BoundingBox] = None
    image_id: Optional[str] = None
    surface_location: Optional[str] = Field(default=None, description="Package surface e.g. front, back, side, top")
    location: Optional[str] = Field(default=None, description="Package surface panel (alias for surface_location)")
    qualifiers: Optional[List[str]] = Field(default=None, description="Prohibited qualifiers like 'approx', 'min'")
    quiet_zone_clear: Optional[bool] = Field(default=None, description="Visual aid: is 1Hx2H quiet zone clear")

    @model_validator(mode="before")
    @classmethod
    def _sync_location(cls, data: Any) -> Any:
        if isinstance(data, dict):
            loc = data.get("surface_location") or data.get("location")
            if loc:
                data["surface_location"] = loc
                data["location"] = loc
        return data

class MRPExtraction(BaseModel):
    value: Optional[float] = Field(default=None, description="Parsed numeric price")
    currency: Optional[str] = Field(default="₹", description="Currency symbol or abbreviation")
    tax_inclusivity: Optional[bool] = Field(default=None, description="Whether inclusive of all taxes was found")
    raw_text: str = Field(..., description="Raw price string on package")
    confidence: float = Field(..., ge=0.0, le=1.0, description="OCR confidence")
    bounding_box: Optional[BoundingBox] = None
    image_id: Optional[str] = None
    surface_location: Optional[str] = Field(default=None, description="Package surface e.g. front, back, side, top")
    location: Optional[str] = Field(default=None, description="Package surface panel (alias for surface_location)")
    is_sticker: Optional[bool] = Field(default=False, description="Whether price is printed on an individual sticker")
    original_mrp: Optional[float] = Field(default=None, description="Original printed price if covered by sticker")

    @model_validator(mode="before")
    @classmethod
    def _sync_location(cls, data: Any) -> Any:
        if isinstance(data, dict):
            loc = data.get("surface_location") or data.get("location")
            if loc:
                data["surface_location"] = loc
                data["location"] = loc
        return data

class DateExtraction(BaseModel):
    month: Optional[str] = Field(default=None, description="Month of manufacture/packing")
    year: Optional[str] = Field(default=None, description="Year of manufacture/packing")
    raw_text: str = Field(..., description="Raw date string")
    confidence: float = Field(..., ge=0.0, le=1.0, description="OCR confidence")
    bounding_box: Optional[BoundingBox] = None
    image_id: Optional[str] = None
    is_rubber_stamped: Optional[bool] = Field(default=False, description="Rubber stamped date indicator")
    has_overwriting: Optional[bool] = Field(default=False, description="Detected overlapping stroke/overwriting")

class AddressExtraction(BaseModel):
    premises: Optional[str] = Field(default=None, description="Factory/building premises name/number")
    street: Optional[str] = Field(default=None, description="Street name or landmark")
    city: Optional[str] = Field(default=None, description="City name")
    state: Optional[str] = Field(default=None, description="State name")
    pin_code: Optional[str] = Field(default=None, description="6-digit PIN code")
    raw_text: str = Field(..., description="Full raw address text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    bounding_box: Optional[BoundingBox] = None
    image_id: Optional[str] = None

class ConsumerCareExtraction(BaseModel):
    name_or_office: Optional[str] = Field(default=None, description="Person or office to contact")
    address: Optional[str] = Field(default=None, description="Physical postal address for grievances")
    phone: Optional[str] = Field(default=None, description="Helpline / phone number")
    email: Optional[str] = Field(default=None, description="Consumer care email address")
    raw_text: str = Field(..., description="Raw consumer care block text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence")
    bounding_box: Optional[BoundingBox] = None
    image_id: Optional[str] = None

class ExtractionPayload(BaseModel):
    """
    Contract between P1 (AI/OCR) and P3 (Backend).
    Submitted to POST /api/inspections/{id}/extraction.
    """
    inspection_id: Optional[str] = Field(default=None, description="Inspection ID (optional in payload if in URL)")
    product_name: Optional[ExtractedField] = Field(default=None, description="Generic commodity name")
    commodity_category: Optional[ExtractedField] = Field(default=None, description="Classified category e.g. 'Pan Masala', 'Medical Device', 'Biscuits'")
    manufacturer: Optional[AddressExtraction] = Field(default=None, description="Manufacturer address details")
    packer: Optional[AddressExtraction] = Field(default=None, description="Packer address details")
    importer: Optional[AddressExtraction] = Field(default=None, description="Importer address details")
    country_of_origin: Optional[ExtractedField] = Field(default=None, description="Country of origin e.g. India, Germany")
    is_importer_on_pdp: Optional[bool] = Field(default=None, description="Whether Indian importer address is on Principal Display Panel")
    net_quantity: Optional[NetQuantityExtraction] = Field(default=None, description="Declared net quantity details (highest confidence or primary)")
    net_quantity_observations: List[NetQuantityExtraction] = Field(default_factory=list, description="Per-surface net quantity observations")
    mrp: Optional[MRPExtraction] = Field(default=None, description="Declared retail sale price details (highest confidence or primary)")
    mrp_observations: List[MRPExtraction] = Field(default_factory=list, description="Per-surface MRP observations")
    date_of_manufacture: Optional[DateExtraction] = Field(default=None, description="Month & year of packing/mfg/import")
    consumer_care: Optional[ConsumerCareExtraction] = Field(default=None, description="Customer grievance contact details")
    medical_device_markers: Optional[ExtractedField] = Field(default=None, description="Medical device marker e.g. 'Mfg. Lic. No. MD-123'")
    non_standard_size_disclaimer: Optional[ExtractedField] = Field(default=None, description="Statutory disclaimer for 2nd Schedule non-standard sizes")
    stickers_detected: Optional[List[ExtractedField]] = Field(default_factory=list, description="List of sticker overlays detected")
    contrast_analysis: Optional[ExtractedField] = Field(default=None, description="Contrast/readability score & flagged regions")
    image_coverage: ImageCoverage = Field(default_factory=ImageCoverage, description="Surfaces covered in submitted images")
    raw_ocr_blocks: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="All raw OCR text lines and bounding boxes")

    @model_validator(mode="after")
    def sync_observations(self) -> "ExtractionPayload":
        # MRP sync
        if self.mrp_observations and self.mrp is None:
            self.mrp = max(self.mrp_observations, key=lambda x: x.confidence)
        elif self.mrp and not self.mrp_observations:
            self.mrp_observations = [self.mrp]

        # Net quantity sync
        if self.net_quantity_observations and self.net_quantity is None:
            self.net_quantity = max(self.net_quantity_observations, key=lambda x: x.confidence)
        elif self.net_quantity and not self.net_quantity_observations:
            self.net_quantity_observations = [self.net_quantity]

        return self
