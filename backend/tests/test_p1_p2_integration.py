import io
import pytest
from app.schemas.common import ResultState

def test_full_pipeline_compliant_product(client, temp_upload_dir):
    # 1. Create inspection
    create_res = client.post("/api/inspections", json={
        "product_name": "Digestive Wholewheat Biscuits",
        "brand_name": "NutriBake",
        "commodity_category": "Biscuits",
        "inspector_id": "insp_int_01",
        "image_coverage": {"front": True, "back": True, "side": False, "top": False},
    })
    insp_id = create_res.json()["id"]

    # 2. Upload front panel
    fake_front = io.BytesIO(b"front_img")
    client.post(
        f"/api/inspections/{insp_id}/image",
        files={"file": ("front.jpg", fake_front, "image/jpeg")},
        data={"image_type": "front"},
    )

    # 3. Upload back panel
    fake_back = io.BytesIO(b"back_img")
    client.post(
        f"/api/inspections/{insp_id}/image",
        files={"file": ("back.jpg", fake_back, "image/jpeg")},
        data={"image_type": "back"},
    )

    # 4. Submit P1 ExtractionPayload
    extraction_payload = {
        "inspection_id": insp_id,
        "product_name": {"value": "Wholewheat Biscuits", "raw_text": "Digestive Wholewheat Biscuits", "confidence": 0.98, "location": "front"},
        "commodity_category": {"value": "Biscuits", "raw_text": "Biscuits", "confidence": 0.99, "location": "front"},
        "country_of_origin": {"value": "India", "raw_text": "Made in India", "confidence": 0.99, "location": "back"},
        "manufacturer": {
            "premises": "Unit 2, Industrial Estate",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pin_code": "560100",
            "raw_text": "Mfg by NutriBake, Unit 2, Industrial Estate, Bengaluru, Karnataka - 560100",
            "confidence": 0.96,
        },
        "net_quantity": {
            "value": 250.0,
            "unit": "g",
            "raw_text": "Net Weight: 250 g",
            "confidence": 0.97,
            "surface_location": "front",
            "quiet_zone_clear": True,
        },
        "net_quantity_observations": [
            {
                "value": 250.0,
                "unit": "g",
                "raw_text": "Net Weight: 250 g",
                "confidence": 0.97,
                "surface_location": "front",
            }
        ],
        "mrp": {
            "value": 50.0,
            "currency": "₹",
            "tax_inclusivity": True,
            "raw_text": "MRP ₹ 50.00 incl. of all taxes",
            "confidence": 0.95,
            "surface_location": "back",
            "is_sticker": False,
        },
        "mrp_observations": [
            {
                "value": 50.0,
                "currency": "₹",
                "tax_inclusivity": True,
                "raw_text": "MRP ₹ 50.00 incl. of all taxes",
                "confidence": 0.95,
                "surface_location": "back",
            }
        ],
        "date_of_manufacture": {
            "month": "09",
            "year": "2026",
            "raw_text": "Mfg: 09/2026",
            "confidence": 0.95,
        },
        "consumer_care": {
            "phone": "1800223344",
            "email": "care@nutribake.in",
            "raw_text": "Customer Helpline: 1800223344, care@nutribake.in",
            "confidence": 0.94,
        },
        "image_coverage": {"front": True, "back": True, "side": False, "top": False},
    }
    sub_res = client.post(f"/api/inspections/{insp_id}/extraction", json=extraction_payload)
    assert sub_res.status_code == 200

    # 5. Run compliance analysis via P2 RealComplianceEngine
    comp_res = client.post(f"/api/inspections/{insp_id}/analyze")
    assert comp_res.status_code == 200
    comp_data = comp_res.json()

    assert comp_data["overall_status"] == "COMPLIANT"
    assert comp_data["engine_version"] == "p2-real-v1.0.0"
    assert len(comp_data["rule_results"]) == 15
    assert comp_data["summary_counts"]["compliant"] >= 8
    assert comp_data["summary_counts"]["potential_violations"] == 0

def test_incomplete_coverage_deescalates_missing_declarations(client):
    # Only front image uploaded (back is missing)
    create_res = client.post("/api/inspections", json={
        "product_name": "Incomplete Coverage Juice",
        "image_coverage": {"front": True, "back": False, "side": False, "top": False},
    })
    insp_id = create_res.json()["id"]

    # Extraction only has front details (no date or consumer care)
    extraction_payload = {
        "inspection_id": insp_id,
        "product_name": {"value": "Apple Juice", "raw_text": "Apple Juice 1L", "confidence": 0.95, "location": "front"},
        "net_quantity": {"value": 1.0, "unit": "L", "raw_text": "1 L", "confidence": 0.95, "surface_location": "front"},
        "image_coverage": {"front": True, "back": False, "side": False, "top": False},
    }
    client.post(f"/api/inspections/{insp_id}/extraction", json=extraction_payload)

    comp_res = client.post(f"/api/inspections/{insp_id}/analyze")
    assert comp_res.status_code == 200
    rules_map = {r["rule_id"]: r for r in comp_res.json()["rule_results"]}

    # Missing declarations on incomplete coverage must be NEEDS_MANUAL_REVIEW, NOT POTENTIAL_VIOLATION
    assert rules_map["REQ-MVP-01"]["status"] == "NEEDS_MANUAL_REVIEW"
    assert rules_map["REQ-MVP-06"]["status"] == "NEEDS_MANUAL_REVIEW"
    assert rules_map["REQ-MVP-07"]["status"] == "NEEDS_MANUAL_REVIEW"
    assert rules_map["REQ-MVP-08"]["status"] == "NEEDS_MANUAL_REVIEW"

def test_mrp_conflict_propagation(client):
    create_res = client.post("/api/inspections", json={"product_name": "MRP Conflict Audit"})
    insp_id = create_res.json()["id"]

    extraction_payload = {
        "inspection_id": insp_id,
        "product_name": {"value": "Coffee", "raw_text": "Coffee", "confidence": 0.9},
        "manufacturer": {"premises": "Factory", "raw_text": "Mfg by Coffee Co", "pin_code": "560001", "confidence": 0.9},
        "net_quantity": {"value": 100.0, "unit": "g", "raw_text": "100g", "confidence": 0.9},
        "date_of_manufacture": {"month": "01", "year": "2026", "raw_text": "01/2026", "confidence": 0.9},
        "mrp_observations": [
            {"value": 100.0, "currency": "₹", "tax_inclusivity": True, "raw_text": "MRP ₹100", "confidence": 0.95, "surface_location": "front", "image_id": "img_f"},
            {"value": 130.0, "currency": "₹", "tax_inclusivity": True, "raw_text": "MRP ₹130", "confidence": 0.95, "surface_location": "back", "image_id": "img_b"},
        ],
        "image_coverage": {"front": True, "back": True, "side": False, "top": False},
    }
    client.post(f"/api/inspections/{insp_id}/extraction", json=extraction_payload)

    comp_res = client.post(f"/api/inspections/{insp_id}/analyze")
    rules_map = {r["rule_id"]: r for r in comp_res.json()["rule_results"]}

    req_02 = rules_map["REQ-MVP-02"]
    assert req_02["status"] == "NEEDS_MANUAL_REVIEW"
    assert req_02["conflicts"] is not None
    assert req_02["conflicts"]["field"] == "mrp"
    assert len(req_02["conflicts"]["values_found"]) == 2

def test_net_quantity_conflict_propagation(client):
    create_res = client.post("/api/inspections", json={"product_name": "Quantity Conflict Audit"})
    insp_id = create_res.json()["id"]

    extraction_payload = {
        "inspection_id": insp_id,
        "product_name": {"value": "Chips", "raw_text": "Chips", "confidence": 0.9},
        "manufacturer": {"premises": "Factory", "raw_text": "Mfg by Chips Co", "pin_code": "560001", "confidence": 0.9},
        "mrp": {"value": 20.0, "tax_inclusivity": True, "raw_text": "MRP ₹20 incl taxes", "confidence": 0.95},
        "date_of_manufacture": {"month": "01", "year": "2026", "raw_text": "01/2026", "confidence": 0.9},
        "net_quantity_observations": [
            {"value": 200.0, "unit": "g", "raw_text": "Net Qty: 200g", "confidence": 0.95, "surface_location": "front"},
            {"value": 180.0, "unit": "g", "raw_text": "Net Qty: 180g", "confidence": 0.95, "surface_location": "back"},
        ],
        "image_coverage": {"front": True, "back": True, "side": False, "top": False},
    }
    client.post(f"/api/inspections/{insp_id}/extraction", json=extraction_payload)

    comp_res = client.post(f"/api/inspections/{insp_id}/analyze")
    rules_map = {r["rule_id"]: r for r in comp_res.json()["rule_results"]}

    req_03 = rules_map["REQ-MVP-03"]
    assert req_03["status"] == "NEEDS_MANUAL_REVIEW"
    assert req_03["conflicts"] is not None
    assert req_03["conflicts"]["field"] == "net_quantity"

def test_medical_device_three_state_confirmation_lifecycle(client):
    create_res = client.post("/api/inspections", json={"product_name": "Surgical Bandage"})
    insp_id = create_res.json()["id"]

    # Initial state: is_medical_device_confirmed is None
    insp = client.get(f"/api/inspections/{insp_id}").json()
    assert insp["is_medical_device_confirmed"] is None

    extraction_payload = {
        "inspection_id": insp_id,
        "product_name": {"value": "Surgical Bandage", "raw_text": "Surgical Bandage", "confidence": 0.95},
        "commodity_category": {"value": "Medical Device", "raw_text": "Medical Device", "confidence": 0.95},
        "medical_device_markers": {"value": "MD-456", "raw_text": "Mfg Lic MD-456", "confidence": 0.92},
        "image_coverage": {"front": True, "back": True, "side": False, "top": False},
    }
    client.post(f"/api/inspections/{insp_id}/extraction", json=extraction_payload)

    # Step 1: Initial analysis pending confirmation -> REQ-MVP-11 is NEEDS_MANUAL_REVIEW
    res1 = client.post(f"/api/inspections/{insp_id}/analyze").json()
    r11 = next(r for r in res1["rule_results"] if r["rule_id"] == "REQ-MVP-11")
    assert r11["status"] == "NEEDS_MANUAL_REVIEW"

    # Step 2: Confirm True -> standard PCR suppressed to NOT_APPLICABLE
    conf_res = client.post(
        f"/api/inspections/{insp_id}/medical-device-confirmation",
        json={"is_confirmed_medical_device": True},
    ).json()
    assert conf_res["overall_status"] == "NOT_APPLICABLE"

    # Check persisted on inspection
    insp_after_confirm = client.get(f"/api/inspections/{insp_id}").json()
    assert insp_after_confirm["is_medical_device_confirmed"] is True

    # Step 3: Reject False -> standard PCR rules applied
    rej_res = client.post(
        f"/api/inspections/{insp_id}/medical-device-confirmation",
        json={"is_confirmed_medical_device": False},
    ).json()
    assert rej_res["overall_status"] != "NOT_APPLICABLE"
    insp_after_reject = client.get(f"/api/inspections/{insp_id}").json()
    assert insp_after_reject["is_medical_device_confirmed"] is False

def test_pan_masala_routing_enforces_declarations(client):
    create_res = client.post("/api/inspections", json={"product_name": "Small Pan Masala"})
    insp_id = create_res.json()["id"]

    # Pan Masala under 10g missing declarations
    extraction_payload = {
        "inspection_id": insp_id,
        "product_name": {"value": "Pan Masala", "raw_text": "Pan Masala 4g", "confidence": 0.95},
        "commodity_category": {"value": "Pan Masala", "raw_text": "Pan Masala", "confidence": 0.95},
        "net_quantity": {"value": 4.0, "unit": "g", "raw_text": "4g", "confidence": 0.95},
        "image_coverage": {"front": True, "back": True, "side": False, "top": False},
    }
    client.post(f"/api/inspections/{insp_id}/extraction", json=extraction_payload)

    comp_res = client.post(f"/api/inspections/{insp_id}/analyze").json()
    r10 = next(r for r in comp_res["rule_results"] if r["rule_id"] == "REQ-MVP-10")
    # Rule 26 exemption cannot be claimed -> POTENTIAL_VIOLATION
    assert r10["status"] == "POTENTIAL_VIOLATION"
    assert "excluded from Rule 26" in r10["reason"]

def test_visual_rules_are_never_compliant_or_violation(client):
    create_res = client.post("/api/inspections", json={"product_name": "Visual Rules Test"})
    insp_id = create_res.json()["id"]

    extraction_payload = {
        "inspection_id": insp_id,
        "product_name": {"value": "Tea", "raw_text": "Tea", "confidence": 0.9},
        "mrp": {"value": 50.0, "currency": "₹", "tax_inclusivity": True, "raw_text": "MRP ₹50 incl taxes", "confidence": 0.9},
        "net_quantity": {"value": 100.0, "unit": "g", "raw_text": "100g", "confidence": 0.9, "quiet_zone_clear": True},
        "contrast_analysis": {"value": 4.5, "raw_text": "contrast ok", "confidence": 0.8},
        "image_coverage": {"front": True, "back": True, "side": False, "top": False},
    }
    client.post(f"/api/inspections/{insp_id}/extraction", json=extraction_payload)

    comp_res = client.post(f"/api/inspections/{insp_id}/analyze").json()
    rules_map = {r["rule_id"]: r for r in comp_res["rule_results"]}

    r14 = rules_map["REQ-MVP-14"]
    r15 = rules_map["REQ-MVP-15"]

    assert r14["status"] in ("NEEDS_MANUAL_REVIEW", "NOT_DETECTED")
    assert r15["status"] in ("NEEDS_MANUAL_REVIEW", "NOT_DETECTED")
    assert r14["status"] not in ("COMPLIANT", "POTENTIAL_VIOLATION")
    assert r15["status"] not in ("COMPLIANT", "POTENTIAL_VIOLATION")

def test_golden_case_b_statutory_violations(client):
    """
    Golden Case B: Product with statutory violations
    - Rule 2(m): Lacks mandatory tax inclusivity phrase
    - Rule 13(1): Uses prohibited unit symbol 'gms'
    - Rule 13(2): Scaling boundary violation ('0.5 kg' instead of '500 g')
    """
    create_res = client.post("/api/inspections", json={
        "product_name": "Basmati Rice 0.5kg Non-Compliant",
        "brand_name": "TestGrains",
        "commodity_category": "Rice",
        "inspector_id": "insp_golden_b",
        "image_coverage": {"front": True, "back": True, "side": False, "top": False},
    })
    insp_id = create_res.json()["id"]

    extraction_payload = {
        "inspection_id": insp_id,
        "product_name": {"value": "Basmati Rice", "raw_text": "Basmati Rice 0.5kg", "confidence": 0.95, "location": "front"},
        "commodity_category": {"value": "Rice", "raw_text": "Rice", "confidence": 0.95, "location": "front"},
        "country_of_origin": {"value": "India", "raw_text": "Made in India", "confidence": 0.95, "location": "back"},
        "manufacturer": {
            "premises": "Shed 1",
            "city": "Karnal",
            "state": "Haryana",
            "pin_code": "132001",
            "raw_text": "Packed by: Rice Mills, Karnal - 132001",
            "confidence": 0.92,
        },
        "net_quantity": {
            "value": 0.5,
            "unit": "kg",
            "raw_text": "Net Weight: 0.5 kg (500 gms)",
            "confidence": 0.95,
            "surface_location": "front",
        },
        "mrp": {
            "value": 75.0,
            "currency": "₹",
            "tax_inclusivity": False,
            "raw_text": "MRP ₹ 75.00",
            "confidence": 0.95,
            "surface_location": "back",
        },
        "date_of_manufacture": {"month": "09", "year": "2026", "raw_text": "09/2026", "confidence": 0.9},
        "consumer_care": {"phone": "1800119988", "email": "care@grains.in", "raw_text": "care@grains.in", "confidence": 0.9},
        "image_coverage": {"front": True, "back": True, "side": False, "top": False},
    }
    sub_res = client.post(f"/api/inspections/{insp_id}/extraction", json=extraction_payload)
    assert sub_res.status_code == 200

    comp_res = client.post(f"/api/inspections/{insp_id}/analyze")
    assert comp_res.status_code == 200
    comp_data = comp_res.json()

    assert comp_data["overall_status"] == "POTENTIAL_VIOLATION"
    assert comp_data["summary_counts"]["potential_violations"] >= 2

    rules_map = {r["rule_id"]: r for r in comp_data["rule_results"]}
    # REQ-MVP-02: Missing tax inclusivity phrase
    assert rules_map["REQ-MVP-02"]["status"] == "POTENTIAL_VIOLATION"
    # REQ-MVP-04: Unit-switching boundary violation (0.5 kg instead of grams)
    assert rules_map["REQ-MVP-04"]["status"] == "POTENTIAL_VIOLATION"

