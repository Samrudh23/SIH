import io
import pytest
from seed.demo_data import DEMO_PRODUCTS

def test_image_upload_and_plural_alias(client, temp_upload_dir):
    # 1. Create inspection
    create_res = client.post("/api/inspections", json={"product_name": "Plural Route Test Product"})
    assert create_res.status_code == 201
    insp_id = create_res.json()["id"]

    # 2. Upload image via /image
    fake_img = io.BytesIO(b"fake jpeg data")
    res1 = client.post(
        f"/api/inspections/{insp_id}/image",
        files={"file": ("front.jpg", fake_img, "image/jpeg")},
        data={"image_type": "front"},
    )
    assert res1.status_code == 201
    ev1 = res1.json()
    assert ev1["image_type"] == "front"

    # 3. Upload image via /images (plural alias)
    fake_img2 = io.BytesIO(b"fake jpeg data back")
    res2 = client.post(
        f"/api/inspections/{insp_id}/images",
        files={"file": ("back.jpg", fake_img2, "image/jpeg")},
        data={"image_type": "back"},
    )
    assert res2.status_code == 201
    ev2 = res2.json()
    assert ev2["image_type"] == "back"

    # 4. Fetch evidence via /evidence and /images
    ev_res = client.get(f"/api/inspections/{insp_id}/evidence")
    assert ev_res.status_code == 200
    assert len(ev_res.json()["images"]) == 2

    images_res = client.get(f"/api/inspections/{insp_id}/images")
    assert images_res.status_code == 200
    assert len(images_res.json()["images"]) == 2

    # Check that coverage was automatically updated
    insp_check = client.get(f"/api/inspections/{insp_id}").json()
    assert insp_check["image_coverage"]["front"] is True
    assert insp_check["image_coverage"]["back"] is True

def test_surface_assignment_endpoints(client, temp_upload_dir):
    create_res = client.post("/api/inspections", json={"product_name": "Surface Assignment Test"})
    insp_id = create_res.json()["id"]

    fake_img = io.BytesIO(b"sample bytes")
    res = client.post(
        f"/api/inspections/{insp_id}/image",
        files={"file": ("side_panel.jpg", fake_img, "image/jpeg")},
        data={"image_type": "package_image"},
    )
    ev_id = res.json()["evidence_id"]

    # Reassign surface to 'side' via PATCH
    patch_res = client.patch(
        f"/api/inspections/{insp_id}/images/{ev_id}/surface",
        json={"surface": "side"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["image_type"] == "side"

    # Check inspection coverage auto-updated
    insp_res = client.get(f"/api/inspections/{insp_id}").json()
    assert insp_res["image_coverage"]["side"] is True

    # Reassign surface via POST alias
    post_res = client.post(
        f"/api/inspections/{insp_id}/images/{ev_id}/surface",
        json={"surface": "top"},
    )
    assert post_res.status_code == 200
    assert post_res.json()["image_type"] == "top"

def test_coverage_update_endpoint(client):
    create_res = client.post("/api/inspections", json={"product_name": "Coverage Test"})
    insp_id = create_res.json()["id"]

    put_res = client.put(
        f"/api/inspections/{insp_id}/coverage",
        json={"coverage": {"front": True, "back": True, "side": True, "top": False}},
    )
    assert put_res.status_code == 200
    assert put_res.json()["image_coverage"]["side"] is True
    assert put_res.json()["image_coverage"]["top"] is False

def test_extract_endpoint_execution(client, temp_upload_dir):
    create_res = client.post("/api/inspections", json={"product_name": "Extract Pipeline Test"})
    insp_id = create_res.json()["id"]

    # Upload mock image
    fake_img = io.BytesIO(b"dummy image bytes")
    client.post(
        f"/api/inspections/{insp_id}/image",
        files={"file": ("label.jpg", fake_img, "image/jpeg")},
        data={"image_type": "front"},
    )

    # Trigger extraction execution
    extract_res = client.post(f"/api/inspections/{insp_id}/extract")
    assert extract_res.status_code == 200
    ext_data = extract_res.json()
    assert ext_data["status"] == "success"
    assert ext_data["inspection_id"] == insp_id
    assert "extraction_id" in ext_data

    # Verify retrieval
    stored_ext = client.get(f"/api/inspections/{insp_id}/extraction")
    assert stored_ext.status_code == 200

def test_single_rule_result_retrieval(client):
    # Seed inspection and run analysis
    create_res = client.post("/api/inspections", json=DEMO_PRODUCTS[0]["inspection"].model_dump())
    insp_id = create_res.json()["id"]
    client.post(f"/api/inspections/{insp_id}/extraction", json=DEMO_PRODUCTS[0]["extraction"].model_dump())
    client.post(f"/api/inspections/{insp_id}/analyze")

    # Fetch specific rule REQ-MVP-01
    rule_res = client.get(f"/api/inspections/{insp_id}/rules/REQ-MVP-01")
    assert rule_res.status_code == 200
    assert rule_res.json()["rule_id"] == "REQ-MVP-01"
    assert rule_res.json()["status"] == "COMPLIANT"

    # Fetch via alias /result/rules/REQ-MVP-02
    alias_res = client.get(f"/api/inspections/{insp_id}/result/rules/REQ-MVP-02")
    assert alias_res.status_code == 200
    assert alias_res.json()["rule_id"] == "REQ-MVP-02"

    # Fetch nonexistent rule -> 404
    bad_rule = client.get(f"/api/inspections/{insp_id}/rules/REQ-NONEXISTENT")
    assert bad_rule.status_code == 404

def test_manual_review_endpoint(client):
    # Demo product 5 has medical device marker -> triggers NEEDS_MANUAL_REVIEW on REQ-MVP-11
    create_res = client.post("/api/inspections", json=DEMO_PRODUCTS[5]["inspection"].model_dump())
    insp_id = create_res.json()["id"]
    client.post(f"/api/inspections/{insp_id}/extraction", json=DEMO_PRODUCTS[5]["extraction"].model_dump())
    client.post(f"/api/inspections/{insp_id}/analyze")

    # Fetch manual review items
    rev_res = client.get(f"/api/inspections/{insp_id}/manual-review")
    assert rev_res.status_code == 200
    rev_data = rev_res.json()
    assert rev_data["manual_review_count"] >= 1
    unresolved_ids = [r["rule_id"] for r in rev_data["unresolved_rules"]]
    assert "REQ-MVP-11" in unresolved_ids

    # Check alias /review
    alias_res = client.get(f"/api/inspections/{insp_id}/review")
    assert alias_res.status_code == 200

def test_report_aliases_on_inspections_path(client):
    create_res = client.post("/api/inspections", json=DEMO_PRODUCTS[0]["inspection"].model_dump())
    insp_id = create_res.json()["id"]
    client.post(f"/api/inspections/{insp_id}/extraction", json=DEMO_PRODUCTS[0]["extraction"].model_dump())
    client.post(f"/api/inspections/{insp_id}/analyze")

    # JSON report alias
    rep_res = client.get(f"/api/inspections/{insp_id}/report")
    assert rep_res.status_code == 200
    assert rep_res.json()["inspection"]["id"] == insp_id

    # HTML report alias
    html_res = client.get(f"/api/inspections/{insp_id}/report/html")
    assert html_res.status_code == 200
    assert "<!DOCTYPE html>" in html_res.text
