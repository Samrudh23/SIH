import io
import pytest

def test_complete_frontend_lifecycle_workflow(client, temp_upload_dir):
    """
    Phase 9: Comprehensive 14-step real frontend workflow test.
    1. Create inspection.
    2. Upload front image.
    3. Upload back image.
    4. Assign surfaces.
    5. Run P1 extraction.
    6. Validate ExtractionPayload.
    7. Run P2 compliance.
    8. Retrieve ComplianceReport.
    9. Retrieve individual RuleResults.
    10. Trigger a manual-review case.
    11. Submit medical-device confirmation.
    12. Re-run/retrieve compliance result.
    13. Retrieve inspection history.
    14. Retrieve final report.
    """
    # 1. Create inspection
    create_res = client.post("/api/inspections", json={
        "product_name": "E2E Lifecycle Product",
        "brand_name": "BrandX",
        "commodity_category": "Packaged Commodity",
        "inspector_id": "officer_e2e_01",
        "image_coverage": {"front": False, "back": False, "side": False, "top": False},
        "metadata": {"batch": "BATCH-E2E-2026"},
    })
    assert create_res.status_code == 201
    insp_id = create_res.json()["id"]
    assert create_res.json()["status"] == "CREATED"
    assert create_res.json()["compliance_status"] == "PENDING"

    # 2. Upload front image
    fake_front = io.BytesIO(b"front-panel-bytes")
    up1 = client.post(
        f"/api/inspections/{insp_id}/images",
        files={"file": ("front_panel.jpg", fake_front, "image/jpeg")},
        data={"image_type": "front"},
    )
    assert up1.status_code == 201
    ev_front_id = up1.json()["evidence_id"]

    # 3. Upload back image
    fake_back = io.BytesIO(b"back-panel-bytes")
    up2 = client.post(
        f"/api/inspections/{insp_id}/images",
        files={"file": ("back_panel.jpg", fake_back, "image/jpeg")},
        data={"image_type": "back"},
    )
    assert up2.status_code == 201
    ev_back_id = up2.json()["evidence_id"]

    # 4. Assign / verify surfaces
    patch_surf = client.patch(
        f"/api/inspections/{insp_id}/images/{ev_front_id}/surface",
        json={"surface": "front"},
    )
    assert patch_surf.status_code == 200
    assert patch_surf.json()["image_type"] == "front"

    insp_status = client.get(f"/api/inspections/{insp_id}").json()
    assert insp_status["image_coverage"]["front"] is True
    assert insp_status["image_coverage"]["back"] is True
    assert insp_status["status"] == "IMAGE_UPLOADED"

    # 5. Run P1 extraction
    # Since fake bytes have no real text, submit realistic extraction payload representing P1 output
    extraction_payload = {
        "inspection_id": insp_id,
        "product_name": {"value": "Organic Roasted Almonds", "raw_text": "Organic Roasted Almonds 200g", "confidence": 0.98, "location": "front"},
        "commodity_category": {"value": "Edible Nuts", "raw_text": "Edible Nuts", "confidence": 0.95, "location": "front"},
        "country_of_origin": {"value": "India", "raw_text": "Country of Origin: India", "confidence": 0.99, "location": "back"},
        "manufacturer": {
            "premises": "Plot 5, Food Park",
            "city": "Pune",
            "state": "Maharashtra",
            "pin_code": "411028",
            "raw_text": "Mfg by: NutCo Pvt Ltd, Plot 5, Food Park, Pune, Maharashtra - 411028",
            "confidence": 0.96,
        },
        "net_quantity": {
            "value": 200.0,
            "unit": "g",
            "raw_text": "Net Weight: 200 g",
            "confidence": 0.97,
            "surface_location": "front",
            "quiet_zone_clear": True,
        },
        "net_quantity_observations": [
            {"value": 200.0, "unit": "g", "raw_text": "Net Weight: 200 g", "confidence": 0.97, "surface_location": "front"}
        ],
        "mrp": {
            "value": 250.0,
            "currency": "₹",
            "tax_inclusivity": True,
            "raw_text": "MRP ₹ 250.00 incl. of all taxes",
            "confidence": 0.95,
            "surface_location": "back",
            "is_sticker": False,
        },
        "mrp_observations": [
            {"value": 250.0, "currency": "₹", "tax_inclusivity": True, "raw_text": "MRP ₹ 250.00 incl. of all taxes", "confidence": 0.95, "surface_location": "back"}
        ],
        "date_of_manufacture": {"month": "09", "year": "2026", "raw_text": "Pkd: 09/2026", "confidence": 0.95},
        "consumer_care": {"phone": "1800223399", "email": "help@nutco.in", "raw_text": "Care: 1800223399, help@nutco.in", "confidence": 0.94},
        "image_coverage": {"front": True, "back": True, "side": False, "top": False},
    }
    submit_res = client.post(f"/api/inspections/{insp_id}/extraction", json=extraction_payload)
    assert submit_res.status_code == 200

    # 6. Validate ExtractionPayload stored correctly
    stored_ext = client.get(f"/api/inspections/{insp_id}/extraction")
    assert stored_ext.status_code == 200
    assert stored_ext.json()["product_name"]["value"] == "Organic Roasted Almonds"
    assert stored_ext.json()["mrp"]["value"] == 250.0

    # 7. Run P2 compliance evaluation
    comp_res = client.post(f"/api/inspections/{insp_id}/analyze")
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["overall_status"] == "COMPLIANT"

    # 8. Retrieve ComplianceReport
    rep_res = client.get(f"/api/reports/{insp_id}")
    assert rep_res.status_code == 200
    assert rep_res.json()["compliance_evaluation"]["overall_status"] == "COMPLIANT"
    assert len(rep_res.json()["compliance_evaluation"]["findings"]) == 15

    # 9. Retrieve individual RuleResults
    r1 = client.get(f"/api/inspections/{insp_id}/rules/REQ-MVP-01")
    assert r1.status_code == 200
    assert r1.json()["status"] == "COMPLIANT"

    r2 = client.get(f"/api/inspections/{insp_id}/rules/REQ-MVP-02")
    assert r2.status_code == 200
    assert r2.json()["status"] == "COMPLIANT"

    # 10. Trigger a manual-review case on medical device
    med_create = client.post("/api/inspections", json={"product_name": "Surgical Swab"})
    med_id = med_create.json()["id"]
    client.post(f"/api/inspections/{med_id}/extraction", json={
        "inspection_id": med_id,
        "product_name": {"value": "Surgical Swab", "raw_text": "Surgical Swab", "confidence": 0.95},
        "commodity_category": {"value": "Medical Device", "raw_text": "Medical Device", "confidence": 0.95},
        "medical_device_markers": {"value": "CDSCO MD-99", "raw_text": "Mfg Lic CDSCO MD-99", "confidence": 0.92},
        "image_coverage": {"front": True, "back": True, "side": False, "top": False},
    })
    med_comp = client.post(f"/api/inspections/{med_id}/analyze").json()
    r11_init = next(r for r in med_comp["rule_results"] if r["rule_id"] == "REQ-MVP-11")
    assert r11_init["status"] == "NEEDS_MANUAL_REVIEW"

    # Check manual review endpoint returns it
    man_rev = client.get(f"/api/inspections/{med_id}/manual-review").json()
    assert man_rev["manual_review_count"] >= 1

    # 11. Submit medical-device confirmation (Confirmed True)
    med_confirm = client.post(
        f"/api/inspections/{med_id}/medical-device-confirmation",
        json={"is_confirmed_medical_device": True},
    )
    assert med_confirm.status_code == 200
    assert med_confirm.json()["overall_status"] == "NOT_APPLICABLE"

    # 12. Re-run / retrieve compliance result
    med_retrieved = client.get(f"/api/inspections/{med_id}/result").json()
    assert med_retrieved["overall_status"] == "NOT_APPLICABLE"

    # 13. Retrieve inspection history
    list_res = client.get("/api/inspections?limit=10")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 2

    # 14. Retrieve final HTML report
    html_res = client.get(f"/api/reports/{insp_id}/html")
    assert html_res.status_code == 200
    assert "<!DOCTYPE html>" in html_res.text
    assert "LEGAL METROLOGY" in html_res.text

def test_error_states_and_technical_failures(client):
    # 404 for nonexistent inspection
    res404 = client.get("/api/inspections/nonexistent-12345")
    assert res404.status_code == 404

    # 400 when analyzing inspection with no extraction or images
    empty_insp = client.post("/api/inspections", json={"product_name": "Empty Test"}).json()
    res400 = client.post(f"/api/inspections/{empty_insp['id']}/analyze")
    assert res400.status_code == 400

    # 422 for malformed extraction confidence > 1.0
    res422 = client.post(
        f"/api/inspections/{empty_insp['id']}/extraction",
        json={"mrp": {"raw_text": "MRP 100", "confidence": 1.5}},
    )
    assert res422.status_code == 422

    # 404 for nonexistent rule
    insp = client.post("/api/inspections", json={"product_name": "Rule 404 Test"}).json()
    client.post(f"/api/inspections/{insp['id']}/extraction", json={
        "product_name": {"value": "P", "raw_text": "P", "confidence": 0.9},
        "mrp": {"value": 10.0, "raw_text": "MRP 10", "confidence": 0.9},
        "image_coverage": {"front": True, "back": True, "side": False, "top": False},
    })
    client.post(f"/api/inspections/{insp['id']}/analyze")
    r404 = client.get(f"/api/inspections/{insp['id']}/rules/NONEXISTENT_RULE")
    assert r404.status_code == 404
