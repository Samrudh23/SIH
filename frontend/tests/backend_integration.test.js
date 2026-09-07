/**
 * Real Backend Integration & Contract Test Suite for SIH26034 P4 Frontend
 * Validates real HTTP client communication against P3 FastAPI backend
 * and covers the 14 required compliance scenarios.
 */

import { apiService, ApiError } from "../src/services/api.js";

export async function runBackendIntegrationTests(assert) {
  // Switch apiService to live backend mode
  apiService.setMode("live");
  const isOnline = await apiService.checkBackendHealth();
  if (!isOnline) {
    console.warn("Backend server not online; skipping live backend integration tests.");
    return;
  }

  // Integration Test 1: Dashboard Summary Live Endpoint
  await assert.test("Live Backend 1. Dashboard summary returns live operational KPIs", async () => {
    const summary = await apiService.getDashboardSummary();
    assert.ok(summary.total_inspections >= 6, "Must have seeded inspections");
    assert.ok(typeof summary.compliant_inspections === "number");
    assert.ok(typeof summary.potential_violations === "number");
    assert.ok(typeof summary.needs_manual_review === "number");
    assert.ok(Array.isArray(summary.recent_inspections));
    assert.ok(Array.isArray(summary.top_violated_rules));
  });

  // Integration Test 2: Inspection History Listing & Filtering
  await assert.test("Live Backend 2. List inspections with search and status filtering", async () => {
    const listAll = await apiService.listInspections();
    assert.ok(listAll.total >= 6, "Total seeded inspections should be >= 6");
    assert.ok(listAll.items.length >= 6);

    // Filter by compliance status
    const listViolations = await apiService.listInspections({ compliance_status: "POTENTIAL_VIOLATION" });
    assert.ok(listViolations.items.length >= 1, "Should filter potential violations");
    listViolations.items.forEach((item) => {
      assert.equal(item.compliance_status, "POTENTIAL_VIOLATION");
    });

    // Filter by product query
    const listSearch = await apiService.listInspections({ product: "Parle" });
    assert.ok(listSearch.items.length >= 1, "Should find Parle product");
  });

  // Integration Test 3: Create Inspection & Image Upload in Live Backend
  let createdInspectionId = null;
  await assert.test("Live Backend 3. Create inspection and upload image evidence", async () => {
    const createPayload = {
      product_name: "Integration Test Biscuit 200g",
      brand_name: "TestBiscuitCo",
      commodity_category: "Biscuits",
      inspector_id: "insp_integration_test",
      image_coverage: { front: true, back: true, side: false, top: false },
      metadata: { env: "integration_test" },
    };

    const inspection = await apiService.createInspection(createPayload);
    assert.ok(inspection.id, "Created inspection must receive UUID id");
    assert.equal(inspection.product_name, "Integration Test Biscuit 200g");
    assert.equal(inspection.status, "CREATED");
    assert.equal(inspection.compliance_status, "PENDING");
    createdInspectionId = inspection.id;

    // Upload mock image blob
    const dummyBlob = new Blob(["fake image bytes"], { type: "image/jpeg" });
    const dummyFile = new File([dummyBlob], "front_panel.jpg", { type: "image/jpeg" });
    const uploadRes = await apiService.uploadInspectionImage(createdInspectionId, dummyFile, "front");
    assert.ok(uploadRes.evidence_id, "Evidence record must receive ID");
    assert.equal(uploadRes.image_type, "front");

    // Fetch evidence
    const evidence = await apiService.getEvidence(createdInspectionId);
    assert.ok(evidence.images.length >= 1, "Evidence images must include uploaded file");
  });

  // Integration Test 4: Submit Structured Extraction Payload
  await assert.test("Live Backend 4. Submit P1 ExtractionPayload and verify storage", async () => {
    const extractionPayload = {
      inspection_id: createdInspectionId,
      product_name: {
        value: "Integration Test Biscuit 200g",
        raw_text: "Integration Test Biscuit 200g",
        confidence: 0.97,
        location: "front",
      },
      commodity_category: {
        value: "Biscuits",
        raw_text: "Biscuits",
        confidence: 0.99,
        location: "front",
      },
      manufacturer: {
        premises: "Plot 10, Industrial Estate",
        city: "Pune",
        state: "Maharashtra",
        pin_code: "411001",
        raw_text: "Mfg by: Biscuit Co, Plot 10, Pune - 411001",
        confidence: 0.95,
      },
      country_of_origin: {
        value: "India",
        raw_text: "Made in India",
        confidence: 0.99,
        location: "back",
      },
      net_quantity: {
        value: 200.0,
        unit: "g",
        raw_text: "Net Weight: 200 g",
        confidence: 0.96,
        surface_location: "front",
        location: "front",
        quiet_zone_clear: true,
      },
      net_quantity_observations: [
        {
          value: 200.0,
          unit: "g",
          raw_text: "Net Weight: 200 g",
          confidence: 0.96,
          surface_location: "front",
          location: "front",
        },
      ],
      mrp: {
        value: 40.0,
        currency: "₹",
        tax_inclusivity: true,
        raw_text: "MRP ₹ 40.00 incl. of all taxes",
        confidence: 0.95,
        surface_location: "back",
        location: "back",
        is_sticker: false,
      },
      mrp_observations: [
        {
          value: 40.0,
          currency: "₹",
          tax_inclusivity: true,
          raw_text: "MRP ₹ 40.00 incl. of all taxes",
          confidence: 0.95,
          surface_location: "back",
          location: "back",
        },
      ],
      date_of_manufacture: {
        month: "09",
        year: "2026",
        raw_text: "Mfg: 09/2026",
        confidence: 0.94,
      },
      consumer_care: {
        phone: "1800223344",
        email: "care@biscuitco.in",
        raw_text: "Helpline: 1800223344, care@biscuitco.in",
        confidence: 0.93,
      },
      image_coverage: { front: true, back: true, side: false, top: false },
    };

    const submitRes = await apiService.submitExtraction(createdInspectionId, extractionPayload);
    assert.equal(submitRes.status, "success");

    const fetchedExt = await apiService.getExtraction(createdInspectionId);
    assert.equal(fetchedExt.product_name.value, "Integration Test Biscuit 200g");
    assert.equal(fetchedExt.mrp.value, 40.0);
    assert.equal(fetchedExt.net_quantity.value, 200.0);
  });

  // Integration Test 5: Analyze Inspection with Real Compliance Engine (P2)
  await assert.test("Live Backend 5. Execute P2 RealComplianceEngine evaluation", async () => {
    const compliance = await apiService.analyzeInspection(createdInspectionId);
    assert.ok(compliance.overall_status, "Must return overall status");
    assert.equal(compliance.overall_status, "COMPLIANT");
    assert.equal(compliance.rule_results.length, 15, "Engine must evaluate all 15 rules");
    assert.ok(compliance.summary_counts.compliant >= 8);

    // Verify visual-aid rules are restricted
    const qzRule = compliance.rule_results.find((r) => r.rule_id === "REQ-MVP-14");
    assert.ok(qzRule.status === "NEEDS_MANUAL_REVIEW" || qzRule.status === "NOT_DETECTED");
  });

  // Integration Test 6: Medical Device Confirmation Gate (Fix 2)
  await assert.test("Live Backend 6. Fix 2 Medical Device confirmation gate via live backend", async () => {
    // Create an isolated medical device candidate inspection for idempotency
    const medInsp = await apiService.createInspection({
      product_name: "Integration Test Sterile Swab",
      brand_name: "MedCo",
      commodity_category: "Medical Device",
      inspector_id: "insp_test_gate",
      image_coverage: { front: true, back: true, side: false, top: false },
    });
    const medId = medInsp.id;

    // Submit extraction with medical device marker (CDSCO)
    await apiService.submitExtraction(medId, {
      inspection_id: medId,
      product_name: { value: "Sterile Swab", raw_text: "Sterile Swab", confidence: 0.95, location: "front" },
      commodity_category: { value: "Medical Device", raw_text: "Medical Device", confidence: 0.95, location: "front" },
      medical_device_markers: { value: "MD-1234", raw_text: "Mfg Lic MD-1234", confidence: 0.92, location: "back" },
      image_coverage: { front: true, back: true, side: false, top: false },
    });

    // Run initial analysis: REQ-MVP-11 should be NEEDS_MANUAL_REVIEW (Fix 2 gate pending)
    const initialResult = await apiService.analyzeInspection(medId);
    const medRule = initialResult.rule_results.find((r) => r.rule_id === "REQ-MVP-11");
    assert.ok(medRule, "REQ-MVP-11 must be evaluated in compliance result");
    assert.equal(medRule.status, "NEEDS_MANUAL_REVIEW", "Medical device candidate must trigger NEEDS_MANUAL_REVIEW on REQ-MVP-11");

    // Send confirmation: true -> suppresses PCR rules to NOT_APPLICABLE
    const confirmedRes = await apiService.confirmMedicalDevice(medId, true);
    assert.equal(confirmedRes.overall_status, "NOT_APPLICABLE", "Confirmed medical device must be NOT_APPLICABLE");

    // Send rejection: false -> standard PCR rules evaluated
    const rejectedRes = await apiService.confirmMedicalDevice(medId, false);
    assert.ok(
      rejectedRes.overall_status === "COMPLIANT" ||
      rejectedRes.overall_status === "POTENTIAL_VIOLATION" ||
      rejectedRes.overall_status === "NEEDS_MANUAL_REVIEW",
      "Rejected classification must evaluate under standard PCR"
    );
  });

  // Integration Test 7: Inspector Notes Recording
  await assert.test("Live Backend 7. Update inspector notes via POST /notes", async () => {
    const noteText = "Measured font height: 4.2mm with digital caliper. Verified packaging seal.";
    const updated = await apiService.updateNotes(createdInspectionId, noteText);
    assert.equal(updated.notes, noteText);

    // Verify reflected in getInspection
    const fetched = await apiService.getInspection(createdInspectionId);
    assert.equal(fetched.notes, noteText);
  });

  // Integration Test 8: Report Generation (JSON and HTML)
  await assert.test("Live Backend 8. Generate structured JSON report and printable HTML", async () => {
    const reportData = await apiService.getReportData(createdInspectionId);
    assert.ok(reportData.title.includes("LEGAL METROLOGY"));
    assert.equal(reportData.inspection.id, createdInspectionId);
    assert.ok(reportData.compliance_evaluation.findings.length === 15);

    const reportHtml = await apiService.getReportHtml(createdInspectionId);
    assert.ok(typeof reportHtml === "string");
    assert.ok(reportHtml.includes("LEGAL METROLOGY") || reportHtml.includes("Compliance"));
  });

  // Integration Test 9: Strict Error on Nonexistent Inspection
  await assert.test("Live Backend 9. Requesting invalid inspection throws ApiError with 404", async () => {
    let threw = false;
    try {
      await apiService.getInspection("nonexistent-uuid-12345");
    } catch (err) {
      threw = true;
      assert.ok(err instanceof ApiError);
      assert.equal(err.status, 404);
      assert.ok(err.actionableRemedy);
    }
    assert.ok(threw, "Must throw 404 ApiError");
  });
}
