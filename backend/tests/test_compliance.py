from seed.demo_data import DEMO_PRODUCTS

def test_full_analysis_workflow_product_a(client):
    # 1. Create inspection
    create_res = client.post("/api/inspections", json=DEMO_PRODUCTS[0]["inspection"].model_dump())
    insp_id = create_res.json()["id"]

    # 2. Submit extraction
    client.post(f"/api/inspections/{insp_id}/extraction", json=DEMO_PRODUCTS[0]["extraction"].model_dump())

    # 3. Analyze
    analyze_res = client.post(f"/api/inspections/{insp_id}/analyze")
    assert analyze_res.status_code == 200
    res_data = analyze_res.json()

    # Product A is fully compliant
    assert res_data["overall_status"] == "COMPLIANT"
    assert res_data["summary_counts"]["compliant"] >= 10
    assert res_data["summary_counts"]["potential_violations"] == 0
    assert len(res_data["rule_results"]) == 15

    # Check inspection status updated
    insp_res = client.get(f"/api/inspections/{insp_id}")
    assert insp_res.json()["status"] == "ANALYSIS_COMPLETE"
    assert insp_res.json()["compliance_status"] == "COMPLIANT"

    # 4. Get result via GET
    get_res = client.get(f"/api/inspections/{insp_id}/result")
    assert get_res.status_code == 200
    assert get_res.json()["overall_status"] == "COMPLIANT"

def test_product_b_missing_declarations(client):
    create_res = client.post("/api/inspections", json=DEMO_PRODUCTS[1]["inspection"].model_dump())
    insp_id = create_res.json()["id"]
    client.post(f"/api/inspections/{insp_id}/extraction", json=DEMO_PRODUCTS[1]["extraction"].model_dump())

    analyze_res = client.post(f"/api/inspections/{insp_id}/analyze")
    assert analyze_res.status_code == 200
    data = analyze_res.json()

    assert data["overall_status"] == "POTENTIAL_VIOLATION"
    rules_map = {r["rule_id"]: r for r in data["rule_results"]}

    # REQ-MVP-06 (Date) and REQ-MVP-07 (Consumer Care) must be POTENTIAL_VIOLATION
    assert rules_map["REQ-MVP-06"]["status"] == "POTENTIAL_VIOLATION"
    assert rules_map["REQ-MVP-07"]["status"] == "POTENTIAL_VIOLATION"

def test_product_c_unit_and_scale_violations(client):
    create_res = client.post("/api/inspections", json=DEMO_PRODUCTS[2]["inspection"].model_dump())
    insp_id = create_res.json()["id"]
    client.post(f"/api/inspections/{insp_id}/extraction", json=DEMO_PRODUCTS[2]["extraction"].model_dump())

    analyze_res = client.post(f"/api/inspections/{insp_id}/analyze")
    assert analyze_res.status_code == 200
    data = analyze_res.json()

    assert data["overall_status"] == "POTENTIAL_VIOLATION"
    rules_map = {r["rule_id"]: r for r in data["rule_results"]}

    # REQ-MVP-03: Prohibited 'gms' unit
    assert rules_map["REQ-MVP-03"]["status"] == "POTENTIAL_VIOLATION"
    # REQ-MVP-04: Decimal scaling < 1 kg in kg
    assert rules_map["REQ-MVP-04"]["status"] == "POTENTIAL_VIOLATION"

def test_product_d_quantity_qualifier_violation(client):
    create_res = client.post("/api/inspections", json=DEMO_PRODUCTS[3]["inspection"].model_dump())
    insp_id = create_res.json()["id"]
    client.post(f"/api/inspections/{insp_id}/extraction", json=DEMO_PRODUCTS[3]["extraction"].model_dump())

    analyze_res = client.post(f"/api/inspections/{insp_id}/analyze")
    assert analyze_res.status_code == 200
    data = analyze_res.json()

    assert data["overall_status"] == "POTENTIAL_VIOLATION"
    rules_map = {r["rule_id"]: r for r in data["rule_results"]}
    # REQ-MVP-05: Prohibited qualifier 'approx'
    assert rules_map["REQ-MVP-05"]["status"] == "POTENTIAL_VIOLATION"

def test_fix_1_mrp_low_confidence_fallback(client):
    # Test Fix 1: When price + tax phrase are present, but confidence < 0.75 -> fallback to NEEDS_MANUAL_REVIEW
    create_res = client.post("/api/inspections", json={"product_name": "Low Light Juice"})
    insp_id = create_res.json()["id"]

    extraction = {
        "mrp": {
            "value": 99.0,
            "raw_text": "incl of taxes ₹99",
            "confidence": 0.71,  # < 0.75 threshold
        }
    }
    client.post(f"/api/inspections/{insp_id}/extraction", json=extraction)
    analyze_res = client.post(f"/api/inspections/{insp_id}/analyze")
    assert analyze_res.status_code == 200
    data = analyze_res.json()
    rules_map = {r["rule_id"]: r for r in data["rule_results"]}

    assert rules_map["REQ-MVP-02"]["status"] == "NEEDS_MANUAL_REVIEW"
    assert "OCR confidence is below" in rules_map["REQ-MVP-02"]["reason"]

def test_fix_2_medical_device_confirmation_gate(client):
    # Test Fix 2: Medical Device detected triggers confirmation gate
    create_res = client.post("/api/inspections", json=DEMO_PRODUCTS[5]["inspection"].model_dump())
    insp_id = create_res.json()["id"]
    client.post(f"/api/inspections/{insp_id}/extraction", json=DEMO_PRODUCTS[5]["extraction"].model_dump())

    # First analysis: Gate requires manual review
    analyze_res = client.post(f"/api/inspections/{insp_id}/analyze")
    assert analyze_res.status_code == 200
    data = analyze_res.json()
    rules_map = {r["rule_id"]: r for r in data["rule_results"]}
    assert rules_map["REQ-MVP-11"]["status"] == "NEEDS_MANUAL_REVIEW"

    # Inspector confirms it IS a medical device
    confirm_res = client.post(
        f"/api/inspections/{insp_id}/medical-device-confirmation",
        json={"is_confirmed_medical_device": True},
    )
    assert confirm_res.status_code == 200
    confirmed_data = confirm_res.json()
    # When confirmed, routed out of PCR to Medical Device rules -> NOT_APPLICABLE
    assert confirmed_data["overall_status"] == "NOT_APPLICABLE"
    c_rules_map = {r["rule_id"]: r for r in confirmed_data["rule_results"]}
    assert c_rules_map["REQ-MVP-11"]["status"] == "NOT_APPLICABLE"

def test_visual_aid_constraint_req_14_and_15(client):
    create_res = client.post("/api/inspections", json=DEMO_PRODUCTS[0]["inspection"].model_dump())
    insp_id = create_res.json()["id"]
    client.post(f"/api/inspections/{insp_id}/extraction", json=DEMO_PRODUCTS[0]["extraction"].model_dump())

    analyze_res = client.post(f"/api/inspections/{insp_id}/analyze")
    data = analyze_res.json()
    rules_map = {r["rule_id"]: r for r in data["rule_results"]}

    # Must be NEEDS_MANUAL_REVIEW or NOT_DETECTED, NEVER COMPLIANT or POTENTIAL_VIOLATION
    assert rules_map["REQ-MVP-14"]["status"] in ("NEEDS_MANUAL_REVIEW", "NOT_DETECTED")
    assert rules_map["REQ-MVP-15"]["status"] in ("NEEDS_MANUAL_REVIEW", "NOT_DETECTED")
    assert rules_map["REQ-MVP-14"]["status"] != "COMPLIANT"
    assert rules_map["REQ-MVP-15"]["status"] != "COMPLIANT"
