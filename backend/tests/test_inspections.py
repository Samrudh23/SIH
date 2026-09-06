def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "sih26034-backend"

def test_create_and_get_inspection(client):
    # 1. Create
    payload = {
        "product_name": "Test Snack Pack",
        "brand_name": "SnackCo",
        "commodity_category": "Biscuits",
        "inspector_id": "insp_01",
        "image_coverage": {"front": True, "back": True, "side": False, "top": False},
        "metadata": {"test_run": True},
    }
    response = client.post("/api/inspections", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["id"] is not None
    assert created["status"] == "CREATED"
    assert created["compliance_status"] == "PENDING"
    assert created["product_name"] == "Test Snack Pack"
    assert created["image_coverage"]["front"] is True
    assert created["image_coverage"]["back"] is True

    inspection_id = created["id"]

    # 2. Get
    get_res = client.get(f"/api/inspections/{inspection_id}")
    assert get_res.status_code == 200
    fetched = get_res.json()
    assert fetched["id"] == inspection_id
    assert fetched["brand_name"] == "SnackCo"

def test_inspection_not_found(client):
    response = client.get("/api/inspections/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_update_inspection_notes(client):
    create_res = client.post("/api/inspections", json={"product_name": "Sample"})
    insp_id = create_res.json()["id"]

    notes_payload = {"notes": "Inspector verified label font size manually with optical loupe."}
    response = client.post(f"/api/inspections/{insp_id}/notes", json=notes_payload)
    assert response.status_code == 200
    assert response.json()["notes"] == notes_payload["notes"]

def test_list_inspections_with_filters(client):
    # Create 3 inspections
    client.post("/api/inspections", json={"product_name": "Parle Biscuits", "commodity_category": "Biscuits"})
    client.post("/api/inspections", json={"product_name": "Amul Milk", "commodity_category": "Dairy"})
    client.post("/api/inspections", json={"product_name": "Tata Salt", "commodity_category": "Salt"})

    # List all
    res = client.get("/api/inspections")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3

    # Filter by product query
    res_filtered = client.get("/api/inspections?product=Amul")
    assert res_filtered.status_code == 200
    assert res_filtered.json()["total"] == 1
    assert res_filtered.json()["items"][0]["product_name"] == "Amul Milk"
