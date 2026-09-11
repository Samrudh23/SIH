from seed.demo_data import DEMO_PRODUCTS

def test_dashboard_summary_calculation(client):
    # Check initial empty summary
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_inspections"] == 0

    # Add Product A (Compliant)
    r1 = client.post("/api/inspections", json=DEMO_PRODUCTS[0]["inspection"].model_dump())
    id1 = r1.json()["id"]
    client.post(f"/api/inspections/{id1}/extraction", json=DEMO_PRODUCTS[0]["extraction"].model_dump())
    client.post(f"/api/inspections/{id1}/analyze")

    # Add Product B (Violation)
    r2 = client.post("/api/inspections", json=DEMO_PRODUCTS[1]["inspection"].model_dump())
    id2 = r2.json()["id"]
    client.post(f"/api/inspections/{id2}/extraction", json=DEMO_PRODUCTS[1]["extraction"].model_dump())
    client.post(f"/api/inspections/{id2}/analyze")

    # Add Product E2 (Needs Review)
    r3 = client.post("/api/inspections", json=DEMO_PRODUCTS[5]["inspection"].model_dump())
    id3 = r3.json()["id"]
    client.post(f"/api/inspections/{id3}/extraction", json=DEMO_PRODUCTS[5]["extraction"].model_dump())
    client.post(f"/api/inspections/{id3}/analyze")

    # Check updated dashboard metrics
    res_updated = client.get("/api/dashboard/summary")
    assert res_updated.status_code == 200
    metrics = res_updated.json()

    assert metrics["total_inspections"] == 3
    assert metrics["compliant_inspections"] == 1
    assert metrics["potential_violations"] == 1
    assert metrics["needs_manual_review"] == 1
    assert len(metrics["recent_inspections"]) == 3

def test_report_generation_json_and_html(client):
    r1 = client.post("/api/inspections", json=DEMO_PRODUCTS[0]["inspection"].model_dump())
    id1 = r1.json()["id"]
    client.post(f"/api/inspections/{id1}/extraction", json=DEMO_PRODUCTS[0]["extraction"].model_dump())
    client.post(f"/api/inspections/{id1}/analyze")

    # 1. JSON report
    res_json = client.get(f"/api/reports/{id1}")
    assert res_json.status_code == 200
    report = res_json.json()
    assert report["title"] == "LEGAL METROLOGY (PACKAGED COMMODITIES) SCREENING REPORT"
    assert "LEGAL DISCLAIMER" in report["disclaimer"]
    assert report["inspection"]["id"] == id1

    # 2. HTML report
    res_html = client.get(f"/api/reports/{id1}/html")
    assert res_html.status_code == 200
    assert "text/html" in res_html.headers["content-type"]
    assert "<title>Compliance Report" in res_html.text
    assert "LEGAL DISCLAIMER" in res_html.text
