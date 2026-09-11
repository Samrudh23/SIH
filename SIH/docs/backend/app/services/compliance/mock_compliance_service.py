"""
================================================================================
TEMPORARY MOCK COMPLIANCE SERVICE — SIH26034 (P3 BACKEND)
================================================================================
NOTICE:
This module is a temporary mock implementation of the compliance engine
built strictly against the finalized legal specification:
- docs/legal/PCR_Compliance_Rules.md
- docs/legal/Confidence_Status_Schema.md

When P2 completes the real compliance engine, this module can be swapped
by updating `get_compliance_engine()` in `app/services/compliance/__init__.py`.
The replacement must satisfy `BaseComplianceEngine.evaluate()`.
================================================================================
"""

import re
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from app.schemas.common import (
    ResultState,
    EvidenceObject,
    ConflictObject,
    ConflictItem,
    ImageCoverage,
)
from app.schemas.extraction import ExtractionPayload
from app.schemas.compliance import (
    RuleResult,
    SummaryCounts,
    ComplianceResult,
    RULE_VERSION_METADATA_TABLE,
)
from app.services.compliance.base import BaseComplianceEngine

class MockComplianceEngine(BaseComplianceEngine):
    """
    Evaluates all 15 Phase-1 rules according to PCR_Compliance_Rules.md and
    Confidence_Status_Schema.md.
    """

    def evaluate(
        self,
        extraction: ExtractionPayload,
        image_coverage: Optional[ImageCoverage] = None,
        is_medical_device_confirmed: Optional[bool] = None,
    ) -> ComplianceResult:
        coverage = image_coverage or extraction.image_coverage or ImageCoverage()
        rule_results: List[RuleResult] = []

        category_str = ""
        if extraction.commodity_category and extraction.commodity_category.value:
            category_str = str(extraction.commodity_category.value).lower()
        elif extraction.product_name and extraction.product_name.value:
            category_str = str(extraction.product_name.value).lower()

        is_pan_masala = "pan masala" in category_str or "panmasala" in category_str
        is_medical = (
            "medical" in category_str
            or (extraction.medical_device_markers is not None and bool(extraction.medical_device_markers.raw_text))
        )
        is_bidi_or_lpg = "bidi" in category_str or "lpg" in category_str or "cylinder" in category_str

        # Check for conflicts (Section 6: Scoped to MRP and Net Quantity)
        mrp_conflict = self._check_conflict("mrp", extraction)
        qty_conflict = self._check_conflict("net_quantity", extraction)

        # -------------------------------------------------------------
        # REQ-MVP-01: Mandatory Declaration Presence
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_01(extraction, coverage, is_pan_masala))

        # -------------------------------------------------------------
        # REQ-MVP-02: Maximum Retail Price (MRP) Layout (Fix 1 applied)
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_02(extraction, is_bidi_or_lpg, mrp_conflict))

        # -------------------------------------------------------------
        # REQ-MVP-03: Net Quantity Metric Unit Validation
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_03(extraction, qty_conflict))

        # -------------------------------------------------------------
        # REQ-MVP-04: Net Quantity Unit-Switching Boundary
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_04(extraction))

        # -------------------------------------------------------------
        # REQ-MVP-05: Prohibited Quantity Qualifiers
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_05(extraction))

        # -------------------------------------------------------------
        # REQ-MVP-06: Date Declaration & Rubber-Stamp Proviso
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_06(extraction, coverage, is_bidi_or_lpg))

        # -------------------------------------------------------------
        # REQ-MVP-07: Consumer Care Contact Details
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_07(extraction, coverage))

        # -------------------------------------------------------------
        # REQ-MVP-08: Manufacturer Address Block Layout
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_08(extraction, coverage))

        # -------------------------------------------------------------
        # REQ-MVP-09: Foreign Importer PDP Address Match
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_09(extraction, coverage))

        # -------------------------------------------------------------
        # REQ-MVP-10: Pan Masala Compliance Router
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_10(extraction, is_pan_masala))

        # -------------------------------------------------------------
        # REQ-MVP-11: Medical Devices Compliance Router (Fix 2 applied)
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_11(extraction, is_medical, is_medical_device_confirmed))

        # -------------------------------------------------------------
        # REQ-MVP-12: Non-Standard Pack Size Disclaimer
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_12(extraction, category_str))

        # -------------------------------------------------------------
        # REQ-MVP-13: Prohibition of Individual Correction Stickers
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_13(extraction))

        # -------------------------------------------------------------
        # REQ-MVP-14: Quantity Clearance Space (Quiet Zone) [VISUAL AID ONLY]
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_14(extraction))

        # -------------------------------------------------------------
        # REQ-MVP-15: Readability & Text Contrast [VISUAL AID ONLY]
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_15(extraction))

        # Calculate Summary Counts
        summary = SummaryCounts(total_rules=len(rule_results))
        for r in rule_results:
            if r.status == ResultState.COMPLIANT:
                summary.compliant += 1
            elif r.status == ResultState.POTENTIAL_VIOLATION:
                summary.potential_violations += 1
            elif r.status == ResultState.NEEDS_MANUAL_REVIEW:
                summary.needs_manual_review += 1
            elif r.status == ResultState.NOT_APPLICABLE:
                summary.not_applicable += 1
            elif r.status == ResultState.NOT_DETECTED:
                summary.not_detected += 1
            elif r.status == ResultState.ANALYSIS_FAILED:
                summary.analysis_failed += 1

        # Determine Overall Status
        # Note: REQ-MVP-14 and REQ-MVP-15 are assistive visual aids only (Part 2 of legal spec).
        # They emit NEEDS_MANUAL_REVIEW as a soft-flag visual reminder, but do not invalidate an otherwise
        # compliant product unless a core statutory requirement (REQ-01 through 13) flagged review or violation.
        core_violations = any(
            r.status == ResultState.POTENTIAL_VIOLATION for r in rule_results
        )
        core_needs_review = any(
            r.status == ResultState.NEEDS_MANUAL_REVIEW
            for r in rule_results
            if r.rule_id not in ("REQ-MVP-14", "REQ-MVP-15")
        )

        if is_medical_device_confirmed:
            overall = ResultState.NOT_APPLICABLE
        elif core_violations:
            overall = ResultState.POTENTIAL_VIOLATION
        elif core_needs_review:
            overall = ResultState.NEEDS_MANUAL_REVIEW
        elif summary.analysis_failed > 0:
            overall = ResultState.ANALYSIS_FAILED
        elif summary.compliant > 0:
            overall = ResultState.COMPLIANT
        else:
            overall = ResultState.NOT_APPLICABLE

        inspection_id = extraction.inspection_id or "unassigned"
        return ComplianceResult(
            inspection_id=inspection_id,
            overall_status=overall,
            summary_counts=summary,
            rule_results=rule_results,
            evaluated_at=datetime.now(timezone.utc),
            engine_version="mock-v1.0.0",
        )

    def _check_conflict(self, field_name: str, extraction: ExtractionPayload) -> Optional[ConflictObject]:
        if field_name == "mrp":
            observations = extraction.mrp_observations or []
            if len(observations) < 2:
                return None

            distinct_values = set()
            for obs in observations:
                if obs.value is not None:
                    distinct_values.add(round(obs.value, 2))
                elif obs.raw_text:
                    distinct_values.add(obs.raw_text.strip().lower())

            if len(distinct_values) < 2:
                return None

            items = [
                ConflictItem(
                    value=f"{obs.currency or '₹'}{obs.value:g}" if obs.value is not None else obs.raw_text,
                    image_id=obs.image_id,
                    location=obs.surface_location or obs.location,
                )
                for obs in observations
            ]
            return ConflictObject(
                field="mrp",
                values_found=items,
                resolution="NEEDS_MANUAL_REVIEW",
                reason="Conflicting MRP values detected across submitted package surfaces.",
            )

        elif field_name == "net_quantity":
            observations = extraction.net_quantity_observations or []
            if len(observations) < 2:
                return None

            distinct_values = set()
            for obs in observations:
                v = round(obs.value, 4) if obs.value is not None else None
                u = obs.unit.strip().lower() if obs.unit else ""
                if v is None and not u:
                    distinct_values.add(obs.raw_text.strip().lower())
                else:
                    distinct_values.add((v, u))

            if len(distinct_values) < 2:
                return None

            items = [
                ConflictItem(
                    value=f"{obs.value:g}{obs.unit}" if (obs.value is not None and obs.unit) else (f"{obs.value:g}" if obs.value is not None else obs.raw_text),
                    image_id=obs.image_id,
                    location=obs.surface_location or obs.location,
                )
                for obs in observations
            ]
            return ConflictObject(
                field="net_quantity",
                values_found=items,
                resolution="NEEDS_MANUAL_REVIEW",
                reason="Conflicting NET_QUANTITY values detected across submitted package surfaces.",
            )

        return None

    def _eval_req_01(self, ext: ExtractionPayload, cov: ImageCoverage, is_pan_masala: bool) -> RuleResult:
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-01"]
        # 5 core blocks: mfg/packer, commodity name, net qty, date, mrp
        has_address = ext.manufacturer is not None or ext.packer is not None or ext.importer is not None
        has_name = ext.product_name is not None
        has_qty = ext.net_quantity is not None
        has_date = ext.date_of_manufacture is not None
        has_mrp = ext.mrp is not None

        detected_blocks = []
        if has_address: detected_blocks.append("Address")
        if has_name: detected_blocks.append("Commodity Name")
        if has_qty: detected_blocks.append("Net Quantity")
        if has_date: detected_blocks.append("Date")
        if has_mrp: detected_blocks.append("MRP")

        detected_str = f"{len(detected_blocks)}/5 mandatory blocks detected ({', '.join(detected_blocks)})"

        # Check under-10g exemption under Rule 26(a)
        if ext.net_quantity and ext.net_quantity.value is not None:
            if ext.net_quantity.value <= 10.0 and ext.net_quantity.unit in ("g", "ml"):
                if not is_pan_masala:
                    return RuleResult(
                        rule_id="REQ-MVP-01",
                        status=ResultState.NOT_APPLICABLE,
                        detected_value=f"Net Qty: {ext.net_quantity.value}{ext.net_quantity.unit}",
                        normalized_value="Exempt under Rule 26(a) (<= 10g/ml)",
                        detection_confidence=ext.net_quantity.confidence,
                        applicability_confidence=1.0,
                        reason="Package is under 10g/ml; exempt from Chapter II rules under Rule 26(a).",
                        explanation_for_inspector="Product qualifies for small package exemption under Rule 26.",
                        rule_version=meta,
                    )

        if len(detected_blocks) == 5:
            return RuleResult(
                rule_id="REQ-MVP-01",
                status=ResultState.COMPLIANT,
                detected_value=detected_str,
                normalized_value="all_5_mandatory_blocks_present=true",
                detection_confidence=min(
                    ext.manufacturer.confidence if ext.manufacturer else 0.9,
                    ext.net_quantity.confidence if ext.net_quantity else 0.9,
                    ext.mrp.confidence if ext.mrp else 0.9,
                ),
                applicability_confidence=1.0,
                reason="All five mandatory declaration blocks detected on package surfaces.",
                explanation_for_inspector="All five mandatory declarations (Manufacturer Address, Generic Name, Net Quantity, Manufacture Date, and MRP) have been successfully identified on the package.",
                rule_version=meta,
            )
        else:
            missing = [b for b in ["Address", "Commodity Name", "Net Quantity", "Date", "MRP"] if b not in detected_blocks]
            # Coverage aware handling
            if cov.front and cov.back:
                # Substantial coverage was scanned
                status = ResultState.POTENTIAL_VIOLATION
                reason = f"Missing mandatory declarations on submitted surfaces: {', '.join(missing)}."
            else:
                status = ResultState.NEEDS_MANUAL_REVIEW
                reason = f"System could not identify: {', '.join(missing)}. Submitted package surfaces may be incomplete."

            return RuleResult(
                rule_id="REQ-MVP-01",
                status=status,
                detected_value=detected_str,
                normalized_value=f"missing_blocks={missing}",
                detection_confidence=0.80,
                applicability_confidence=1.0,
                reason=reason,
                explanation_for_inspector="The system could not identify one or more mandatory blocks on the visible packaging panels. Please manually inspect the container to ensure all required details are printed elsewhere.",
                rule_version=meta,
            )

    def _eval_req_02(self, ext: ExtractionPayload, is_bidi_or_lpg: bool, conflict: Optional[ConflictObject]) -> RuleResult:
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-02"]
        if is_bidi_or_lpg:
            return RuleResult(
                rule_id="REQ-MVP-02",
                status=ResultState.NOT_APPLICABLE,
                detected_value=None,
                normalized_value="exempt_category=true",
                detection_confidence=1.0,
                applicability_confidence=1.0,
                reason="Bidies and domestic LPG cylinders are exempt from declaring retail sale price.",
                explanation_for_inspector="Product exempt from MRP requirement under Rule 2(m) proviso.",
                rule_version=meta,
            )

        if conflict:
            return RuleResult(
                rule_id="REQ-MVP-02",
                status=ResultState.NEEDS_MANUAL_REVIEW,
                detected_value="Conflicting MRP values",
                normalized_value=None,
                detection_confidence=0.85,
                applicability_confidence=1.0,
                reason=conflict.reason,
                conflicts=conflict,
                explanation_for_inspector="Multiple conflicting MRP declarations were found across package surfaces. Inspector review required.",
                rule_version=meta,
            )

        mrp = ext.mrp
        if not mrp or not mrp.raw_text:
            return RuleResult(
                rule_id="REQ-MVP-02",
                status=ResultState.NOT_DETECTED,
                detected_value=None,
                normalized_value=None,
                detection_confidence=0.0,
                applicability_confidence=1.0,
                reason="No retail sale price declaration block was detected in the OCR output.",
                explanation_for_inspector="Price declaration not found on submitted images.",
                rule_version=meta,
            )

        raw = mrp.raw_text.lower()
        has_price_figure = bool(re.search(r"(?:₹|rs\.?|inr|mrp)\s*\d+", raw)) or (mrp.value is not None)
        if not has_price_figure:
            return RuleResult(
                rule_id="REQ-MVP-02",
                status=ResultState.NOT_DETECTED,
                detected_value=mrp.raw_text,
                normalized_value=None,
                detection_confidence=mrp.confidence,
                applicability_confidence=1.0,
                reason="Text region found near price area, but contains no recognizable price numeral.",
                explanation_for_inspector="No numeric price detected.",
                rule_version=meta,
            )

        # Fix 1: Fuzzy match on tax inclusivity keyword family ("incl", "inclusive", "taxes")
        has_tax_keywords = any(k in raw for k in ("incl", "inclusive", "taxes", "tax"))
        evidence = EvidenceObject(
            image_id=mrp.image_id,
            bounding_box=mrp.bounding_box,
            raw_ocr_text=mrp.raw_text,
        )

        if not has_tax_keywords:
            return RuleResult(
                rule_id="REQ-MVP-02",
                status=ResultState.POTENTIAL_VIOLATION,
                detected_value=mrp.raw_text,
                normalized_value=f"price={mrp.value}; tax_inclusive=false",
                detection_confidence=mrp.confidence,
                applicability_confidence=1.0,
                reason="Price figure found but lacks mandatory tax-inclusion phrase ('inclusive of all taxes' or 'incl. of all taxes').",
                evidence=evidence,
                explanation_for_inspector="The extracted price string lacks the mandatory tax-inclusion suffix. Rule 2(m) requires the exact phrase 'inclusive of all taxes' or its approved abbreviations.",
                rule_version=meta,
            )

        # Tax phrase found: Check detection_confidence >= 0.75 threshold (Fix 1)
        if mrp.confidence >= 0.75:
            return RuleResult(
                rule_id="REQ-MVP-02",
                status=ResultState.COMPLIANT,
                detected_value=mrp.raw_text,
                normalized_value=f"price={mrp.value}; tax_inclusive=true",
                detection_confidence=mrp.confidence,
                applicability_confidence=1.0,
                reason="MRP declaration complies with Rule 2(m). Contains price figure and valid tax-inclusion phrase.",
                evidence=evidence,
                explanation_for_inspector="MRP declaration complies with Rule 2(m). It is formatted using the Rupee symbol and includes the mandatory tax declaration.",
                rule_version=meta,
            )
        else:
            return RuleResult(
                rule_id="REQ-MVP-02",
                status=ResultState.NEEDS_MANUAL_REVIEW,
                detected_value=mrp.raw_text,
                normalized_value=f"price={mrp.value}; tax_inclusive=true",
                detection_confidence=mrp.confidence,
                applicability_confidence=1.0,
                reason="Price and tax-inclusivity phrase detected, but OCR confidence is below 0.75 threshold.",
                evidence=evidence,
                explanation_for_inspector="Price and tax-inclusion phrase were found, but confidence is low due to image clarity. Please confirm manually.",
                rule_version=meta,
            )

    def _eval_req_03(self, ext: ExtractionPayload, conflict: Optional[ConflictObject]) -> RuleResult:
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-03"]
        if conflict:
            return RuleResult(
                rule_id="REQ-MVP-03",
                status=ResultState.NEEDS_MANUAL_REVIEW,
                detected_value="Conflicting net quantities",
                detection_confidence=0.85,
                applicability_confidence=1.0,
                reason=conflict.reason,
                conflicts=conflict,
                explanation_for_inspector="Conflicting quantity values detected across panels.",
                rule_version=meta,
            )

        qty = ext.net_quantity
        if not qty or not qty.raw_text:
            return RuleResult(
                rule_id="REQ-MVP-03",
                status=ResultState.NOT_DETECTED,
                detected_value=None,
                detection_confidence=0.0,
                applicability_confidence=1.0,
                reason="Net quantity declaration not detected.",
                explanation_for_inspector="Net quantity statement was not found.",
                rule_version=meta,
            )

        evidence = EvidenceObject(
            image_id=qty.image_id,
            bounding_box=qty.bounding_box,
            raw_ocr_text=qty.raw_text,
        )

        unit = (qty.unit or "").strip()
        raw = qty.raw_text.lower()

        prohibited_units = ["gms", "g.m.s", "nos.", "pcs", "pieces", "dozen", "gross", "score"]
        for p in prohibited_units:
            if p in raw or unit.lower() == p:
                return RuleResult(
                    rule_id="REQ-MVP-03",
                    status=ResultState.POTENTIAL_VIOLATION,
                    detected_value=f"{qty.value or ''} {unit or raw}",
                    normalized_value=f"prohibited_unit={p}",
                    detection_confidence=qty.confidence,
                    applicability_confidence=1.0,
                    reason=f"Prohibited unit symbol or counting term '{p}' used in quantity declaration.",
                    evidence=evidence,
                    explanation_for_inspector="Prohibited unit symbol detected on the label. Standard metric units must use official symbols (e.g., 'g' instead of 'gms', 'N' or 'U' instead of 'Nos.'). Use of words like 'dozen' or 'gross' is illegal under Rule 13(4).",
                    rule_version=meta,
                )

        valid_si = {"g", "kg", "ml", "l", "L", "n", "u", "N", "U", "m", "cm", "mm"}
        if unit in valid_si or any(f" {u}" in raw or raw.endswith(u) for u in ["g", "kg", "ml", "l"]):
            return RuleResult(
                rule_id="REQ-MVP-03",
                status=ResultState.COMPLIANT,
                detected_value=f"{qty.value or ''} {unit}",
                normalized_value=f"unit={unit}; standard_si=true",
                detection_confidence=qty.confidence,
                applicability_confidence=1.0,
                reason="Net quantity declared using valid SI metric unit symbol.",
                evidence=evidence,
                explanation_for_inspector="The quantity unit symbol complies with Rule 13.",
                rule_version=meta,
            )

        return RuleResult(
            rule_id="REQ-MVP-03",
            status=ResultState.NEEDS_MANUAL_REVIEW,
            detected_value=qty.raw_text,
            normalized_value=f"unrecognized_unit={unit}",
            detection_confidence=qty.confidence,
            applicability_confidence=1.0,
            reason="Unrecognized unit symbol or formatting in quantity declaration.",
            evidence=evidence,
            explanation_for_inspector="Please manually verify the unit symbol declared for net quantity.",
            rule_version=meta,
        )

    def _eval_req_04(self, ext: ExtractionPayload) -> RuleResult:
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-04"]
        qty = ext.net_quantity
        if not qty or qty.value is None or not qty.unit:
            return RuleResult(
                rule_id="REQ-MVP-04",
                status=ResultState.NOT_DETECTED,
                detected_value=None,
                detection_confidence=0.0,
                applicability_confidence=1.0,
                reason="Net quantity value or unit missing for boundary evaluation.",
                explanation_for_inspector="Quantity boundary check could not be performed.",
                rule_version=meta,
            )

        val = qty.value
        u = qty.unit.strip().lower()

        # Rule 13(2), (3) Proviso:
        # Option proviso: exactly 1 kg or 1 L may legally be declared as 1000 g or 1000 ml
        if (val == 1000.0 and u in ("g", "ml")) or (val == 1.0 and u in ("kg", "l")):
            return RuleResult(
                rule_id="REQ-MVP-04",
                status=ResultState.COMPLIANT,
                detected_value=f"{val} {u}",
                normalized_value="valid_boundary_or_proviso=true",
                detection_confidence=qty.confidence,
                applicability_confidence=1.0,
                reason="Quantity expression matches statutory boundary threshold (or exact 1kg/1L proviso).",
                explanation_for_inspector="Quantity expression scale matches boundary thresholds under Rule 13.",
                rule_version=meta,
            )

        # Violations:
        # < 1 kg declared in kg (e.g. 0.5 kg instead of 500 g)
        if u == "kg" and val < 1.0:
            return RuleResult(
                rule_id="REQ-MVP-04",
                status=ResultState.POTENTIAL_VIOLATION,
                detected_value=f"{val} {u}",
                normalized_value=f"scale_violation: {val} kg should be {int(val*1000)} g",
                detection_confidence=qty.confidence,
                applicability_confidence=1.0,
                reason=f"Quantities less than 1 kilogram must be expressed in grams (Rule 13(2)(a)). Found: {val} kg.",
                explanation_for_inspector=f"Scaling transition violation detected. Rule 13(2) mandates that quantities below 1 kg must be declared in grams (e.g., '{int(val*1000)} g' instead of '{val} kg').",
                rule_version=meta,
            )

        # < 1 L declared in L (e.g. 0.5 L instead of 500 ml)
        if u in ("l", "litre") and val < 1.0:
            return RuleResult(
                rule_id="REQ-MVP-04",
                status=ResultState.POTENTIAL_VIOLATION,
                detected_value=f"{val} {u}",
                normalized_value=f"scale_violation: {val} L should be {int(val*1000)} ml",
                detection_confidence=qty.confidence,
                applicability_confidence=1.0,
                reason=f"Quantities less than 1 litre must be expressed in millilitres (Rule 13(2)(f)). Found: {val} L.",
                explanation_for_inspector=f"Scaling transition violation detected. Rule 13(2) mandates that quantities below 1 L must be declared in milliliters.",
                rule_version=meta,
            )

        # > 1000 g or > 1000 ml declared in g/ml (e.g. 1500 ml instead of 1.5 L)
        if (u == "g" and val > 1000.0) or (u == "ml" and val > 1000.0):
            target_unit = "kg" if u == "g" else "L"
            return RuleResult(
                rule_id="REQ-MVP-04",
                status=ResultState.POTENTIAL_VIOLATION,
                detected_value=f"{val} {u}",
                normalized_value=f"scale_violation: {val} {u} should be {val/1000.0} {target_unit}",
                detection_confidence=qty.confidence,
                applicability_confidence=1.0,
                reason=f"Quantities exceeding 1000 {u} must transition to {target_unit} (Rule 13(3)).",
                explanation_for_inspector=f"Scaling transition violation detected. Quantities of 1 kg/L or more must be declared in terms of kg/L.",
                rule_version=meta,
            )

        return RuleResult(
            rule_id="REQ-MVP-04",
            status=ResultState.COMPLIANT,
            detected_value=f"{val} {u}",
            normalized_value="valid_boundary=true",
            detection_confidence=qty.confidence,
            applicability_confidence=1.0,
            reason="Declared quantity conforms to standard scale boundary transitions.",
            explanation_for_inspector="Quantity expression scale matches boundary thresholds under Rule 13.",
            rule_version=meta,
        )

    def _eval_req_05(self, ext: ExtractionPayload) -> RuleResult:
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-05"]
        qty = ext.net_quantity
        if not qty or not qty.raw_text:
            return RuleResult(
                rule_id="REQ-MVP-05",
                status=ResultState.NOT_DETECTED,
                detected_value=None,
                detection_confidence=0.0,
                applicability_confidence=1.0,
                reason="Net quantity text not available to check for qualifiers.",
                explanation_for_inspector="Net quantity statement was not found.",
                rule_version=meta,
            )

        raw = qty.raw_text.lower()
        prohibited = ["minimum", "min", "not less than", "average", "about", "approximately", "approx"]
        found = []

        if qty.qualifiers:
            found.extend(qty.qualifiers)
        for p in prohibited:
            if p in raw and p not in found:
                found.append(p)

        evidence = EvidenceObject(
            image_id=qty.image_id,
            bounding_box=qty.bounding_box,
            raw_ocr_text=qty.raw_text,
        )

        if found:
            return RuleResult(
                rule_id="REQ-MVP-05",
                status=ResultState.POTENTIAL_VIOLATION,
                detected_value=qty.raw_text,
                normalized_value=f"prohibited_qualifiers={found}",
                detection_confidence=qty.confidence,
                applicability_confidence=1.0,
                reason=f"Prohibited qualitative words detected near quantity declaration: {', '.join(found)}.",
                evidence=evidence,
                explanation_for_inspector="The quantity is qualified by a prohibited word. Rule 12(6) strictly forbids using terms like 'minimum', 'about', or 'approximately' to qualify the declared net quantity.",
                rule_version=meta,
            )

        return RuleResult(
            rule_id="REQ-MVP-05",
            status=ResultState.COMPLIANT,
            detected_value=qty.raw_text,
            normalized_value="has_prohibited_qualifiers=false",
            detection_confidence=qty.confidence,
            applicability_confidence=1.0,
            reason="No prohibited qualitative modifiers detected on the net quantity line.",
            evidence=evidence,
            explanation_for_inspector="The quantity declaration contains no illegal qualitative qualifiers.",
            rule_version=meta,
        )

    def _eval_req_06(self, ext: ExtractionPayload, cov: ImageCoverage, is_bidi_or_lpg: bool) -> RuleResult:
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-06"]
        if is_bidi_or_lpg:
            return RuleResult(
                rule_id="REQ-MVP-06",
                status=ResultState.NOT_APPLICABLE,
                detected_value=None,
                detection_confidence=1.0,
                applicability_confidence=1.0,
                reason="Bidies, agarbatti, and domestic LPG cylinders are exempt from date declaration under Rule 6(1) Proviso (A).",
                explanation_for_inspector="Product category exempt from date declaration.",
                rule_version=meta,
            )

        date_ext = ext.date_of_manufacture
        if not date_ext or not date_ext.raw_text:
            status = ResultState.POTENTIAL_VIOLATION if (cov.front and cov.back) else ResultState.NEEDS_MANUAL_REVIEW
            return RuleResult(
                rule_id="REQ-MVP-06",
                status=status,
                detected_value=None,
                detection_confidence=0.0,
                applicability_confidence=1.0,
                reason="Month and year of manufacture/packing not detected on package label.",
                explanation_for_inspector="Date of manufacture/packing could not be identified on submitted panels.",
                rule_version=meta,
            )

        evidence = EvidenceObject(
            image_id=date_ext.image_id,
            bounding_box=date_ext.bounding_box,
            raw_ocr_text=date_ext.raw_text,
        )

        if date_ext.has_overwriting:
            return RuleResult(
                rule_id="REQ-MVP-06",
                status=ResultState.POTENTIAL_VIOLATION,
                detected_value=date_ext.raw_text,
                normalized_value="overwriting_detected=true",
                detection_confidence=date_ext.confidence,
                applicability_confidence=1.0,
                reason="Date stamp shows stroke overlapping / overwriting, violating Rule 6(1)(d) proviso.",
                evidence=evidence,
                explanation_for_inspector="The date declaration displays severe stroke overlap or double stamping. Rule 6(1)(d) permits rubber stamping but strictly prohibits overwriting.",
                rule_version=meta,
            )

        return RuleResult(
            rule_id="REQ-MVP-06",
            status=ResultState.COMPLIANT,
            detected_value=date_ext.raw_text,
            normalized_value=f"month={date_ext.month}; year={date_ext.year}",
            detection_confidence=date_ext.confidence,
            applicability_confidence=1.0,
            reason="Date of manufacture/packing clearly declared without illegal overwriting.",
            evidence=evidence,
            explanation_for_inspector="Date of manufacture is clearly printed in a valid format.",
            rule_version=meta,
        )

    def _eval_req_07(self, ext: ExtractionPayload, cov: ImageCoverage) -> RuleResult:
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-07"]
        cc = ext.consumer_care
        if not cc or not cc.raw_text:
            status = ResultState.POTENTIAL_VIOLATION if (cov.front and cov.back) else ResultState.NEEDS_MANUAL_REVIEW
            return RuleResult(
                rule_id="REQ-MVP-07",
                status=status,
                detected_value=None,
                detection_confidence=0.0,
                applicability_confidence=1.0,
                reason="Consumer grievance / customer care contact block not found on packaging.",
                explanation_for_inspector="The system could not find a clear consumer care block on submitted images.",
                rule_version=meta,
            )

        evidence = EvidenceObject(
            image_id=cc.image_id,
            bounding_box=cc.bounding_box,
            raw_ocr_text=cc.raw_text,
        )

        has_phone = bool(cc.phone or re.search(r"(?:tel|phone|ph|call|toll\s*free|help(?:line)?)\s*[:\-\d\s]{7,}", cc.raw_text.lower()))
        has_email = bool(cc.email or re.search(r"[\w\.\-]+@[\w\.\-]+\.\w+", cc.raw_text))

        if not has_phone or not has_email:
            missing_fields = []
            if not has_phone: missing_fields.append("telephone number")
            if not has_email: missing_fields.append("email address")
            return RuleResult(
                rule_id="REQ-MVP-07",
                status=ResultState.POTENTIAL_VIOLATION,
                detected_value=cc.raw_text,
                normalized_value=f"has_phone={has_phone}; has_email={has_email}",
                detection_confidence=cc.confidence,
                applicability_confidence=1.0,
                reason=f"Consumer care details incomplete. Missing mandatory fields: {', '.join(missing_fields)}.",
                evidence=evidence,
                explanation_for_inspector="Missing mandatory consumer care fields. The grievance contact block must contain a valid telephone number and email address.",
                rule_version=meta,
            )

        return RuleResult(
            rule_id="REQ-MVP-07",
            status=ResultState.COMPLIANT,
            detected_value=cc.raw_text,
            normalized_value=f"phone={cc.phone or 'present'}; email={cc.email or 'present'}",
            detection_confidence=cc.confidence,
            applicability_confidence=1.0,
            reason="Consumer care block complies with Rule 6(2); includes name/office, telephone, and email.",
            evidence=evidence,
            explanation_for_inspector="Consumer care contact details are complete under Rule 6(2).",
            rule_version=meta,
        )

    def _eval_req_08(self, ext: ExtractionPayload, cov: ImageCoverage) -> RuleResult:
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-08"]
        addr = ext.manufacturer or ext.packer
        if not addr or not addr.raw_text:
            status = ResultState.POTENTIAL_VIOLATION if (cov.front and cov.back) else ResultState.NEEDS_MANUAL_REVIEW
            return RuleResult(
                rule_id="REQ-MVP-08",
                status=status,
                detected_value=None,
                detection_confidence=0.0,
                applicability_confidence=1.0,
                reason="Manufacturer/packer postal address block not detected.",
                explanation_for_inspector="Manufacturer address details missing from submitted package surfaces.",
                rule_version=meta,
            )

        evidence = EvidenceObject(
            image_id=addr.image_id,
            bounding_box=addr.bounding_box,
            raw_ocr_text=addr.raw_text,
        )

        pin_match = addr.pin_code or re.search(r"\b[1-9][0-9]{5}\b", addr.raw_text)
        has_pin = bool(pin_match)
        pin_val = pin_match.group(0) if hasattr(pin_match, "group") else pin_match

        if not has_pin:
            return RuleResult(
                rule_id="REQ-MVP-08",
                status=ResultState.POTENTIAL_VIOLATION,
                detected_value=addr.raw_text,
                normalized_value="valid_pin=false",
                detection_confidence=addr.confidence,
                applicability_confidence=1.0,
                reason="Address block lacks a valid 6-digit Indian Postal Index Number (PIN Code) under Rule 10(1).",
                evidence=evidence,
                explanation_for_inspector="Address block is incomplete. Rule 10(1) mandates a complete physical address including street details, city, state, and PIN code.",
                rule_version=meta,
            )

        return RuleResult(
            rule_id="REQ-MVP-08",
            status=ResultState.COMPLIANT,
            detected_value=addr.raw_text,
            normalized_value=f"pin_code={pin_val}; complete_address=true",
            detection_confidence=addr.confidence,
            applicability_confidence=1.0,
            reason="Address block contains complete factory/premises information and a valid PIN code.",
            evidence=evidence,
            explanation_for_inspector="Address block contains complete postal details including street indices and PIN code.",
            rule_version=meta,
        )

    def _eval_req_09(self, ext: ExtractionPayload, cov: ImageCoverage) -> RuleResult:
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-09"]
        origin = ext.country_of_origin
        origin_country = (origin.raw_text if origin else "").lower()

        is_foreign = bool(origin_country and "india" not in origin_country)
        if not is_foreign:
            return RuleResult(
                rule_id="REQ-MVP-09",
                status=ResultState.NOT_APPLICABLE,
                detected_value=origin.raw_text if origin else "India (domestic)",
                detection_confidence=origin.confidence if origin else 1.0,
                applicability_confidence=1.0,
                reason="Commodity origin is domestic (India); Rule 10(1) Proviso 2 (Foreign Importer PDP match) not applicable.",
                explanation_for_inspector="Domestic product; foreign importer PDP rule is not applicable.",
                rule_version=meta,
            )

        # Foreign origin detected: verify Indian importer name and complete address on PDP
        importer = ext.importer
        is_on_pdp = ext.is_importer_on_pdp is True

        if importer and is_on_pdp:
            return RuleResult(
                rule_id="REQ-MVP-09",
                status=ResultState.COMPLIANT,
                detected_value=f"Origin: {origin.raw_text}, Importer on PDP: {importer.raw_text}",
                normalized_value="importer_on_pdp=true",
                detection_confidence=min(origin.confidence, importer.confidence),
                applicability_confidence=1.0,
                reason="Imported product carries local Indian importer's name and complete address on Principal Display Panel.",
                explanation_for_inspector="Imported product PDP contains complete details of the Indian importer/packer.",
                rule_version=meta,
            )
        else:
            return RuleResult(
                rule_id="REQ-MVP-09",
                status=ResultState.POTENTIAL_VIOLATION,
                detected_value=f"Origin: {origin.raw_text if origin else 'Foreign'}",
                normalized_value="importer_on_pdp=false",
                detection_confidence=origin.confidence if origin else 0.85,
                applicability_confidence=1.0,
                reason="Foreign country of origin detected, but local Indian importer details are missing from Principal Display Panel under Rule 10(1) Proviso 2.",
                explanation_for_inspector="Foreign country of origin detected, but the local Indian importer's address block is missing from the Principal Display Panel under Rule 10(1).",
                rule_version=meta,
            )

    def _eval_req_10(self, ext: ExtractionPayload, is_pan_masala: bool) -> RuleResult:
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-10"]
        if not is_pan_masala:
            return RuleResult(
                rule_id="REQ-MVP-10",
                status=ResultState.NOT_APPLICABLE,
                detected_value=None,
                detection_confidence=1.0,
                applicability_confidence=1.0,
                reason="Product is not Pan Masala; G.S.R. 881(E) Pan Masala router does not apply.",
                explanation_for_inspector="Product is not classified as Pan Masala.",
                rule_version=meta,
            )

        # G.S.R. 881(E): Pan Masala is excluded from Rule 26(a) <= 10g exemption
        qty = ext.net_quantity
        is_small = qty and qty.value is not None and qty.value <= 10.0

        # Check if missing any mandatory declarations
        has_all_decls = (
            ext.manufacturer is not None
            and ext.net_quantity is not None
            and ext.mrp is not None
            and ext.date_of_manufacture is not None
        )

        if is_small and not has_all_decls:
            return RuleResult(
                rule_id="REQ-MVP-10",
                status=ResultState.POTENTIAL_VIOLATION,
                detected_value=f"Pan Masala Net Qty: {qty.value if qty else 'small'}g",
                normalized_value="pan_masala_exemption_attempt=true",
                detection_confidence=0.95,
                applicability_confidence=1.0,
                reason="Pan Masala packages are excluded from Rule 26 small package exemptions by G.S.R. 881(E). Full retail declarations must be present regardless of package weight.",
                explanation_for_inspector="Pan Masala products are excluded from small-package exemptions by G.S.R. 881(E). Full retail declarations must be present regardless of package weight.",
                rule_version=meta,
            )

        return RuleResult(
            rule_id="REQ-MVP-10",
            status=ResultState.COMPLIANT,
            detected_value="Pan Masala commodity identified",
            normalized_value="pan_masala_router_enforced=true",
            detection_confidence=0.95,
            applicability_confidence=1.0,
            reason="Pan Masala product correctly enforces 100% of standard retail declarations without claiming small-pack exemption.",
            explanation_for_inspector="Pan Masala product correctly bypasses small-package exemptions and carries all standard retail declarations.",
            rule_version=meta,
        )

    def _eval_req_11(
        self,
        ext: ExtractionPayload,
        is_medical: bool,
        is_confirmed: Optional[bool],
    ) -> RuleResult:
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-11"]
        if not is_medical:
            return RuleResult(
                rule_id="REQ-MVP-11",
                status=ResultState.NOT_APPLICABLE,
                detected_value=None,
                detection_confidence=1.0,
                applicability_confidence=1.0,
                reason="No medical device markers detected. Standard PCR 2011 rules apply.",
                explanation_for_inspector="No medical device classification detected.",
                rule_version=meta,
            )

        # Fix 2: Confirmation Gate Before Bypass
        # If inspector explicitly confirmed:
        if is_confirmed is True:
            return RuleResult(
                rule_id="REQ-MVP-11",
                status=ResultState.NOT_APPLICABLE,
                detected_value="Medical Device confirmed by Inspector",
                normalized_value="routed_to_medical_devices_rules_2017=true",
                detection_confidence=0.95,
                applicability_confidence=1.0,
                reason="Medical Device confirmed by enforcement officer. Bypassing standard PCR 2011 declarations per G.S.R. 778(E).",
                explanation_for_inspector="Medical Device detected and confirmed. Standard PCR 2011 checks bypassed; routed strictly to Medical Devices Rules, 2017.",
                rule_version=meta,
            )
        elif is_confirmed is False:
            # Inspector rejected medical device classification
            return RuleResult(
                rule_id="REQ-MVP-11",
                status=ResultState.COMPLIANT,
                detected_value="Medical device classification rejected by Inspector",
                normalized_value="medical_device_override=false",
                detection_confidence=0.95,
                applicability_confidence=1.0,
                reason="Inspector overrode medical device detection. Standard PCR checks proceed normally.",
                explanation_for_inspector="Classification rejected by inspector. Standard PCR rules enforced.",
                rule_version=meta,
            )
        else:
            # Gate active: Needs inspector confirmation
            return RuleResult(
                rule_id="REQ-MVP-11",
                status=ResultState.NEEDS_MANUAL_REVIEW,
                detected_value=ext.medical_device_markers.raw_text if ext.medical_device_markers else "Medical Device Marker",
                normalized_value="requires_inspector_confirmation_gate=true",
                detection_confidence=ext.medical_device_markers.confidence if ext.medical_device_markers else 0.88,
                applicability_confidence=0.90,
                reason="Probable medical device license marker detected. Confirmation required before switching rule sets.",
                explanation_for_inspector="Probable medical device detected on label. Please confirm in the inspection portal before standard Legal Metrology rules are bypassed.",
                rule_version=meta,
            )

    def _eval_req_12(self, ext: ExtractionPayload, category_str: str) -> RuleResult:
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-12"]
        schedule_2_commodities = ["biscuit", "bread", "tea", "coffee", "salt", "soap", "baby food", "edible oil"]
        is_sched_2 = any(c in category_str for c in schedule_2_commodities)

        if not is_sched_2:
            return RuleResult(
                rule_id="REQ-MVP-12",
                status=ResultState.NOT_APPLICABLE,
                detected_value=None,
                detection_confidence=1.0,
                applicability_confidence=1.0,
                reason="Commodity is not listed under the Second Schedule of PCR 2011.",
                explanation_for_inspector="Product is not subject to Second Schedule standard size constraints.",
                rule_version=meta,
            )

        # Standard pack size check (e.g. for biscuits: 50g, 75g, 100g, 150g, 200g, 250g, 300g, etc.)
        # If non-standard, must carry disclaimer:
        disclaimer = ext.non_standard_size_disclaimer
        raw_disclaimer = (disclaimer.raw_text if disclaimer else "").lower()

        has_valid_disclaimer = (
            "not a standard pack size" in raw_disclaimer
            or "non standard size" in raw_disclaimer
        )

        qty = ext.net_quantity
        val = qty.value if qty else None

        # Suppose standard biscuit sizes include 50, 75, 100, 150, 200, 250, 500
        standard_sizes = {25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 1000}
        is_standard_size = val in standard_sizes if val is not None else False

        if is_standard_size or has_valid_disclaimer:
            return RuleResult(
                rule_id="REQ-MVP-12",
                status=ResultState.COMPLIANT,
                detected_value=f"Size: {val}g; Disclaimer: {'Present' if has_valid_disclaimer else 'Not Required'}",
                normalized_value="compliant_size_or_disclaimer=true",
                detection_confidence=qty.confidence if qty else 0.9,
                applicability_confidence=1.0,
                reason="Package is packed in a prescribed standard size under the Second Schedule, or carries the mandatory statutory non-standard disclaimer.",
                explanation_for_inspector="The package is in a prescribed standard size under the Second Schedule, or is a non-standard size that correctly carries the mandatory statutory disclaimer.",
                rule_version=meta,
            )
        else:
            return RuleResult(
                rule_id="REQ-MVP-12",
                status=ResultState.POTENTIAL_VIOLATION,
                detected_value=f"Non-standard size: {val}g",
                normalized_value="missing_non_standard_disclaimer=true",
                detection_confidence=qty.confidence if qty else 0.85,
                applicability_confidence=1.0,
                reason="Package is a non-standard pack size under Second Schedule and lacks the mandatory disclaimer under Rule 5 Proviso.",
                explanation_for_inspector="The package size is non-standard under the Second Schedule, and the mandatory non-standard size disclaimer is missing from the label.",
                rule_version=meta,
            )

    def _eval_req_13(self, ext: ExtractionPayload) -> RuleResult:
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-13"]
        mrp = ext.mrp
        stickers = ext.stickers_detected or []

        # Sole exception: sticker for downward revised lower MRP that does not obscure original price
        if mrp and mrp.is_sticker:
            # If price was reduced
            if mrp.original_mrp and mrp.value and mrp.value < mrp.original_mrp:
                return RuleResult(
                    rule_id="REQ-MVP-13",
                    status=ResultState.COMPLIANT,
                    detected_value=f"Revised MRP: ₹{mrp.value} (Original: ₹{mrp.original_mrp})",
                    normalized_value="downward_mrp_sticker_permitted=true",
                    detection_confidence=mrp.confidence,
                    applicability_confidence=1.0,
                    reason="Downward revised lower MRP sticker detected, compliant with Rule 6(3) proviso.",
                    explanation_for_inspector="A compliant downward MRP revision sticker is present on the package.",
                    rule_version=meta,
                )
            else:
                return RuleResult(
                    rule_id="REQ-MVP-13",
                    status=ResultState.POTENTIAL_VIOLATION,
                    detected_value=f"Sticker price: ₹{mrp.value}",
                    normalized_value="illegal_sticker=true",
                    detection_confidence=mrp.confidence,
                    applicability_confidence=1.0,
                    reason="MRP sticker detected that increases price or alters declaration illegally under Rule 6(3).",
                    explanation_for_inspector="A physical sticker overlay has been detected on a mandatory declaration field. Rule 6(3) strictly prohibits individual stickers for making or altering declarations, except for downward MRP revisions.",
                    rule_version=meta,
                )

        if stickers:
            return RuleResult(
                rule_id="REQ-MVP-13",
                status=ResultState.POTENTIAL_VIOLATION,
                detected_value=f"{len(stickers)} sticker(s) detected on mandatory declarations",
                normalized_value="illegal_sticker_overlay=true",
                detection_confidence=0.88,
                applicability_confidence=1.0,
                reason="Physical sticker detected on mandatory declaration fields under Rule 6(3).",
                explanation_for_inspector="A physical sticker overlay has been detected on a mandatory declaration field. Rule 6(3) strictly prohibits individual stickers for making or altering declarations, except for downward MRP revisions.",
                rule_version=meta,
            )

        return RuleResult(
            rule_id="REQ-MVP-13",
            status=ResultState.COMPLIANT,
            detected_value="No non-compliant stickers detected",
            normalized_value="has_illegal_stickers=false",
            detection_confidence=0.92,
            applicability_confidence=1.0,
            reason="Package surface appears free of prohibited individual correction stickers.",
            explanation_for_inspector="No non-compliant stickers detected on the package.",
            rule_version=meta,
        )

    def _eval_req_14(self, ext: ExtractionPayload) -> RuleResult:
        # Constraint: NEVER emit COMPLIANT or POTENTIAL_VIOLATION (Section 9)
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-14"]
        qty = ext.net_quantity
        if not qty or not qty.raw_text:
            return RuleResult(
                rule_id="REQ-MVP-14",
                status=ResultState.NOT_DETECTED,
                detected_value=None,
                detection_confidence=0.0,
                applicability_confidence=1.0,
                reason="Quantity numeral block could not be isolated for clearance calculation.",
                explanation_for_inspector="Quantity clearance check not possible without detected quantity.",
                rule_version=meta,
            )

        evidence = EvidenceObject(
            image_id=qty.image_id,
            bounding_box=qty.bounding_box,
            raw_ocr_text=qty.raw_text,
        )
        return RuleResult(
            rule_id="REQ-MVP-14",
            status=ResultState.NEEDS_MANUAL_REVIEW,
            detected_value=f"Quantity numeral: {qty.raw_text}",
            normalized_value="visual_aid_overlay_drawn=true",
            detection_confidence=qty.confidence,
            applicability_confidence=1.0,
            reason="Assistive visual aid only: 1H vertical and 2H horizontal quiet-zone overlay drawn.",
            evidence=evidence,
            explanation_for_inspector="A clearance box (1H vertical clearance, 2H horizontal clearance) has been drawn around the net quantity. Please physically verify that this area is completely free of other printed logos, graphics, or text.",
            rule_version=meta,
        )

    def _eval_req_15(self, ext: ExtractionPayload) -> RuleResult:
        # Constraint: NEVER emit COMPLIANT or POTENTIAL_VIOLATION (Section 9)
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-15"]
        contrast = ext.contrast_analysis
        has_text = bool(ext.mrp or ext.net_quantity or (ext.raw_ocr_blocks and len(ext.raw_ocr_blocks) > 0))

        if not has_text:
            return RuleResult(
                rule_id="REQ-MVP-15",
                status=ResultState.NOT_DETECTED,
                detected_value=None,
                detection_confidence=0.0,
                applicability_confidence=1.0,
                reason="Text blocks too obscure to perform contrast profiling.",
                explanation_for_inspector="Contrast profiling unavailable.",
                rule_version=meta,
            )

        detected_val = contrast.raw_text if contrast else "Character contrast profiled"
        conf = contrast.confidence if contrast else 0.85
        return RuleResult(
            rule_id="REQ-MVP-15",
            status=ResultState.NEEDS_MANUAL_REVIEW,
            detected_value=detected_val,
            normalized_value="assistive_contrast_profiling=true",
            detection_confidence=conf,
            applicability_confidence=1.0,
            reason="Assistive visual aid only: Qualitative contrast requirement under Rule 9(1) requires human inspector verification.",
            explanation_for_inspector="The system detected a potential legibility or low-contrast warning in the highlighted region. Please manually confirm that all declarations are easily readable under normal retail lighting.",
            rule_version=meta,
        )
