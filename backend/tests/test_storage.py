import io

def test_upload_valid_image(client, temp_upload_dir):
    # 1. Create inspection
    create_res = client.post("/api/inspections", json={"product_name": "Image Test Product"})
    insp_id = create_res.json()["id"]

    # 2. Upload fake image
    fake_png = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01")
    files = {"file": ("front_panel.png", fake_png, "image/png")}
    data = {"image_type": "front_panel"}

    upload_res = client.post(f"/api/inspections/{insp_id}/image", files=files, data=data)
    assert upload_res.status_code == 201
    res_data = upload_res.json()
    assert res_data["evidence_id"] is not None
    assert res_data["inspection_id"] == insp_id
    assert res_data["file_name"].endswith(".png")
    assert "/api/images/" in res_data["file_url"]

    # 3. Retrieve evidence list
    evidence_res = client.get(f"/api/inspections/{insp_id}/evidence")
    assert evidence_res.status_code == 200
    ev_data = evidence_res.json()
    assert len(ev_data["images"]) == 1
    assert ev_data["images"][0]["file_name"] == res_data["file_name"]

    # 4. Fetch the served image
    file_name = res_data["file_name"]
    img_get = client.get(f"/api/images/{file_name}")
    assert img_get.status_code == 200

def test_upload_unsupported_file_extension(client, temp_upload_dir):
    create_res = client.post("/api/inspections", json={"product_name": "Bad File Item"})
    insp_id = create_res.json()["id"]

    fake_exe = io.BytesIO(b"MZ\x90\x00\x03\x00\x00\x00")
    files = {"file": ("malware.exe", fake_exe, "application/octet-stream")}
    res = client.post(f"/api/inspections/{insp_id}/image", files=files)
    assert res.status_code == 400
    assert "Unsupported file extension" in res.json()["detail"]

def test_path_traversal_prevention(client, temp_upload_dir):
    res = client.get("/api/images/..%2f..%2fsecret.txt")
    # Must be 400 or 404, never 200 or allow escaping upload directory
    assert res.status_code in (400, 404)
