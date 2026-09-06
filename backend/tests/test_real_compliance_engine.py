import pytest
from app.schemas.common import (
    ResultState,
    ImageCoverage,
    BoundingBox,
)
from app.schemas.extraction import (
    ExtractionPayload,
    ExtractedField,
    MRPExtraction,
    NetQuantityExtraction,
    DateExtraction,
    AddressExtraction,
    ConsumerCareExtraction,
)
from app.schemas.compliance import RULE_VERSION_METADATA_TABLE
from app.services.compliance.real_compliance_engine import RealComplianceEngine
from app.services.compliance.mock_compliance_service import MockComplianceEngine
from seed.demo_data import DEMO_PRODUCTS


@pytest.fixture
def real_engine():
    return RealComplianceEngine()


@pytest.fixture
def mock_engine():
    return MockComplianceEngine()


# -----------------------------------------------------------------------------
# 1. Fully Compliant Product
# -----------------------------------------------------------------------------
def test_fully_compliant_product(real_engine):
    extraction = DEMO_PRODUCTS[0]["extraction"]
    res = real_engine.evaluate(extraction)

    assert res.overall_status == ResultState.COMPLIANT
    assert res.summary_counts.compliant >= 10
    assert res.summary_counts.potential_violations == 0
    assert len(res.rule_results) == 15
    assert res.engine_version == "p2-real-v1.0.0"

    rules_map = {r.rule_id: r for r in res.rule_results}
    assert rules_map["REQ-MVP-01"].status == ResultState.COMPLIANT
    assert rules_map["REQ-MVP-02"].status == ResultState.COMPLIANT
    assert rules_map["REQ-MVP-03"].status == ResultState.COMPLIANT
    assert rules_map["REQ-MVP-04"].status == ResultState.COMPLIANT
    assert rules_map["REQ-MVP-05"].status == ResultState.COMPLIANT
    assert rules_map["REQ-MVP-06"].status == ResultState.COMPLIANT
    assert rules_map["REQ-MVP-07"].status == ResultState.COMPLIANT
    assert rules_map["REQ-MVP-08"].status == ResultState.COMPLIANT


# -----------------------------------------------------------------------------
# 2. Missing Mandatory Declarations (Full Coverage vs Incomplete Coverage)
# -----------------------------------------------------------------------------
def test_missing_declarations_full_coverage(real_engine):
    extraction = ExtractionPayload(
        product_name=ExtractedField(value="Atta", raw_text="Atta", confidence=0.9),
        image_coverage=ImageCoverage(front=True, back=True),
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    # Full coverage means declarations should have been visible -> POTENTIAL_VIOLATION
    assert rules_map["REQ-MVP-01"].status == ResultState.POTENTIAL_VIOLATION
    assert res.overall_status == ResultState.POTENTIAL_VIOLATION


def test_missing_declarations_partial_coverage(real_engine):
    extraction = ExtractionPayload(
        product_name=ExtractedField(value="Atta", raw_text="Atta", confidence=0.9),
        image_coverage=ImageCoverage(front=True, back=False),
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    # Partial coverage -> prompts inspector to scan remaining panels
    assert rules_map["REQ-MVP-01"].status == ResultState.NEEDS_MANUAL_REVIEW


# -----------------------------------------------------------------------------
# 3. Invalid MRP Layout (Missing "inclusive of all taxes")
# -----------------------------------------------------------------------------
def test_invalid_mrp_layout_missing_tax_phrase(real_engine):
    extraction = ExtractionPayload(
        mrp=MRPExtraction(
            value=150.0,
            currency="₹",
            raw_text="MRP ₹ 150.00",
            confidence=0.95,
        )
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    assert rules_map["REQ-MVP-02"].status == ResultState.POTENTIAL_VIOLATION
    assert "lacks mandatory tax-inclusion phrase" in rules_map["REQ-MVP-02"].reason


# -----------------------------------------------------------------------------
# 4. Low-Confidence MRP -> Fallback to NEEDS_MANUAL_REVIEW (Fix 1)
# -----------------------------------------------------------------------------
def test_low_confidence_mrp_fallback(real_engine):
    extraction = ExtractionPayload(
        mrp=MRPExtraction(
            value=99.0,
            raw_text="incl of taxes ₹99",
            confidence=0.71,  # < 0.75 threshold
        )
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    assert rules_map["REQ-MVP-02"].status == ResultState.NEEDS_MANUAL_REVIEW
    assert "confidence is below 0.75 threshold" in rules_map["REQ-MVP-02"].reason


# -----------------------------------------------------------------------------
# 5. Valid SI Metric Units
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("unit", ["g", "kg", "ml", "l", "N", "U", "cm", "m"])
def test_valid_metric_units(real_engine, unit):
    extraction = ExtractionPayload(
        net_quantity=NetQuantityExtraction(
            value=500.0 if unit != "kg" else 1.5,
            unit=unit,
            raw_text=f"Net Qty: 500 {unit}",
            confidence=0.95,
        )
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}
    assert rules_map["REQ-MVP-03"].status == ResultState.COMPLIANT


# -----------------------------------------------------------------------------
# 6. Invalid Metric Units (Prohibited colloquial units)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("prohibited", ["gms", "g.m.s", "nos.", "pcs", "dozen", "gross"])
def test_prohibited_metric_units(real_engine, prohibited):
    extraction = ExtractionPayload(
        net_quantity=NetQuantityExtraction(
            value=500.0,
            unit=prohibited,
            raw_text=f"Net Qty: 500 {prohibited}",
            confidence=0.95,
        )
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}
    assert rules_map["REQ-MVP-03"].status == ResultState.POTENTIAL_VIOLATION
    assert "Prohibited unit symbol" in rules_map["REQ-MVP-03"].reason


# -----------------------------------------------------------------------------
# 7. Quantity below 1 kg using kg incorrectly
# -----------------------------------------------------------------------------
def test_quantity_below_1kg_in_kg(real_engine):
    extraction = ExtractionPayload(
        net_quantity=NetQuantityExtraction(
            value=0.5,
            unit="kg",
            raw_text="Net Qty: 0.5 kg",
            confidence=0.95,
        )
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    assert rules_map["REQ-MVP-04"].status == ResultState.POTENTIAL_VIOLATION
    assert "0.5 kg" in rules_map["REQ-MVP-04"].reason
    assert "must be expressed in grams" in rules_map["REQ-MVP-04"].reason


# -----------------------------------------------------------------------------
# 8. Quantity below 1 L using L incorrectly
# -----------------------------------------------------------------------------
def test_quantity_below_1l_in_l(real_engine):
    extraction = ExtractionPayload(
        net_quantity=NetQuantityExtraction(
            value=0.75,
            unit="L",
            raw_text="Net Vol: 0.75 L",
            confidence=0.95,
        )
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    assert rules_map["REQ-MVP-04"].status == ResultState.POTENTIAL_VIOLATION
    assert "must be expressed in millilitres" in rules_map["REQ-MVP-04"].reason


# -----------------------------------------------------------------------------
# 9. Exactly 1 kg / 1 L boundary behaviour (Proviso)
# -----------------------------------------------------------------------------
def test_exact_1kg_1000g_proviso(real_engine):
    # 1000 g is legally allowed for 1 kg package
    ext_1000g = ExtractionPayload(
        net_quantity=NetQuantityExtraction(value=1000.0, unit="g", raw_text="Net Wt: 1000 g", confidence=0.95)
    )
    res_1000g = real_engine.evaluate(ext_1000g)
    rules_map = {r.rule_id: r for r in res_1000g.rule_results}
    assert rules_map["REQ-MVP-04"].status == ResultState.COMPLIANT

    # 1 kg is also valid
    ext_1kg = ExtractionPayload(
        net_quantity=NetQuantityExtraction(value=1.0, unit="kg", raw_text="Net Wt: 1 kg", confidence=0.95)
    )
    res_1kg = real_engine.evaluate(ext_1kg)
    rules_map_1kg = {r.rule_id: r for r in res_1kg.rule_results}
    assert rules_map_1kg["REQ-MVP-04"].status == ResultState.COMPLIANT


# -----------------------------------------------------------------------------
# 10. Prohibited Quantity Qualifiers
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("qualifier", ["approx", "approximately", "minimum", "average", "about"])
def test_prohibited_quantity_qualifiers(real_engine, qualifier):
    extraction = ExtractionPayload(
        net_quantity=NetQuantityExtraction(
            value=500.0,
            unit="g",
            raw_text=f"Net Weight: {qualifier} 500 g",
            confidence=0.95,
        )
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    assert rules_map["REQ-MVP-05"].status == ResultState.POTENTIAL_VIOLATION
    assert "Prohibited qualitative words detected" in rules_map["REQ-MVP-05"].reason


# -----------------------------------------------------------------------------
# 11 & 12. Missing Consumer Care Phone / Email
# -----------------------------------------------------------------------------
def test_consumer_care_missing_email(real_engine):
    extraction = ExtractionPayload(
        consumer_care=ConsumerCareExtraction(
            phone="1800112233",
            email=None,
            raw_text="Customer Helpline: 1800112233",
            confidence=0.95,
        )
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    assert rules_map["REQ-MVP-07"].status == ResultState.POTENTIAL_VIOLATION
    assert "email address" in rules_map["REQ-MVP-07"].reason


def test_consumer_care_missing_phone(real_engine):
    extraction = ExtractionPayload(
        consumer_care=ConsumerCareExtraction(
            phone=None,
            email="care@brand.com",
            raw_text="Feedback email: care@brand.com",
            confidence=0.95,
        )
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    assert rules_map["REQ-MVP-07"].status == ResultState.POTENTIAL_VIOLATION
    assert "telephone number" in rules_map["REQ-MVP-07"].reason


# -----------------------------------------------------------------------------
# 13. Manufacturer Address without PIN Code
# -----------------------------------------------------------------------------
def test_address_missing_pin_code(real_engine):
    extraction = ExtractionPayload(
        manufacturer=AddressExtraction(
            premises="Plot 10 Industrial Estate",
            street="Main Road",
            city="Jaipur",
            state="Rajasthan",
            pin_code=None,
            raw_text="Plot 10 Industrial Estate, Main Road, Jaipur, Rajasthan",
            confidence=0.95,
        )
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    assert rules_map["REQ-MVP-08"].status == ResultState.POTENTIAL_VIOLATION
    assert "lacks a valid 6-digit Indian Postal Index Number" in rules_map["REQ-MVP-08"].reason


# -----------------------------------------------------------------------------
# 14 & 15. Foreign Importer PDP Address Match
# -----------------------------------------------------------------------------
def test_domestic_origin_not_applicable(real_engine):
    extraction = ExtractionPayload(
        country_of_origin=ExtractedField(raw_text="Made in India", confidence=0.99)
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    assert rules_map["REQ-MVP-09"].status == ResultState.NOT_APPLICABLE


def test_foreign_origin_missing_importer_on_pdp(real_engine):
    extraction = ExtractionPayload(
        country_of_origin=ExtractedField(raw_text="Made in Germany", confidence=0.99),
        importer=None,
        is_importer_on_pdp=False,
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    assert rules_map["REQ-MVP-09"].status == ResultState.POTENTIAL_VIOLATION


def test_foreign_origin_importer_present_on_pdp(real_engine):
    extraction = ExtractionPayload(
        country_of_origin=ExtractedField(raw_text="Made in Germany", confidence=0.99),
        importer=AddressExtraction(
            premises="India Importers Ltd",
            city="Mumbai",
            pin_code="400001",
            raw_text="Imported by: India Importers Ltd, Mumbai 400001",
            confidence=0.95,
        ),
        is_importer_on_pdp=True,
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    assert rules_map["REQ-MVP-09"].status == ResultState.COMPLIANT


# -----------------------------------------------------------------------------
# 16 & 17. Pan Masala Routing & Small Package Override
# -----------------------------------------------------------------------------
def test_pan_masala_standard_compliant(real_engine):
    extraction = ExtractionPayload(
        product_name=ExtractedField(value="Premium Pan Masala", raw_text="Pan Masala", confidence=0.98),
        commodity_category=ExtractedField(value="Pan Masala", raw_text="Pan Masala", confidence=0.99),
        manufacturer=AddressExtraction(raw_text="Mfg by PM Ltd, Kanpur 208001", pin_code="208001", confidence=0.95),
        net_quantity=NetQuantityExtraction(value=50.0, unit="g", raw_text="50g", confidence=0.95),
        mrp=MRPExtraction(value=100.0, raw_text="MRP ₹100 incl. of all taxes", confidence=0.95),
        date_of_manufacture=DateExtraction(month="01", year="2026", raw_text="01/2026", confidence=0.95),
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    assert rules_map["REQ-MVP-10"].status == ResultState.COMPLIANT


def test_small_pan_masala_cannot_claim_small_pack_exemption(real_engine):
    # Under-10g Pan Masala missing declarations must NOT be exempt under Rule 26(a)
    extraction = ExtractionPayload(
        product_name=ExtractedField(value="Mini Pan Masala", raw_text="Pan Masala", confidence=0.98),
        commodity_category=ExtractedField(value="Pan Masala", raw_text="Pan Masala", confidence=0.99),
        net_quantity=NetQuantityExtraction(value=4.0, unit="g", raw_text="4g", confidence=0.95),
        # missing manufacturer and date
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    # REQ-MVP-01 must NOT be NOT_APPLICABLE because Pan Masala is excluded from Rule 26(a)
    assert rules_map["REQ-MVP-01"].status != ResultState.NOT_APPLICABLE
    assert rules_map["REQ-MVP-10"].status == ResultState.POTENTIAL_VIOLATION


# -----------------------------------------------------------------------------
# 18, 19, 20. Medical Device Routing & Confirmation Gate (Fix 2)
# -----------------------------------------------------------------------------
def test_medical_device_pending_confirmation_gate(real_engine):
    extraction = ExtractionPayload(
        product_name=ExtractedField(value="Gauze Swab", raw_text="Gauze Swab", confidence=0.95),
        commodity_category=ExtractedField(value="Medical Device", raw_text="Medical Device", confidence=0.95),
        medical_device_markers=ExtractedField(raw_text="Mfg Lic No. MD-1234", confidence=0.95),
    )
    res = real_engine.evaluate(extraction, is_medical_device_confirmed=None)
    rules_map = {r.rule_id: r for r in res.rule_results}

    # Gate active -> NEEDS_MANUAL_REVIEW
    assert rules_map["REQ-MVP-11"].status == ResultState.NEEDS_MANUAL_REVIEW
    assert res.overall_status == ResultState.NEEDS_MANUAL_REVIEW


def test_medical_device_confirmed_by_inspector(real_engine):
    extraction = ExtractionPayload(
        product_name=ExtractedField(value="Gauze Swab", raw_text="Gauze Swab", confidence=0.95),
        commodity_category=ExtractedField(value="Medical Device", raw_text="Medical Device", confidence=0.95),
        medical_device_markers=ExtractedField(raw_text="Mfg Lic No. MD-1234", confidence=0.95),
    )
    res = real_engine.evaluate(extraction, is_medical_device_confirmed=True)
    rules_map = {r.rule_id: r for r in res.rule_results}

    # When confirmed: REQ-11 is NOT_APPLICABLE, and all standard PCR checks are suppressed -> NOT_APPLICABLE
    assert rules_map["REQ-MVP-11"].status == ResultState.NOT_APPLICABLE
    assert rules_map["REQ-MVP-01"].status == ResultState.NOT_APPLICABLE
    assert rules_map["REQ-MVP-02"].status == ResultState.NOT_APPLICABLE
    assert res.overall_status == ResultState.NOT_APPLICABLE


def test_medical_device_rejected_by_inspector(real_engine):
    extraction = ExtractionPayload(
        product_name=ExtractedField(value="Gauze Swab", raw_text="Gauze Swab", confidence=0.95),
        commodity_category=ExtractedField(value="Medical Device", raw_text="Medical Device", confidence=0.95),
        medical_device_markers=ExtractedField(raw_text="Mfg Lic No. MD-1234", confidence=0.95),
    )
    res = real_engine.evaluate(extraction, is_medical_device_confirmed=False)
    rules_map = {r.rule_id: r for r in res.rule_results}

    # Inspector rejected: PCR checks proceed
    assert rules_map["REQ-MVP-11"].status == ResultState.COMPLIANT


# -----------------------------------------------------------------------------
# 21 & 22. Non-Standard Pack Size (Second Schedule)
# -----------------------------------------------------------------------------
def test_second_schedule_non_standard_size_without_disclaimer(real_engine):
    extraction = ExtractionPayload(
        commodity_category=ExtractedField(value="Biscuit", raw_text="Biscuit", confidence=0.95),
        net_quantity=NetQuantityExtraction(value=62.0, unit="g", raw_text="62g", confidence=0.95),
        non_standard_size_disclaimer=None,
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    assert rules_map["REQ-MVP-12"].status == ResultState.POTENTIAL_VIOLATION
    assert "lacks the mandatory disclaimer" in rules_map["REQ-MVP-12"].reason


def test_second_schedule_non_standard_size_with_disclaimer(real_engine):
    extraction = ExtractionPayload(
        commodity_category=ExtractedField(value="Biscuit", raw_text="Biscuit", confidence=0.95),
        net_quantity=NetQuantityExtraction(value=62.0, unit="g", raw_text="62g", confidence=0.95),
        non_standard_size_disclaimer=ExtractedField(
            raw_text="Not a standard pack size under Legal Metrology Rules", confidence=0.95
        ),
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    assert rules_map["REQ-MVP-12"].status == ResultState.COMPLIANT


# -----------------------------------------------------------------------------
# 23 & 24. Individual Correction Stickers (Rule 6(3))
# -----------------------------------------------------------------------------
def test_permitted_downward_mrp_sticker(real_engine):
    extraction = ExtractionPayload(
        mrp=MRPExtraction(
            value=80.0,
            original_mrp=100.0,
            is_sticker=True,
            raw_text="MRP ₹80 incl. of all taxes",
            confidence=0.95,
        )
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    assert rules_map["REQ-MVP-13"].status == ResultState.COMPLIANT
    assert "downward revised lower mrp" in rules_map["REQ-MVP-13"].reason.lower()


def test_prohibited_upward_mrp_sticker(real_engine):
    extraction = ExtractionPayload(
        mrp=MRPExtraction(
            value=120.0,
            original_mrp=100.0,
            is_sticker=True,
            raw_text="MRP ₹120 incl. of all taxes",
            confidence=0.95,
        )
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    assert rules_map["REQ-MVP-13"].status == ResultState.POTENTIAL_VIOLATION


# -----------------------------------------------------------------------------
# 25. Visual Aid Rules Hard Constraints (REQ-MVP-14 and REQ-MVP-15)
# -----------------------------------------------------------------------------
def test_visual_aid_hard_constraints(real_engine):
    extraction = DEMO_PRODUCTS[0]["extraction"]
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    # REQ-14 and REQ-15 can NEVER produce COMPLIANT or POTENTIAL_VIOLATION
    assert rules_map["REQ-MVP-14"].status in (ResultState.NEEDS_MANUAL_REVIEW, ResultState.NOT_DETECTED)
    assert rules_map["REQ-MVP-15"].status in (ResultState.NEEDS_MANUAL_REVIEW, ResultState.NOT_DETECTED)
    assert rules_map["REQ-MVP-14"].status != ResultState.COMPLIANT
    assert rules_map["REQ-MVP-15"].status != ResultState.COMPLIANT
    assert rules_map["REQ-MVP-14"].status != ResultState.POTENTIAL_VIOLATION
    assert rules_map["REQ-MVP-15"].status != ResultState.POTENTIAL_VIOLATION


# -----------------------------------------------------------------------------
# 26. MRP Conflict Detection Across Surfaces
# -----------------------------------------------------------------------------
def test_mrp_conflict_across_surfaces(real_engine):
    extraction = ExtractionPayload(
        mrp_observations=[
            MRPExtraction(value=100.0, raw_text="₹100", confidence=0.9, surface_location="front", image_id="img1"),
            MRPExtraction(value=120.0, raw_text="₹120", confidence=0.92, surface_location="back", image_id="img2"),
        ]
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    req_02 = rules_map["REQ-MVP-02"]
    assert req_02.status == ResultState.NEEDS_MANUAL_REVIEW
    assert req_02.conflicts is not None
    assert req_02.conflicts.field == "mrp"
    assert len(req_02.conflicts.values_found) == 2


# -----------------------------------------------------------------------------
# 27. Net Quantity Conflict Detection Across Surfaces
# -----------------------------------------------------------------------------
def test_net_quantity_conflict_across_surfaces(real_engine):
    extraction = ExtractionPayload(
        net_quantity_observations=[
            NetQuantityExtraction(value=500.0, unit="g", raw_text="500g", confidence=0.9, surface_location="front"),
            NetQuantityExtraction(value=400.0, unit="g", raw_text="400g", confidence=0.88, surface_location="back"),
        ]
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    req_03 = rules_map["REQ-MVP-03"]
    assert req_03.status == ResultState.NEEDS_MANUAL_REVIEW
    assert req_03.conflicts is not None
    assert req_03.conflicts.field == "net_quantity"
    assert len(req_03.conflicts.values_found) == 2


# -----------------------------------------------------------------------------
# 28. Agreeing Multi-Observations Produce No False Conflict
# -----------------------------------------------------------------------------
def test_agreeing_multi_observations_no_conflict(real_engine):
    extraction = ExtractionPayload(
        mrp_observations=[
            MRPExtraction(value=100.0, raw_text="₹100 incl. of taxes", confidence=0.9, surface_location="front"),
            MRPExtraction(value=100.0, raw_text="₹100 incl. of taxes", confidence=0.95, surface_location="back"),
        ]
    )
    res = real_engine.evaluate(extraction)
    rules_map = {r.rule_id: r for r in res.rule_results}

    req_02 = rules_map["REQ-MVP-02"]
    assert req_02.status == ResultState.COMPLIANT
    assert req_02.conflicts is None


# -----------------------------------------------------------------------------
# 29. Rule Version Metadata Preservation for All 15 Rules
# -----------------------------------------------------------------------------
def test_rule_version_metadata_preservation(real_engine):
    extraction = DEMO_PRODUCTS[0]["extraction"]
    res = real_engine.evaluate(extraction)

    for rule in res.rule_results:
        expected = RULE_VERSION_METADATA_TABLE[rule.rule_id]
        assert rule.rule_version.source == expected.source
        assert rule.rule_version.clause == expected.clause
        assert rule.rule_version.gsr_number == expected.gsr_number
        assert rule.rule_version.verification_status == expected.verification_status
        assert rule.rule_version.last_verified == expected.last_verified


# -----------------------------------------------------------------------------
# 30. All 6 Result States Present Where Applicable
# -----------------------------------------------------------------------------
def test_all_six_result_states_represented(real_engine):
    # Collect all states produced across various evaluations
    observed_states = set()

    # COMPLIANT
    res1 = real_engine.evaluate(DEMO_PRODUCTS[0]["extraction"])
    for r in res1.rule_results:
        observed_states.add(r.status)

    # POTENTIAL_VIOLATION
    res2 = real_engine.evaluate(DEMO_PRODUCTS[1]["extraction"])
    for r in res2.rule_results:
        observed_states.add(r.status)

    # NEEDS_MANUAL_REVIEW
    res3 = real_engine.evaluate(
        ExtractionPayload(
            mrp=MRPExtraction(value=50.0, raw_text="₹50 incl. of taxes", confidence=0.6)
        )
    )
    for r in res3.rule_results:
        observed_states.add(r.status)

    # NOT_APPLICABLE
    res4 = real_engine.evaluate(
        ExtractionPayload(
            country_of_origin=ExtractedField(raw_text="India", confidence=0.99)
        )
    )
    for r in res4.rule_results:
        observed_states.add(r.status)

    # NOT_DETECTED
    res5 = real_engine.evaluate(ExtractionPayload())
    for r in res5.rule_results:
        observed_states.add(r.status)

    assert ResultState.COMPLIANT in observed_states
    assert ResultState.POTENTIAL_VIOLATION in observed_states
    assert ResultState.NEEDS_MANUAL_REVIEW in observed_states
    assert ResultState.NOT_APPLICABLE in observed_states
    assert ResultState.NOT_DETECTED in observed_states


# -----------------------------------------------------------------------------
# 31. Reconciliation / Regression Against Mock Engine
# -----------------------------------------------------------------------------
def test_reconciliation_against_mock_engine(real_engine, mock_engine):
    for i, p in enumerate(DEMO_PRODUCTS):
        ext = p["extraction"]
        real_res = real_engine.evaluate(ext)
        mock_res = mock_engine.evaluate(ext)

        # Compare rule outcomes for each of the 15 rules
        real_map = {r.rule_id: r.status for r in real_res.rule_results}
        mock_map = {r.rule_id: r.status for r in mock_res.rule_results}

        # For non-medical confirmed products, core rules should agree on standard demo products
        for rid in ["REQ-MVP-01", "REQ-MVP-02", "REQ-MVP-03", "REQ-MVP-04", "REQ-MVP-05", "REQ-MVP-06", "REQ-MVP-07", "REQ-MVP-08"]:
            assert real_map[rid] == mock_map[rid], f"Discrepancy on Product {i} for {rid}: Real={real_map[rid]}, Mock={mock_map[rid]}"
