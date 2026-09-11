from seed.demo_data import DEMO_PRODUCTS

def test_submit_valid_extraction(client):
    # 1. Create inspection
    create_res = client.post("/api/inspections", json={"product_name": "Test Item"})
    insp_id = create_res.json()["id"]

    # 2. Submit valid extraction payload from demo data
    extraction_data = DEMO_PRODUCTS[0]["extraction"].model_dump()
    response = client.post(f"/api/inspections/{insp_id}/extraction", json=extraction_data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # 3. Retrieve stored extraction
    get_res = client.get(f"/api/inspections/{insp_id}/extraction")
    assert get_res.status_code == 200
    stored = get_res.json()
    assert stored["product_name"]["value"] == "Glucose Biscuits"
    assert stored["net_quantity"]["value"] == 100.0
    assert stored["mrp"]["value"] == 30.00
    # Verify exact confidence values are preserved as floats
    assert stored["mrp"]["confidence"] == 0.96

def test_reject_malformed_extraction_confidence_out_of_bounds(client):
    create_res = client.post("/api/inspections", json={"product_name": "Test Item"})
    insp_id = create_res.json()["id"]

    # Confidence must be between 0.0 and 1.0
    bad_payload = {
        "mrp": {
            "value": 100.0,
            "raw_text": "MRP 100",
            "confidence": 1.5,  # Illegal!
        }
    }
    response = client.post(f"/api/inspections/{insp_id}/extraction", json=bad_payload)
    assert response.status_code == 422
    err_body = response.json()
    assert err_body["detail"] == "Extraction Schema Validation Failure"
    assert any("mrp -> confidence" in e["field"] for e in err_body["errors"])

def test_reject_negative_confidence(client):
    create_res = client.post("/api/inspections", json={"product_name": "Test Item"})
    insp_id = create_res.json()["id"]

    bad_payload = {
        "net_quantity": {
            "value": 500.0,
            "raw_text": "500g",
            "confidence": -0.1,  # Illegal!
        }
    }
    response = client.post(f"/api/inspections/{insp_id}/extraction", json=bad_payload)
    assert response.status_code == 422

def test_reject_missing_required_raw_text(client):
    create_res = client.post("/api/inspections", json={"product_name": "Test Item"})
    insp_id = create_res.json()["id"]

    bad_payload = {
        "mrp": {
            "value": 50.0,
            "confidence": 0.9,
            # missing raw_text!
        }
    }
    response = client.post(f"/api/inspections/{insp_id}/extraction", json=bad_payload)
    assert response.status_code == 422


def test_submit_multi_observation_extraction(client):
    create_res = client.post("/api/inspections", json={"product_name": "Multi Observation Biscuit"})
    insp_id = create_res.json()["id"]

    payload = {
        "mrp_observations": [
            {
                "value": 100.0,
                "raw_text": "MRP ₹ 100.00 incl. of all taxes",
                "confidence": 0.85,
                "surface_location": "front",
                "image_id": "img_001",
            },
            {
                "value": 120.0,
                "raw_text": "MRP ₹ 120.00 incl. of all taxes",
                "confidence": 0.95,
                "surface_location": "back",
                "image_id": "img_002",
            },
        ],
        "net_quantity_observations": [
            {
                "value": 500.0,
                "unit": "g",
                "raw_text": "Net Qty: 500g",
                "confidence": 0.92,
                "surface_location": "front",
                "image_id": "img_001",
            }
        ],
    }
    res = client.post(f"/api/inspections/{insp_id}/extraction", json=payload)
    assert res.status_code == 200

    stored = client.get(f"/api/inspections/{insp_id}/extraction").json()
    assert len(stored["mrp_observations"]) == 2
    assert stored["mrp_observations"][0]["value"] == 100.0
    assert stored["mrp_observations"][0]["surface_location"] == "front"
    assert stored["mrp_observations"][1]["value"] == 120.0
    assert stored["mrp_observations"][1]["surface_location"] == "back"
    # Backwards-compatible convenience accessor selects highest confidence (0.95 -> 120.0)
    assert stored["mrp"]["value"] == 120.0
    assert stored["mrp"]["confidence"] == 0.95

    assert len(stored["net_quantity_observations"]) == 1
    assert stored["net_quantity"]["value"] == 500.0
