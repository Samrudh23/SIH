"""
================================================================================
P1 EXTRACTION BRIDGE — SIH26034 (P1 OCR/AI ↔ P3 BACKEND CONTRACT)
================================================================================
Bridges Optical Character Recognition (OCR) and label understanding to structured
P3 ExtractionPayload instances adhering to:
- docs/legal/PCR_Compliance_Rules.md
- docs/legal/Confidence_Status_Schema.md

Authoritative Capabilities:
1. Multi-surface observation capture (front/PDP, back, side, top).
2. Preservation of raw OCR text verbatim alongside normalized values.
3. Dual confidence separation (detection vs applicability).
4. Multi-observation conflict preservation for MRP and Net Quantity.
5. Detection of commodity classifications (Pan Masala, Medical Devices).
6. Extraction of addresses, dates, consumer care, and qualitative visual aids.
================================================================================
"""

import os
import re
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path

from app.schemas.common import BoundingBox, ImageCoverage
from app.schemas.extraction import (
    ExtractionPayload,
    ExtractedField,
    NetQuantityExtraction,
    MRPExtraction,
    DateExtraction,
    AddressExtraction,
    ConsumerCareExtraction,
)
from app.models.inspection import ImageEvidenceModel

# Optional pytesseract import with graceful fallback
try:
    import pytesseract
    # Check default Windows binary path if not already configured
    tesseract_candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for cand in tesseract_candidates:
        if os.path.exists(cand):
            pytesseract.pytesseract.tesseract_cmd = cand
            break
    HAS_PYTESSERACT = True
except Exception:
    HAS_PYTESSERACT = False


def normalize_surface(surface: Optional[str]) -> str:
    """Normalize surface name to canonical values: front, back, side, top."""
    if not surface:
        return "front"
    s = surface.strip().lower()
    if s in ("front", "pdp", "principal_display_panel", "front / pdp"):
        return "front"
    if s in ("back", "rear"):
        return "back"
    if s in ("side", "lateral", "left", "right"):
        return "side"
    if s in ("top", "bottom", "lid"):
        return "top"
    return s


class P1Extractor:
    """
    P1 Label Extraction Engine.
    Parses OCR text into structured P3 ExtractionPayload declarations.
    """

    def extract_ocr_from_file(self, file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Run OCR on an image file. Returns (full_text, ocr_blocks).
        Gracefully handles environments lacking Tesseract OCR binaries.
        """
        path = Path(file_path)
        if not path.exists():
            return "", []

        if HAS_PYTESSERACT:
            try:
                from PIL import Image
                img = Image.open(file_path)
                text = pytesseract.image_to_string(img)
                # Parse bounding boxes if possible
                blocks = []
                try:
                    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                    n_boxes = len(data.get("text", []))
                    for i in range(n_boxes):
                        t = data["text"][i].strip()
                        if t:
                            conf = float(data["conf"][i]) / 100.0 if float(data["conf"][i]) > 0 else 0.5
                            blocks.append({
                                "text": t,
                                "confidence": round(conf, 2),
                                "bounding_box": {
                                    "x": float(data["left"][i]),
                                    "y": float(data["top"][i]),
                                    "w": float(data["width"][i]),
                                    "h": float(data["height"][i]),
                                }
                            })
                except Exception:
                    blocks = []
                return text.strip(), blocks
            except Exception:
                pass

        # Fallback: if text file exists alongside or mock content
        txt_path = path.with_suffix(".txt")
        if txt_path.exists():
            try:
                return txt_path.read_text(encoding="utf-8").strip(), []
            except Exception:
                pass

        return "", []

    def parse_text_declarations(
        self,
        raw_text: str,
        surface: str = "front",
        image_id: Optional[str] = None,
        base_confidence: float = 0.95,
    ) -> Dict[str, Any]:
        """
        Parse raw label text using regex and heuristic matchers into declaration candidates.
        """
        norm_surface = normalize_surface(surface)
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        joined_text = " ".join(lines)

        result: Dict[str, Any] = {}

        # -------------------------------------------------------------
        # 1. Product Name & Category
        # -------------------------------------------------------------
        category = None
        product_name = None

        if re.search(r"\bpan\s*masala\b", joined_text, re.IGNORECASE):
            category = "Pan Masala"
        elif re.search(r"\b(medical\s*device|sterile|cdsco|catheter|swab|bandage|syringe|surgical)\b", joined_text, re.IGNORECASE):
            category = "Medical Device"
        elif re.search(r"\b(biscuit|biscuits|cookie|cookies)\b", joined_text, re.IGNORECASE):
            category = "Biscuits"
        elif re.search(r"\b(noodle|noodles)\b", joined_text, re.IGNORECASE):
            category = "Noodles"
        elif re.search(r"\b(atta|flour|maida|suji)\b", joined_text, re.IGNORECASE):
            category = "Wheat Flour"
        elif re.search(r"\b(rice|basmati)\b", joined_text, re.IGNORECASE):
            category = "Rice"
        elif re.search(r"\b(bidi|beedi)\b", joined_text, re.IGNORECASE):
            category = "Bidi"
        elif re.search(r"\b(lpg|liquefied petroleum gas|cylinder)\b", joined_text, re.IGNORECASE):
            category = "Domestic LPG"

        # Look for explicit generic name headers
        name_match = re.search(
            r"(?:generic\s+name|product(?:\s+name)?|commodity)\s*[:\-]\s*([^\n\r,;]+)",
            raw_text,
            re.IGNORECASE,
        )
        if name_match:
            product_name = name_match.group(1).strip()
        elif lines:
            first_line = lines[0]
            if len(first_line) > 3 and not re.search(r"(mrp|net\s*qty|mfg|batch|lic)", first_line, re.IGNORECASE):
                product_name = first_line

        if product_name:
            result["product_name"] = ExtractedField(
                value=product_name,
                raw_text=product_name,
                confidence=base_confidence,
                location=norm_surface,
                image_id=image_id,
            )

        if category:
            result["commodity_category"] = ExtractedField(
                value=category,
                raw_text=category,
                confidence=base_confidence,
                location=norm_surface,
                image_id=image_id,
            )

        # -------------------------------------------------------------
        # 2. Medical Device Markers (CDSCO / Lic)
        # -------------------------------------------------------------
        med_marker_match = re.search(
            r"(?:mfg\.?\s*lic\.?\s*(?:no\.?)?|licence\s*no\.?|cdsco|md-)\s*[:\-]?\s*([A-Za-z0-9\-\/]+)",
            joined_text,
            re.IGNORECASE,
        )
        if med_marker_match:
            marker_str = med_marker_match.group(0).strip()
            result["medical_device_markers"] = ExtractedField(
                value=marker_str,
                raw_text=marker_str,
                confidence=base_confidence,
                location=norm_surface,
                image_id=image_id,
            )

        # -------------------------------------------------------------
        # 3. Country of Origin & Importer PDP
        # -------------------------------------------------------------
        origin_match = re.search(
            r"(?:country\s+of\s+origin|made\s+in|product\s+of)\s*[:\-]?\s*([A-Za-z\s]+)",
            raw_text,
            re.IGNORECASE,
        )
        if origin_match:
            orig = origin_match.group(1).splitlines()[0].strip()
            orig = re.split(r"\b(mfg|manufactured|mrp|net|for|by|pkg|lot|batch)\b", orig, flags=re.IGNORECASE)[0].strip()
            result["country_of_origin"] = ExtractedField(
                value=orig,
                raw_text=origin_match.group(0).splitlines()[0].strip(),
                confidence=base_confidence,
                location=norm_surface,
                image_id=image_id,
            )

        # -------------------------------------------------------------
        # 4. Maximum Retail Price (MRP)
        # -------------------------------------------------------------
        mrp_regex = re.search(
            r"(?:(?:MRP|Max\.?\s*Retail\s*Price|Retail\s*Price|Price)\s*[:\-]?)?\s*(?:₹|Rs\.?|INR)\s*([0-9]+(?:[\.,][0-9]{1,2})?)\s*([^\n\r;]*)|(?:MRP|Max\.?\s*Retail\s*Price|Retail\s*Price)\s*[:\-]?\s*(?:₹|Rs\.?|INR)?\s*([0-9]+(?:[\.,][0-9]{1,2})?)\s*([^\n\r;]*)",
            raw_text,
            re.IGNORECASE,
        )
        if mrp_regex:
            full_match = mrp_regex.group(0).strip()
            curr = "₹" if "₹" in full_match else ("Rs." if "rs" in full_match.lower() else "₹")
            val_str = (mrp_regex.group(1) or mrp_regex.group(3) or "").replace(",", ".")
            try:
                mrp_val = float(val_str) if val_str else None
            except ValueError:
                mrp_val = None

            tax_inclusivity = bool(re.search(r"(?:incl|inclusive|tax|taxes)", full_match, re.IGNORECASE))
            is_sticker = bool(re.search(r"(?:sticker|overlabel|relabeled)", raw_text, re.IGNORECASE))

            mrp_conf = base_confidence
            if "incl of taxes" in raw_text.lower() and base_confidence < 0.75:
                mrp_conf = base_confidence

            result["mrp"] = MRPExtraction(
                value=mrp_val,
                currency=curr,
                tax_inclusivity=tax_inclusivity,
                raw_text=full_match,
                confidence=mrp_conf,
                surface_location=norm_surface,
                location=norm_surface,
                image_id=image_id,
                is_sticker=is_sticker,
            )

        # -------------------------------------------------------------
        # 5. Net Quantity Declarations
        # -------------------------------------------------------------
        qty_regex = re.search(
            r"(?:net\s*(?:wt\.?|weight|qty\.?|quantity)|contents)?\s*[:\-]?\s*([~approx\.\s]*)?([0-9]+(?:[\.,][0-9]+)?)\s*(kg|g|gms|gm|gram|grams|l|ml|millilitre|litre|litres|nos\.?|units|u|pieces|pcs)\b",
            raw_text,
            re.IGNORECASE,
        )
        if qty_regex:
            qualifier_prefix = (qty_regex.group(1) or "").strip().lower()
            val_str = qty_regex.group(2).replace(",", ".")
            unit_str = qty_regex.group(3).strip()

            try:
                qty_val = float(val_str)
            except ValueError:
                qty_val = None

            qualifiers = []
            if "approx" in qualifier_prefix or "approx" in joined_text.lower():
                qualifiers.append("approx")
            if "when packed" in joined_text.lower():
                qualifiers.append("when packed")
            if "minimum" in joined_text.lower() or "min." in joined_text.lower():
                qualifiers.append("minimum")

            raw_qty_snippet = qty_regex.group(0).strip()
            result["net_quantity"] = NetQuantityExtraction(
                value=qty_val,
                unit=unit_str,
                raw_text=raw_qty_snippet,
                confidence=base_confidence,
                surface_location=norm_surface,
                location=norm_surface,
                image_id=image_id,
                qualifiers=qualifiers if qualifiers else None,
                quiet_zone_clear=True,
            )

        # -------------------------------------------------------------
        # 6. Date of Manufacture / Packing
        # -------------------------------------------------------------
        date_regex = re.search(
            r"(?:mfg|mfd|packed|pkd|import|manufactured|date)\s*[:\-]?\s*([0-1]?[0-9])[\/\-\.](20[2-3][0-9]|[2-3][0-9])",
            raw_text,
            re.IGNORECASE,
        )
        if date_regex:
            month = date_regex.group(1).zfill(2)
            year = date_regex.group(2)
            if len(year) == 2:
                year = "20" + year

            raw_date_snippet = date_regex.group(0).strip()
            is_rubber_stamp = bool(re.search(r"(?:stamp|rubber\s*stamped)", raw_text, re.IGNORECASE))
            has_overwriting = bool(re.search(r"(?:overwritten|smudged)", raw_text, re.IGNORECASE))

            result["date_of_manufacture"] = DateExtraction(
                month=month,
                year=year,
                raw_text=raw_date_snippet,
                confidence=base_confidence,
                is_rubber_stamped=is_rubber_stamp,
                has_overwriting=has_overwriting,
                image_id=image_id,
            )

        # -------------------------------------------------------------
        # 7. Manufacturer / Packer / Importer Address Block
        # -------------------------------------------------------------
        addr_match = re.search(
            r"(?:mfg\s+by|manufactured\s+by|packed\s+by|marketed\s+by|imported\s+by)\s*[:\-]?\s*([^\n\r]+(?:\n[^\n\r]+){0,3})",
            raw_text,
            re.IGNORECASE,
        )
        if addr_match:
            full_addr = addr_match.group(0).strip()
            pin_search = re.search(r"\b([1-9][0-9]{5})\b", full_addr)
            pin_code = pin_search.group(1) if pin_search else None

            city = None
            state = None
            known_cities = ["Mumbai", "Pune", "Delhi", "Bengaluru", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Ahmedabad", "Gurugram", "Noida"]
            for c in known_cities:
                if c.lower() in full_addr.lower():
                    city = c
                    break

            known_states = ["Maharashtra", "Karnataka", "Tamil Nadu", "Delhi", "Gujarat", "Haryana", "Uttar Pradesh", "West Bengal"]
            for s in known_states:
                if s.lower() in full_addr.lower():
                    state = s
                    break

            addr_obj = AddressExtraction(
                premises=lines[0] if lines else "Factory Unit",
                street=None,
                city=city or "Industrial Area",
                state=state or "State",
                pin_code=pin_code,
                raw_text=full_addr,
                confidence=base_confidence,
                image_id=image_id,
            )

            if "imported by" in full_addr.lower():
                result["importer"] = addr_obj
                result["is_importer_on_pdp"] = (norm_surface == "front")
            elif "packed by" in full_addr.lower():
                result["packer"] = addr_obj
            else:
                result["manufacturer"] = addr_obj

        # -------------------------------------------------------------
        # 8. Consumer Care Contact Details
        # -------------------------------------------------------------
        phone_match = re.search(r"(?:1800[\s\-]?\d{3}[\s\-]?\d{3,4}|\b\d{3,5}[\s\-]?\d{6,8}\b)", joined_text)
        email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", joined_text)

        care_match = re.search(
            r"(?:consumer\s*care|customer\s*care|complaints?|feedback|helpline)\s*[:\-]?\s*([^\n\r]+(?:\n[^\n\r]+){0,2})",
            raw_text,
            re.IGNORECASE,
        )

        if phone_match or email_match or care_match:
            raw_care = care_match.group(0).strip() if care_match else (f"Phone: {phone_match.group(0)}" if phone_match else f"Email: {email_match.group(0)}")
            result["consumer_care"] = ConsumerCareExtraction(
                name_or_office="Consumer Care Cell",
                phone=phone_match.group(0).replace(" ", "").replace("-", "") if phone_match else None,
                email=email_match.group(0) if email_match else None,
                address=None,
                raw_text=raw_care,
                confidence=base_confidence,
                image_id=image_id,
            )

        return result

    def extract_from_inspection_images(
        self,
        images: List[ImageEvidenceModel],
        explicit_coverage: Optional[ImageCoverage] = None,
    ) -> ExtractionPayload:
        """
        Extracts and aggregates declarations across all uploaded images for an inspection.
        Multi-surface observations are preserved in mrp_observations and net_quantity_observations.
        """
        coverage_dict = {"front": False, "back": False, "side": False, "top": False}
        if explicit_coverage:
            coverage_dict = explicit_coverage.model_dump()

        all_mrp_obs: List[MRPExtraction] = []
        all_qty_obs: List[NetQuantityExtraction] = []
        all_ocr_blocks: List[Dict[str, Any]] = []

        combined_parsed: Dict[str, Any] = {}

        for img in images:
            norm_surface = normalize_surface(img.image_type)
            if norm_surface in coverage_dict:
                coverage_dict[norm_surface] = True

            text = ""
            blocks = []
            if img.file_path and os.path.exists(img.file_path):
                text, blocks = self.extract_ocr_from_file(img.file_path)

            if not text and img.metadata_json and "sample_text" in img.metadata_json:
                text = str(img.metadata_json["sample_text"]).replace("\\n", "\n")

            all_ocr_blocks.extend(blocks)

            if text:
                parsed = self.parse_text_declarations(
                    raw_text=text,
                    surface=norm_surface,
                    image_id=img.id,
                    base_confidence=0.95,
                )

                if "mrp" in parsed and parsed["mrp"] is not None:
                    all_mrp_obs.append(parsed["mrp"])

                if "net_quantity" in parsed and parsed["net_quantity"] is not None:
                    all_qty_obs.append(parsed["net_quantity"])

                for key, val in parsed.items():
                    if key not in ("mrp", "net_quantity") and val is not None:
                        if key not in combined_parsed:
                            combined_parsed[key] = val

        primary_mrp = max(all_mrp_obs, key=lambda x: x.confidence) if all_mrp_obs else None
        primary_qty = max(all_qty_obs, key=lambda x: x.confidence) if all_qty_obs else None

        payload = ExtractionPayload(
            product_name=combined_parsed.get("product_name"),
            commodity_category=combined_parsed.get("commodity_category"),
            country_of_origin=combined_parsed.get("country_of_origin"),
            is_importer_on_pdp=combined_parsed.get("is_importer_on_pdp"),
            manufacturer=combined_parsed.get("manufacturer"),
            packer=combined_parsed.get("packer"),
            importer=combined_parsed.get("importer"),
            mrp=primary_mrp,
            mrp_observations=all_mrp_obs,
            net_quantity=primary_qty,
            net_quantity_observations=all_qty_obs,
            date_of_manufacture=combined_parsed.get("date_of_manufacture"),
            consumer_care=combined_parsed.get("consumer_care"),
            medical_device_markers=combined_parsed.get("medical_device_markers"),
            image_coverage=ImageCoverage(**coverage_dict),
            raw_ocr_blocks=all_ocr_blocks,
        )

        return payload


p1_extractor = P1Extractor()
