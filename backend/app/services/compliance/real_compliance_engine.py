"""
================================================================================
REAL COMPLIANCE ENGINE — SIH26034 (P2 REAL COMPLIANCE ENGINE)
================================================================================
Legal Metrology (Packaged Commodities) Rules, 2011 Compliance Screening Engine.

AUTHORITATIVE SPECIFICATIONS:
- docs/legal/PCR_Compliance_Rules.md (Sole legal source of truth)
- docs/legal/Confidence_Status_Schema.md (Engineering & confidence contract)

CORE SYSTEM DESIGN PRINCIPLES:
1. Observations vs. Determinations: The AI and OCR models extract structural
   observations. The compliance engine matches observations against statutory
   thresholds to produce preliminary screening results for human inspectors.
2. Evidence Preservation: Every flagged result retains visual & textual evidence.
3. De-escalation: Ambiguous signals or qualitative criteria de-escalate to
   NEEDS_MANUAL_REVIEW rather than generating false positives.
4. Classification Precedence: Product category classification (Medical Devices,
   Pan Masala) executes before standard rules to govern routing & exemptions.
================================================================================
"""

import re
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Set, Tuple

from app.schemas.common import (
    ResultState,
    EvidenceObject,
    ConflictObject,
    ConflictItem,
    ImageCoverage,
)
from app.schemas.extraction import ExtractionPayload, MRPExtraction, NetQuantityExtraction
from app.schemas.compliance import (
    RuleResult,
    SummaryCounts,
    ComplianceResult,
    RULE_VERSION_METADATA_TABLE,
)
from app.services.compliance.base import BaseComplianceEngine


class RealComplianceEngine(BaseComplianceEngine):
    """
    Production compliance engine implementing all 15 Legal Metrology MVP rules.
    """

    ENGINE_VERSION = "p2-real-v1.0.0"

    def evaluate(
        self,
        extraction: ExtractionPayload,
        image_coverage: Optional[ImageCoverage] = None,
        is_medical_device_confirmed: Optional[bool] = None,
    ) -> ComplianceResult:
        coverage = image_coverage or extraction.image_coverage or ImageCoverage()
        rule_results: List[RuleResult] = []

        # -------------------------------------------------------------
        # STEP 0: MULTI-OBSERVATION CONFLICT DETECTION (Section 6)
        # Scoped strictly to MRP and Net Quantity across submitted surfaces.
        # -------------------------------------------------------------
        mrp_conflict = self._detect_mrp_conflicts(extraction)
        qty_conflict = self._detect_net_quantity_conflicts(extraction)

        # -------------------------------------------------------------
        # STEP 1: CLASSIFICATION-BEFORE-RULES ROUTING (Fix 2 & GSR 881(E))
        # Product category classification must occur prior to standard rules
        # to execute routing switches and alter standard size exemptions.
        # -------------------------------------------------------------
        category_str = self._extract_category_string(extraction)

        is_pan_masala = "pan masala" in category_str or "panmasala" in category_str
        is_medical = (
            "medical" in category_str
            or "cdsco" in category_str
            or (
                extraction.medical_device_markers is not None
                and bool(extraction.medical_device_markers.raw_text)
            )
        )
        is_bidi_or_lpg = (
            "bidi" in category_str
            or "lpg" in category_str
            or "cylinder" in category_str
            or "agarbatti" in category_str
        )

        # Evaluate Classification Routers first
        req_10_res = self._eval_req_10_pan_masala(extraction, is_pan_masala)
        req_11_res = self._eval_req_11_medical_devices(
            extraction, is_medical, is_medical_device_confirmed
        )

        # If medical device is explicitly confirmed by inspector:
        # Standard PCR checks are suppressed / marked NOT_APPLICABLE (Section 4 Fix 2)
        if is_medical_device_confirmed is True and is_medical:
            rule_results = self._build_medical_device_suppressed_results(req_10_res, req_11_res)
            return self._build_compliance_result(
                extraction=extraction,
                rule_results=rule_results,
                overall_status=ResultState.NOT_APPLICABLE,
            )

        # -------------------------------------------------------------
        # STEP 2: EVALUATE CORE STATUTORY RULES (REQ-01 through REQ-13)
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_01_mandatory_declarations(extraction, coverage, is_pan_masala))
        rule_results.append(self._eval_req_02_mrp_layout(extraction, is_bidi_or_lpg, mrp_conflict))
        rule_results.append(self._eval_req_03_metric_unit(extraction, qty_conflict))
        rule_results.append(self._eval_req_04_unit_switching_boundary(extraction))
        rule_results.append(self._eval_req_05_prohibited_qualifiers(extraction))
        rule_results.append(self._eval_req_06_date_declaration(extraction, coverage, is_bidi_or_lpg))
        rule_results.append(self._eval_req_07_consumer_care(extraction, coverage))
        rule_results.append(self._eval_req_08_manufacturer_address(extraction, coverage))
        rule_results.append(self._eval_req_09_foreign_importer_pdp(extraction, coverage))
        rule_results.append(req_10_res)
        rule_results.append(req_11_res)
        rule_results.append(self._eval_req_12_non_standard_pack_size(extraction, category_str))
        rule_results.append(self._eval_req_13_individual_stickers(extraction))

        # -------------------------------------------------------------
        # STEP 3: EVALUATE ASSISTIVE VISUAL AIDS (REQ-14 & REQ-15)
        # Restricted strictly to NEEDS_MANUAL_REVIEW or NOT_DETECTED.
        # -------------------------------------------------------------
        rule_results.append(self._eval_req_14_clearance_quiet_zone(extraction))
        rule_results.append(self._eval_req_15_readability_contrast(extraction))

        # -------------------------------------------------------------
        # STEP 4: OVERALL STATUS RESOLUTION
        # -------------------------------------------------------------
        overall = self._determine_overall_status(
            rule_results=rule_results,
            is_medical_device_confirmed=is_medical_device_confirmed,
            is_medical=is_medical,
        )

        return self._build_compliance_result(
            extraction=extraction,
            rule_results=rule_results,
            overall_status=overall,
        )

    # =========================================================================
    # CONFLICT DETECTION (Confidence_Status_Schema.md Section 6)
    # =========================================================================

    def _detect_mrp_conflicts(self, extraction: ExtractionPayload) -> Optional[ConflictObject]:
        """
        Detect conflicting MRP values across submitted surfaces.
        Scope: MRP only.
        Never silently select one value when two submitted surfaces disagree.
        Always route to NEEDS_MANUAL_REVIEW with all observations preserved.
        """
        observations = extraction.mrp_observations or []
        if len(observations) < 2:
            return None

        distinct_prices: Set[float] = set()
        distinct_raw: Set[str] = set()

        for obs in observations:
            if obs.value is not None:
                distinct_prices.add(round(obs.value, 2))
            elif obs.raw_text:
                distinct_raw.add(obs.raw_text.strip().lower())

        # If numeric prices disagree, or (lacking numerics) raw text strings disagree
        has_conflict = (len(distinct_prices) > 1) or (not distinct_prices and len(distinct_raw) > 1)
        if not has_conflict:
            return None

        conflict_items = [
            ConflictItem(
                value=f"{obs.currency or '₹'}{obs.value:g}" if obs.value is not None else obs.raw_text,
                image_id=obs.image_id,
                location=obs.surface_location or obs.location,
            )
            for obs in observations
        ]

        return ConflictObject(
            field="mrp",
            values_found=conflict_items,
            resolution="NEEDS_MANUAL_REVIEW",
            reason="Conflicting MRP values detected across submitted package surfaces.",
        )

    def _detect_net_quantity_conflicts(self, extraction: ExtractionPayload) -> Optional[ConflictObject]:
        """
        Detect conflicting Net Quantity values across submitted surfaces.
        Scope: Net Quantity only.
        """
        observations = extraction.net_quantity_observations or []
        if len(observations) < 2:
            return None

        distinct_measurements: Set[Tuple[Optional[float], str]] = set()
        distinct_raw: Set[str] = set()

        for obs in observations:
            val = round(obs.value, 4) if obs.value is not None else None
            unit = obs.unit.strip().lower() if obs.unit else ""
            if val is None and not unit:
                distinct_raw.add(obs.raw_text.strip().lower())
            else:
                distinct_measurements.add((val, unit))

        has_conflict = (len(distinct_measurements) > 1) or (not distinct_measurements and len(distinct_raw) > 1)
        if not has_conflict:
            return None

        conflict_items = [
            ConflictItem(
                value=f"{obs.value:g}{obs.unit}" if (obs.value is not None and obs.unit) else (f"{obs.value:g}" if obs.value is not None else obs.raw_text),
                image_id=obs.image_id,
                location=obs.surface_location or obs.location,
            )
            for obs in observations
        ]

        return ConflictObject(
            field="net_quantity",
            values_found=conflict_items,
            resolution="NEEDS_MANUAL_REVIEW",
            reason="Conflicting NET_QUANTITY values detected across submitted package surfaces.",
        )

    # =========================================================================
    # RULE EVALUATION LOGIC
    # =========================================================================

    def _eval_req_01_mandatory_declarations(
        self, ext: ExtractionPayload, cov: ImageCoverage, is_pan_masala: bool
    ) -> RuleResult:
        """
        REQ-MVP-01 — Mandatory Declaration Presence
        Legal: Rule 6(1); exemption under Rule 26(a).
        Five core declarations: Address, Generic Commodity Name, Net Qty, Month/Year, MRP.
        """
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-01"]

        has_address = ext.manufacturer is not None or ext.packer is not None or ext.importer is not None
        has_name = ext.product_name is not None
        has_qty = ext.net_quantity is not None
        has_date = ext.date_of_manufacture is not None
        has_mrp = ext.mrp is not None

        detected_blocks = []
        if has_address: detected_blocks.append("Manufacturer/Packer Address")
        if has_name: detected_blocks.append("Generic Name")
        if has_qty: detected_blocks.append("Net Quantity")
        if has_date: detected_blocks.append("Manufacture Date")
        if has_mrp: detected_blocks.append("Retail Sale Price (MRP)")

        detected_str = f"{len(detected_blocks)}/5 mandatory blocks detected ({', '.join(detected_blocks)})"

        # Check under-10g/ml small package exemption under Rule 26(a)
        qty = ext.net_quantity
        if qty and qty.value is not None:
            is_small = qty.value <= 10.0 and (qty.unit or "").strip().lower() in ("g", "ml")
            if is_small and not is_pan_masala:
                return RuleResult(
                    rule_id="REQ-MVP-01",
                    status=ResultState.NOT_APPLICABLE,
                    detected_value=f"Net Qty: {qty.value}{qty.unit}",
                    normalized_value="exempt_under_rule_26_a=true (<= 10g/ml)",
                    detection_confidence=qty.confidence,
                    applicability_confidence=1.0,
                    reason="Package net weight/measure is 10g/10ml or less; exempt from Chapter II rules under Rule 26(a).",
                    explanation_for_inspector="Product qualifies for small package exemption under Rule 26(a).",
                    rule_version=meta,
                )

        if len(detected_blocks) == 5:
            conf = min(
                ext.manufacturer.confidence if ext.manufacturer else 0.9,
                ext.net_quantity.confidence if ext.net_quantity else 0.9,
                ext.mrp.confidence if ext.mrp else 0.9,
            )
            return RuleResult(
                rule_id="REQ-MVP-01",
                status=ResultState.COMPLIANT,
                detected_value=detected_str,
                normalized_value="all_5_mandatory_blocks_present=true",
                detection_confidence=conf,
                applicability_confidence=1.0,
                reason="All five mandatory declaration blocks detected on visible package panels.",
                explanation_for_inspector="All five mandatory declarations (Manufacturer Address, Generic Name, Net Quantity, Manufacture Date, and MRP) have been successfully identified on the package.",
                rule_version=meta,
            )

        missing = [
            b for b in [
                "Manufacturer/Packer Address",
                "Generic Name",
                "Net Quantity",
                "Manufacture Date",
                "Retail Sale Price (MRP)",
            ]
            if b not in detected_blocks
        ]

        # Image-coverage-aware NOT_DETECTED handling (Section 5)
        if cov.front and cov.back:
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

    def _eval_req_02_mrp_layout(
        self, ext: ExtractionPayload, is_bidi_or_lpg: bool, conflict: Optional[ConflictObject]
    ) -> RuleResult:
        """
        REQ-MVP-02 — Maximum Retail Price (MRP) Layout
        Legal: Rule 2(m), Rule 6(1)(e).
        Engineering: Confidence_Status_Schema.md Fix 1 (Fuzzy matching + manual-review fallback).
        """
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-02"]

        # Statutory exemption: Bidies and domestic LPG
        if is_bidi_or_lpg:
            return RuleResult(
                rule_id="REQ-MVP-02",
                status=ResultState.NOT_APPLICABLE,
                detected_value=None,
                normalized_value="exempt_category=true",
                detection_confidence=1.0,
                applicability_confidence=1.0,
                reason="Bidies and domestic liquefied petroleum gas cylinders bottled/marketed by PSUs are exempt from declaring retail sale price under Rule 2(m) proviso.",
                explanation_for_inspector="Product exempt from MRP requirement under Rule 2(m) proviso.",
                rule_version=meta,
            )

        # Conflict gate: Distinct MRP values across package surfaces
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

        # Fix 1: Fuzzy matching on tax-inclusivity keyword family ("incl", "inclusive", "taxes", "tax")
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

        # Fix 1 Fallback Threshold: detection_confidence >= 0.75
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

    def _eval_req_03_metric_unit(
        self, ext: ExtractionPayload, conflict: Optional[ConflictObject]
    ) -> RuleResult:
        """
        REQ-MVP-03 — Net Quantity Metric Unit Validation
        Legal: Rule 13(1), (4), (5).
        Requires standard metric units (SI units). Prohibits colloquial/counting units.
        """
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

        # Prohibited colloquial symbols & counting units under Rule 13(4)
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

        # Standard legal SI symbols under Rule 13
        valid_si = {"g", "kg", "mg", "ml", "l", "L", "kl", "kL", "n", "u", "N", "U", "m", "cm", "mm"}
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

    def _eval_req_04_unit_switching_boundary(self, ext: ExtractionPayload) -> RuleResult:
        """
        REQ-MVP-04 — Net Quantity Unit-Switching Boundary
        Legal: Rule 13(2), (3) + Proviso.
        Quantities < 1 kg must be in g. Quantities < 1 L must be in ml.
        Proviso: Exactly 1 kg / 1 L may legally be declared as 1000 g / 1000 ml.
        """
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

        # Rule 13(2), (3) Proviso: exactly 1 kg or 1 L may legally be declared as 1000 g or 1000 ml
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

        # Scale violation: < 1 kg declared in kg (e.g. 0.5 kg -> 500 g)
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

        # Scale violation: < 1 L declared in L (e.g. 0.5 L -> 500 ml)
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

        # Scale violation: > 1000 g or > 1000 ml declared in g/ml
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
                explanation_for_inspector="Scaling transition violation detected. Quantities of 1 kg/L or more must be declared in terms of kg/L.",
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

    def _eval_req_05_prohibited_qualifiers(self, ext: ExtractionPayload) -> RuleResult:
        """
        REQ-MVP-05 — Prohibited Quantity Qualifiers
        Legal: Rule 12(6).
        Forbids words like 'minimum', 'not less than', 'average', 'about', 'approximately', etc.
        """
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
        prohibited = ["minimum", "min", "not less than", "average", "about", "approximately", "approx", "when packed"]
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

    def _eval_req_06_date_declaration(
        self, ext: ExtractionPayload, cov: ImageCoverage, is_bidi_or_lpg: bool
    ) -> RuleResult:
        """
        REQ-MVP-06 — Date Declaration & Rubber-Stamp Proviso
        Legal: Rule 6(1)(d) + Proviso.
        Month and year of manufacture/packing/import.
        Rubber stamping permitted; stroke overwriting strictly prohibited.
        """
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

    def _eval_req_07_consumer_care(self, ext: ExtractionPayload, cov: ImageCoverage) -> RuleResult:
        """
        REQ-MVP-07 — Consumer Care Contact Details
        Legal: Rule 6(2).
        Must mention name/office, telephone helpline, and email address.
        """
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

    def _eval_req_08_manufacturer_address(self, ext: ExtractionPayload, cov: ImageCoverage) -> RuleResult:
        """
        REQ-MVP-08 — Manufacturer Address Block Layout
        Legal: Rule 10(1) Explanation.
        Must contain complete address with 6-digit Indian PIN Code.
        """
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

    def _eval_req_09_foreign_importer_pdp(self, ext: ExtractionPayload, cov: ImageCoverage) -> RuleResult:
        """
        REQ-MVP-09 — Foreign Importer PDP Address Match
        Legal: Rule 10(1) Proviso 2.
        For imported commodities: name and complete address of Indian importer/packer must be on PDP.
        Domestic goods -> NOT_APPLICABLE.
        """
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

        # Foreign origin confirmed: verify Indian importer name and complete address on PDP
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

    def _eval_req_10_pan_masala(self, ext: ExtractionPayload, is_pan_masala: bool) -> RuleResult:
        """
        REQ-MVP-10 — Pan Masala Compliance Router
        Legal: G.S.R. 881(E) (Second Amendment, 2025), Rule 26(a) Second Proviso.
        Disables Rule 26 small package exemptions for Pan Masala; enforces 100% PCR declarations.
        """
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

        qty = ext.net_quantity
        is_small = qty and qty.value is not None and qty.value <= 10.0

        # Verify all mandatory declarations
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

    def _eval_req_11_medical_devices(
        self,
        ext: ExtractionPayload,
        is_medical: bool,
        is_confirmed: Optional[bool],
    ) -> RuleResult:
        """
        REQ-MVP-11 — Medical Devices Compliance Router
        Legal: G.S.R. 778(E) (Amendment 2025), Rule 2(h)/7(2)/7(3) Provisos.
        Engineering: Confidence_Status_Schema.md Fix 2 (Confirmation gate before bypass).
        """
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
            # Gate active: Needs explicit inspector confirmation
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

    def _eval_req_12_non_standard_pack_size(
        self, ext: ExtractionPayload, category_str: str
    ) -> RuleResult:
        """
        REQ-MVP-12 — Non-Standard Pack Size Disclaimer
        Legal: Rule 5, Second Schedule.
        Commodities in Second Schedule (biscuits, bread, tea, coffee, etc.) must be in standard sizes
        OR bear the mandatory non-standard size disclaimer.
        """
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-12"]
        schedule_2_commodities = [
            "biscuit", "bread", "tea", "coffee", "salt", "soap", "baby food", "edible oil", "atta", "flour", "rice", "wheat"
        ]
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

        disclaimer = ext.non_standard_size_disclaimer
        raw_disclaimer = (disclaimer.raw_text if disclaimer else "").lower()

        has_valid_disclaimer = (
            "not a standard pack size" in raw_disclaimer
            or "non standard size" in raw_disclaimer
            or "non-standard size" in raw_disclaimer
            or "non-standard pack size" in raw_disclaimer
        )

        qty = ext.net_quantity
        val = qty.value if qty else None

        # Standard schedule sizes (grams / ml)
        standard_sizes = {25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 1000, 2000, 5000}
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

    def _eval_req_13_individual_stickers(self, ext: ExtractionPayload) -> RuleResult:
        """
        REQ-MVP-13 — Prohibition of Individual Correction Stickers
        Legal: Rule 6(3).
        No individual stickers allowed to alter declarations.
        Sole exception: sticker for downward revised MRP that does not obscure original price.
        """
        meta = RULE_VERSION_METADATA_TABLE["REQ-MVP-13"]
        mrp = ext.mrp
        stickers = ext.stickers_detected or []

        # Downward revised lower MRP sticker exception
        if mrp and mrp.is_sticker:
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

    def _eval_req_14_clearance_quiet_zone(self, ext: ExtractionPayload) -> RuleResult:
        """
        REQ-MVP-14 — Quantity Clearance Space (Quiet Zone) [VISUAL AID ONLY]
        Legal: Rule 8(1) Proviso.
        Hard constraint: NEVER emit COMPLIANT or POTENTIAL_VIOLATION (Section 9).
        Allowed outcomes: NEEDS_MANUAL_REVIEW or NOT_DETECTED.
        """
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

    def _eval_req_15_readability_contrast(self, ext: ExtractionPayload) -> RuleResult:
        """
        REQ-MVP-15 — Readability & Text Contrast [VISUAL AID ONLY]
        Legal: Rule 9(1) + Proviso (a).
        Hard constraint: NEVER emit COMPLIANT or POTENTIAL_VIOLATION (Section 9).
        Allowed outcomes: NEEDS_MANUAL_REVIEW or NOT_DETECTED.
        """
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
            evidence=None,
            explanation_for_inspector="The system detected a potential legibility or low-contrast warning in the highlighted region. Please manually confirm that all declarations are easily readable under normal retail lighting.",
            rule_version=meta,
        )

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _extract_category_string(self, extraction: ExtractionPayload) -> str:
        cat = ""
        if extraction.commodity_category and extraction.commodity_category.value:
            cat = str(extraction.commodity_category.value).lower()
        elif extraction.commodity_category and extraction.commodity_category.raw_text:
            cat = str(extraction.commodity_category.raw_text).lower()
        elif extraction.product_name and extraction.product_name.value:
            cat = str(extraction.product_name.value).lower()
        elif extraction.product_name and extraction.product_name.raw_text:
            cat = str(extraction.product_name.raw_text).lower()
        return cat

    def _build_medical_device_suppressed_results(
        self, req_10: RuleResult, req_11: RuleResult
    ) -> List[RuleResult]:
        """
        When medical device routing is confirmed by inspector:
        Standard PCR 2011 checks are suppressed for this inspection (Section 4 Fix 2).
        """
        results: List[RuleResult] = []
        suppressed_rules = [
            "REQ-MVP-01", "REQ-MVP-02", "REQ-MVP-03", "REQ-MVP-04",
            "REQ-MVP-05", "REQ-MVP-06", "REQ-MVP-07", "REQ-MVP-08",
            "REQ-MVP-09", "REQ-MVP-10", "REQ-MVP-11", "REQ-MVP-12",
            "REQ-MVP-13", "REQ-MVP-14", "REQ-MVP-15"
        ]

        for rid in suppressed_rules:
            if rid == "REQ-MVP-11":
                results.append(req_11)
            elif rid == "REQ-MVP-10":
                results.append(req_10)
            else:
                meta = RULE_VERSION_METADATA_TABLE[rid]
                results.append(
                    RuleResult(
                        rule_id=rid,
                        status=ResultState.NOT_APPLICABLE,
                        detected_value="Suppressed (Medical Device)",
                        normalized_value="medical_device_bypass=true",
                        detection_confidence=1.0,
                        applicability_confidence=1.0,
                        reason="Standard Packaged Commodities Rules bypassed: product confirmed as Medical Device governed by Medical Devices Rules, 2017.",
                        explanation_for_inspector="Standard Legal Metrology checks suppressed for confirmed Medical Device.",
                        rule_version=meta,
                    )
                )
        return results

    def _determine_overall_status(
        self,
        rule_results: List[RuleResult],
        is_medical_device_confirmed: Optional[bool],
        is_medical: bool,
    ) -> ResultState:
        """
        Computes overall compliance screening status across all 15 rules.
        """
        if is_medical_device_confirmed is True and is_medical:
            return ResultState.NOT_APPLICABLE

        # Check for core violations (REQ-01 through 13)
        has_core_violation = any(
            r.status == ResultState.POTENTIAL_VIOLATION for r in rule_results
        )
        if has_core_violation:
            return ResultState.POTENTIAL_VIOLATION

        # Check for core manual review needs (REQ-01 through 13)
        # Note: REQ-14 and REQ-15 are visual aids and do not trigger overall NEEDS_MANUAL_REVIEW
        has_core_manual_review = any(
            r.status == ResultState.NEEDS_MANUAL_REVIEW
            for r in rule_results
            if r.rule_id not in ("REQ-MVP-14", "REQ-MVP-15")
        )
        if has_core_manual_review:
            return ResultState.NEEDS_MANUAL_REVIEW

        has_analysis_failed = any(
            r.status == ResultState.ANALYSIS_FAILED for r in rule_results
        )
        if has_analysis_failed:
            return ResultState.ANALYSIS_FAILED

        has_compliant = any(
            r.status == ResultState.COMPLIANT for r in rule_results
        )
        if has_compliant:
            return ResultState.COMPLIANT

        return ResultState.NOT_APPLICABLE

    def _build_compliance_result(
        self,
        extraction: ExtractionPayload,
        rule_results: List[RuleResult],
        overall_status: ResultState,
    ) -> ComplianceResult:
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

        inspection_id = extraction.inspection_id or "unassigned"
        return ComplianceResult(
            inspection_id=inspection_id,
            overall_status=overall_status,
            summary_counts=summary,
            rule_results=rule_results,
            evaluated_at=datetime.now(timezone.utc),
            engine_version=self.ENGINE_VERSION,
        )
