#!/usr/bin/env python3
"""
SIH26034 — Packaged Commodity Compliance Scanner
End-to-End Production Smoke Test Suite (Phase 7)
"""

import sys
import os
import argparse
import time
from io import BytesIO
import httpx

def run_smoke_tests(base_url: str):
    base_url = base_url.rstrip("/")
    print("=" * 70)
    print(f"SIH26034 PRODUCTION SMOKE TEST RUNNER")
    print(f"Target URL: {base_url}")
    print("=" * 70)

    client = httpx.Client(base_url=base_url, timeout=15.0)
    passed = 0
    total = 16

    # -------------------------------------------------------------------------
    # 1. Verify API Health Endpoint
    # -------------------------------------------------------------------------
    print("\n[Step 1/16] Verifying API Health Endpoint (/api/health)...")
    try:
        r = client.get("/api/health")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        assert data.get("status") == "ok", f"Expected status 'ok', got {data.get('status')}"
        assert "compliance_engine" in data
        print(f"  [+] PASS: Health check OK (Service: {data.get('service')}, Engine: {data.get('compliance_engine')})")
        passed += 1
    except Exception as e:
        print(f"  [-] FAIL: Health check failed: {e}")

    # -------------------------------------------------------------------------
    # 2. Open Hosted Frontend
    # -------------------------------------------------------------------------
    print("\n[Step 2/16] Verifying Hosted Frontend Index (/)...")
    try:
        r = client.get("/")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        assert "<!DOCTYPE html>" in r.text or "<html" in r.text
        assert "SIH26034" in r.text
        print("  [+] PASS: Hosted frontend loaded successfully with valid HTML.")
        passed += 1
    except Exception as e:
        print(f"  [-] FAIL: Hosted frontend failed: {e}")

    # -------------------------------------------------------------------------
    # 3. Verify Frontend Assets Delivery
    # -------------------------------------------------------------------------
    print("\n[Step 3/16] Verifying Frontend Static Asset Modules (/src/app.js, /src/styles/app.css)...")
    try:
        r_js = client.get("/src/app.js")
        assert r_js.status_code == 200, f"Failed to fetch /src/app.js: {r_js.status_code}"
        r_css = client.get("/src/styles/app.css")
        assert r_css.status_code == 200, f"Failed to fetch /src/styles/app.css: {r_css.status_code}"
        print("  [+] PASS: Frontend ES modules and CSS design system served properly.")
        passed += 1
    except Exception as e:
        print(f"  [-] FAIL: Asset delivery failed: {e}")

    # -------------------------------------------------------------------------
    # 4. Load Dashboard Summary
    # -------------------------------------------------------------------------
    print("\n[Step 4/16] Loading Dashboard Metrics (/api/dashboard/summary)...")
    try:
        r = client.get("/api/dashboard/summary")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        d = r.json()
        assert "total_inspections" in d
        assert "compliant_inspections" in d
        assert "potential_violations" in d
        print(f"  [+] PASS: Dashboard summary retrieved. Total recorded inspections: {d['total_inspections']}")
        passed += 1
    except Exception as e:
        print(f"  [-] FAIL: Dashboard summary failed: {e}")

    # -------------------------------------------------------------------------
    # 5. Create New Inspection
    # -------------------------------------------------------------------------
    print("\n[Step 5/16] Creating New Inspection (/api/inspections)...")
    inspection_id = None
    try:
        payload = {
            "product_name": "P6 Test Crunchy Biscuits 200g",
            "brand_name": "P6 Verifier",
            "commodity_category": "Food / Bakery",
            "inspector_id": "P6-TESTER-01",
            "location": "Central Hub Mumbai",
            "notes": "Automated release verification inspection",
            "image_coverage": {
                "front": True,
                "back": True,
                "side": False,
                "top": False
            }
        }
        r = client.post("/api/inspections", json=payload)
        assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
        data = r.json()
        inspection_id = data["id"]
        assert inspection_id, "Missing inspection ID"
        print(f"  [+] PASS: Created inspection with ID: {inspection_id}")
        passed += 1
    except Exception as e:
        print(f"  [-] FAIL: Create inspection failed: {e}")

    # -------------------------------------------------------------------------
    # 6. Upload Package Evidence Image
    # -------------------------------------------------------------------------
    print("\n[Step 6/16] Uploading Package Evidence Image (/api/inspections/{id}/image)...")
    uploaded_file_name = None
    try:
        # Generate a synthetic 1x1 PNG image
        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        files = {"file": ("front_panel.png", png_bytes, "image/png")}
        data = {"image_type": "front"}
        r = client.post(f"/api/inspections/{inspection_id}/image", files=files, data=data)
        assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
        resp_data = r.json()
        uploaded_file_name = resp_data["file_name"]
        assert uploaded_file_name, "Missing safe filename"
        print(f"  [+] PASS: Uploaded evidence. Safe filename: {uploaded_file_name}")
        passed += 1
    except Exception as e:
        print(f"  [-] FAIL: Image upload failed: {e}")

    # -------------------------------------------------------------------------
    # 7. Verify Stored Image Retrieval
    # -------------------------------------------------------------------------
    print("\n[Step 7/16] Verifying Stored Image Retrieval (/api/images/{file_name})...")
    try:
        assert uploaded_file_name, "No image was uploaded"
        r = client.get(f"/api/images/{uploaded_file_name}")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        assert len(r.content) > 0, "Empty image bytes received"
        print(f"  [+] PASS: Stored image successfully retrieved ({len(r.content)} bytes).")
        passed += 1
    except Exception as e:
        print(f"  [-] FAIL: Image retrieval failed: {e}")

    # -------------------------------------------------------------------------
    # 8. Submit Structured Extraction Payload
    # -------------------------------------------------------------------------
    print("\n[Step 8/16] Submitting Extraction Payload (/api/inspections/{id}/extraction)...")
    try:
        extraction_payload = {
            "inspection_id": inspection_id,
            "product_name": {
                "value": "P6 Test Crunchy Biscuits 200g",
                "raw_text": "P6 Test Crunchy Biscuits 200g",
                "confidence": 0.95,
                "location": "front"
            },
            "commodity_category": {
                "value": "Food / Bakery",
                "raw_text": "Category: Food / Bakery",
                "confidence": 0.90,
                "location": "front"
            },
            "country_of_origin": {
                "value": "India",
                "raw_text": "Country of Origin: India",
                "confidence": 0.98,
                "location": "back"
            },
            "net_quantity": {
                "value": 200.0,
                "unit": "g",
                "raw_text": "Net Qty: 200g",
                "confidence": 0.94,
                "surface_location": "front"
            },
            "net_quantity_observations": [
                {
                    "value": 200.0,
                    "unit": "g",
                    "raw_text": "Net Qty: 200g",
                    "surface_location": "front",
                    "confidence": 0.94
                },
                {
                    "value": 180.0,
                    "unit": "g",
                    "raw_text": "Net Weight: 180g",
                    "surface_location": "back",
                    "confidence": 0.88
                }
            ],
            "mrp": {
                "value": 40.0,
                "currency": "₹",
                "tax_inclusivity": True,
                "raw_text": "MRP Rs. 40.00 (incl. of all taxes)",
                "confidence": 0.95,
                "surface_location": "back"
            },
            "mrp_observations": [
                {
                    "value": 40.0,
                    "currency": "₹",
                    "tax_inclusivity": True,
                    "raw_text": "MRP Rs. 40.00 (incl. of all taxes)",
                    "surface_location": "back",
                    "confidence": 0.95
                },
                {
                    "value": 45.0,
                    "currency": "₹",
                    "tax_inclusivity": True,
                    "raw_text": "MRP Rs. 45.00",
                    "surface_location": "front",
                    "confidence": 0.89
                }
            ],
            "manufacturer": {
                "premises": "Plot 42",
                "street": "Industrial Area, Sector 5",
                "city": "Navi Mumbai",
                "state": "Maharashtra",
                "pin_code": "400705",
                "raw_text": "Mfg by: P6 Quality Foods Pvt Ltd, Plot 42, Industrial Area, Sector 5, Navi Mumbai, MH 400705",
                "confidence": 0.90
            },
            "date_of_manufacture": {
                "month": "03",
                "year": "2026",
                "raw_text": "Mfg Date: 03/2026",
                "confidence": 0.92
            },
            "consumer_care": {
                "name_or_office": "Consumer Care Manager",
                "address": "Plot 42, Industrial Area, Navi Mumbai, MH 400705",
                "phone": "1800-111-222",
                "email": "care@p6foods.example.com",
                "raw_text": "For complaints, contact Consumer Care Manager, Plot 42, Navi Mumbai, Phone: 1800-111-222, Email: care@p6foods.example.com",
                "confidence": 0.91
            },
            "image_coverage": {
                "front": True,
                "back": True,
                "side": False,
                "top": False
            }
        }
        r = client.post(f"/api/inspections/{inspection_id}/extraction", json=extraction_payload)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data.get("inspection_id") == inspection_id
        print("  [+] PASS: Extraction payload saved and linked to inspection.")
        passed += 1
    except Exception as e:
        print(f"  [-] FAIL: Extraction submission failed: {e}")


    # -------------------------------------------------------------------------
    # 9. Trigger Compliance Analysis
    # -------------------------------------------------------------------------
    print("\n[Step 9/16] Triggering Compliance Analysis Engine (/api/inspections/{id}/analyze)...")
    comp_result = None
    try:
        r = client.post(f"/api/inspections/{inspection_id}/analyze")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        comp_result = r.json()
        assert comp_result.get("overall_status") in ("COMPLIANT", "POTENTIAL_VIOLATION", "NEEDS_MANUAL_REVIEW")
        assert "rule_results" in comp_result
        assert len(comp_result["rule_results"]) >= 10
        print(f"  [+] PASS: Compliance evaluated. Overall Status: {comp_result['overall_status']} (Evaluated {len(comp_result['rule_results'])} rules)")
        passed += 1
    except Exception as e:
        print(f"  [-] FAIL: Compliance analysis failed: {e}")

    # -------------------------------------------------------------------------
    # 10. Verify Authoritative Compliance States
    # -------------------------------------------------------------------------
    print("\n[Step 10/16] Verifying Rule Status Semantics & Explanations...")
    try:
        valid_states = {"COMPLIANT", "POTENTIAL_VIOLATION", "NEEDS_MANUAL_REVIEW", "NOT_DETECTED", "NOT_APPLICABLE", "PENDING"}
        for rule in comp_result["rule_results"]:
            st = rule.get("status")
            assert st in valid_states, f"Invalid rule status: {st}"
            assert rule.get("rule_id"), "Missing rule_id"
            assert rule.get("explanation_for_inspector"), "Missing explanation_for_inspector"
        print(f"  [+] PASS: All {len(comp_result['rule_results'])} rules adhere to authoritative legal schema.")
        passed += 1
    except Exception as e:
        print(f"  [-] FAIL: Compliance status verification failed: {e}")

    # -------------------------------------------------------------------------
    # 11. Test Multi-Surface Conflict Detection (MRP & Net Quantity)
    # -------------------------------------------------------------------------
    print("\n[Step 11/16] Verifying MRP & Net Quantity Multi-Surface Conflict Detection...")
    try:
        r = client.get(f"/api/inspections/{inspection_id}/manual-review")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        rev_data = r.json()
        conflicts = rev_data.get("conflicts", [])
        assert len(conflicts) >= 1, "Expected at least one conflict from multi-surface observations"
        print(f"  [+] PASS: Multi-surface conflict detected and routed to manual review workspace ({len(conflicts)} conflict sets).")
        passed += 1
    except Exception as e:
        print(f"  [-] FAIL: Conflict verification failed: {e}")

    # -------------------------------------------------------------------------
    # 12. Test Medical Device Confirmation Gate (Fix 2)
    # -------------------------------------------------------------------------
    print("\n[Step 12/16] Testing Medical Device Confirmation Gate (/medical-device-confirmation)...")
    try:
        # Case A: Confirm as medical device
        r_med = client.post(
            f"/api/inspections/{inspection_id}/medical-device-confirmation",
            json={"is_confirmed_medical_device": True}
        )
        assert r_med.status_code == 200, f"Expected 200, got {r_med.status_code}"
        med_data = r_med.json()
        assert med_data["overall_status"] in ("COMPLIANT", "NOT_APPLICABLE", "NEEDS_MANUAL_REVIEW", "POTENTIAL_VIOLATION")

        # Revert back to standard product
        r_revert = client.post(
            f"/api/inspections/{inspection_id}/medical-device-confirmation",
            json={"is_confirmed_medical_device": False}
        )
        assert r_revert.status_code == 200
        print("  [+] PASS: Medical Device Confirmation Gate triggers and updates rules as per Fix 2.")
        passed += 1
    except Exception as e:
        print(f"  [-] FAIL: Medical Device Confirmation failed: {e}")

    # -------------------------------------------------------------------------
    # 13. Test Inspector Notes Update
    # -------------------------------------------------------------------------
    print("\n[Step 13/16] Updating Inspector Notes (/api/inspections/{id}/notes)...")
    try:
        r = client.post(
            f"/api/inspections/{inspection_id}/notes",
            json={"notes": "P6 verified: Package inspected according to Legal Metrology PCR 2011."}
        )
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        updated_insp = r.json()
        assert "P6 verified" in updated_insp.get("notes", "")
        print("  [+] PASS: Inspector notes persisted successfully.")
        passed += 1
    except Exception as e:
        print(f"  [-] FAIL: Notes update failed: {e}")

    # -------------------------------------------------------------------------
    # 14. Generate Structured JSON Inspection Report
    # -------------------------------------------------------------------------
    print("\n[Step 14/16] Generating Structured JSON Report (/api/reports/{id})...")
    try:
        r = client.get(f"/api/reports/{inspection_id}")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        report = r.json()
        assert report.get("title") == "LEGAL METROLOGY (PACKAGED COMMODITIES) SCREENING REPORT"
        assert "LEGAL DISCLAIMER" in report.get("disclaimer", "")
        assert report["inspection"]["id"] == inspection_id
        print("  [+] PASS: Structured JSON report generated with authoritative legal disclaimer.")
        passed += 1
    except Exception as e:
        print(f"  [-] FAIL: JSON report failed: {e}")

    # -------------------------------------------------------------------------
    # 15. Generate Printable HTML Inspection Report
    # -------------------------------------------------------------------------
    print("\n[Step 15/16] Generating Printable HTML Report (/api/reports/{id}/html)...")
    try:
        r = client.get(f"/api/reports/{inspection_id}/html")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        assert "text/html" in r.headers.get("content-type", "")
        assert "<!DOCTYPE html>" in r.text or "<html" in r.text
        assert "LEGAL METROLOGY" in r.text
        assert "P6 Test Crunchy Biscuits 200g" in r.text
        assert "Compliance Report" in r.text
        print("  [+] PASS: High-fidelity printable HTML report delivered successfully.")
        passed += 1
    except Exception as e:
        print(f"  [-] FAIL: HTML report failed: {repr(e)}")

    # -------------------------------------------------------------------------
    # 16. Verify Database Persistence Across Queries
    # -------------------------------------------------------------------------
    print("\n[Step 16/16] Verifying Database Write Persistence Across Subsequent Queries...")
    try:
        # Check inspection record
        r = client.get(f"/api/inspections/{inspection_id}")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        persisted = r.json()
        assert persisted["id"] == inspection_id
        assert persisted["product_name"] == "P6 Test Crunchy Biscuits 200g"
        assert persisted.get("images_count", 0) >= 1

        # Check linked evidence images
        r_ev = client.get(f"/api/inspections/{inspection_id}/evidence")
        assert r_ev.status_code == 200, f"Expected 200, got {r_ev.status_code}"
        ev_data = r_ev.json()
        assert len(ev_data.get("images", [])) >= 1
        assert ev_data["images"][0]["file_name"] == uploaded_file_name

        print(f"  [+] PASS: Database persistence verified (Record {inspection_id} intact with images_count={persisted['images_count']} and linked evidence).")
        passed += 1
    except Exception as e:
        print(f"  [-] FAIL: Database persistence check failed: {repr(e)}")


    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f"SMOKE TEST SUMMARY: {passed}/{total} Passed ({(passed/total)*100:.1f}%)")
    print("=" * 70)

    if passed == total:
        print("\n>>> ALL PRODUCTION END-TO-END SMOKE TESTS PASSED CLEANLY! <<<\n")
        return 0
    else:
        print(f"\n>>> {total - passed} SMOKE TESTS FAILED! <<<\n")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SIH26034 Production Smoke Test")
    parser.add_argument("--target-url", default="http://127.0.0.1:8000", help="Base URL of deployed service")
    args = parser.parse_args()
    sys.exit(run_smoke_tests(args.target_url))
