/**
 * Frontend Compliance Test Suite for SIH26034
 * Verifies result states, 15 MVP rules, multi-surface conflicts, Fix 2 medical device gate, and fixtures.
 */

import { RESULT_STATE_CONFIG, renderResultBadge } from "../src/components/StatusBadge.js";
import { renderConfidenceMeter } from "../src/components/ConfidenceMeter.js";
import { renderConflictViewer } from "../src/components/ConflictViewer.js";
import { MOCK_FIXTURES, RULE_METADATA } from "../src/services/mockFixtures.js";
import { apiService } from "../src/services/api.js";

export async function runTests(assert) {
  // Test 1: All 6 result states exist and render properly
  await assert.test("1. All 6 authoritative compliance result states are defined", () => {
    const expectedStates = [
      "COMPLIANT",
      "POTENTIAL_VIOLATION",
      "NEEDS_MANUAL_REVIEW",
      "NOT_APPLICABLE",
      "NOT_DETECTED",
      "ANALYSIS_FAILED",
    ];

    expectedStates.forEach((state) => {
      assert.ok(RESULT_STATE_CONFIG[state], `ResultState '${state}' must be defined in RESULT_STATE_CONFIG`);
      const html = renderResultBadge(state);
      assert.ok(html.includes(state.replace(/_/g, " ")), `Badge for '${state}' must contain text label`);
      assert.ok(html.includes("aria-label"), `Badge for '${state}' must include accessible aria-label`);
    });
  });

  // Test 2: All 15 MVP rules have verifiable legal citations
  await assert.test("2. All 15 MVP rules exist with authoritative legal metadata", () => {
    const ruleIds = Array.from({ length: 15 }, (_, i) => `REQ-MVP-${String(i + 1).padStart(2, "0")}`);
    assert.equal(ruleIds.length, 15, "Must evaluate exactly 15 MVP rules");

    ruleIds.forEach((rId) => {
      const meta = RULE_METADATA[rId];
      assert.ok(meta, `Rule '${rId}' must exist in RULE_METADATA`);
      assert.ok(meta.clause, `Rule '${rId}' must specify statutory clause`);
      assert.ok(meta.source, `Rule '${rId}' must specify source document`);
      assert.ok(meta.gsr_number, `Rule '${rId}' must cite G.S.R. notification`);
      assert.ok(meta.verification_status, `Rule '${rId}' must specify verification status`);
    });
  });

  // Test 3: Visual aid rules REQ-MVP-14 & REQ-MVP-15 are never COMPLIANT or POTENTIAL_VIOLATION
  await assert.test("3. Visual-aid-only rules (REQ-MVP-14 & REQ-MVP-15) never issue automated pass/fail", () => {
    const visualAidIds = ["REQ-MVP-14", "REQ-MVP-15"];

    Object.values(MOCK_FIXTURES).forEach((fixture) => {
      if (fixture.compliance && fixture.compliance.rule_results) {
        fixture.compliance.rule_results.forEach((rule) => {
          if (visualAidIds.includes(rule.rule_id)) {
            assert.ok(
              rule.status !== "COMPLIANT" && rule.status !== "POTENTIAL_VIOLATION",
              `Visual-aid rule ${rule.rule_id} in ${fixture.inspection.id} produced invalid automated state: ${rule.status}`
            );
            assert.ok(
              ["NEEDS_MANUAL_REVIEW", "NOT_DETECTED", "NOT_APPLICABLE", "ANALYSIS_FAILED"].includes(rule.status),
              `Visual-aid rule ${rule.rule_id} must produce restricted states only`
            );
          }
        });
      }
    });
  });

  // Test 4: Multi-surface conflicts preserve all observations without silently picking a winner
  await assert.test("4. Multi-surface observation conflicts display all readings side-by-side", () => {
    // Check MRP conflict fixture (insp-004)
    const mrpFixture = MOCK_FIXTURES["insp-004"];
    assert.ok(mrpFixture, "MRP conflict fixture insp-004 must exist");
    assert.equal(mrpFixture.compliance.overall_status, "NEEDS_MANUAL_REVIEW");

    const mrpRule = mrpFixture.compliance.rule_results.find((r) => r.rule_id === "REQ-MVP-02");
    assert.ok(mrpRule.conflicts, "MRP rule must include conflict object");
    assert.equal(mrpRule.conflicts.values_found.length, 2, "Must preserve both observations");
    assert.equal(mrpRule.conflicts.resolution, "NEEDS_MANUAL_REVIEW");

    const conflictHtml = renderConflictViewer(mrpRule.conflicts);
    assert.ok(conflictHtml.includes("190"), "Conflict viewer must show 190 observation");
    assert.ok(conflictHtml.includes("210"), "Conflict viewer must show 210 observation");
    assert.ok(conflictHtml.toLowerCase().includes("front"), "Conflict viewer must identify front location");
    assert.ok(conflictHtml.toLowerCase().includes("back"), "Conflict viewer must identify back location");

    // Check Net Quantity conflict fixture (insp-005)
    const qtyFixture = MOCK_FIXTURES["insp-005"];
    assert.ok(qtyFixture, "Net Quantity conflict fixture insp-005 must exist");
    const qtyRule = qtyFixture.compliance.rule_results.find((r) => r.rule_id === "REQ-MVP-03");
    assert.ok(qtyRule.conflicts, "Net quantity rule must include conflict object");
    assert.equal(qtyRule.conflicts.values_found.length, 2);
  });

  // Test 5: Fix 2 Medical device confirmation gate routes properly
  await assert.test("5. Fix 2 Medical device confirmation gate executes correctly", async () => {
    const pendingFixture = MOCK_FIXTURES["insp-006"];
    assert.equal(pendingFixture.compliance.overall_status, "NEEDS_MANUAL_REVIEW");

    const medRule = pendingFixture.compliance.rule_results.find((r) => r.rule_id === "REQ-MVP-11");
    assert.equal(medRule.status, "NEEDS_MANUAL_REVIEW", "Pending gate must be NEEDS_MANUAL_REVIEW");

    // Confirm as medical device -> PCR suppressed to NOT_APPLICABLE
    const confirmedResult = await apiService.confirmMedicalDevice("insp-006", true);
    assert.equal(confirmedResult.overall_status, "NOT_APPLICABLE", "Confirmed medical device must suppress to NOT_APPLICABLE");

    // Reject classification -> PCR checks proceed
    const rejectedResult = await apiService.confirmMedicalDevice("insp-006", false);
    assert.equal(rejectedResult.overall_status, "COMPLIANT", "Rejected classification must apply standard PCR");
  });

  // Test 6: Dual confidence split is maintained permanently separate
  await assert.test("6. Detection Confidence and Applicability Confidence remain separate", () => {
    const html = renderConfidenceMeter(0.72, 1.0);
    assert.ok(html.includes("72%"), "Must display OCR detection confidence of 72%");
    assert.ok(html.includes("100%"), "Must display Rule applicability confidence of 100%");
    assert.ok(!html.includes("86%"), "Must NEVER average confidence scores together");
    assert.ok(!html.includes("% legally compliant"), "Must NEVER use prohibited phrase '% legally compliant'");
  });

  // Test 7: Incomplete surface coverage marks missing declarations NOT_DETECTED
  await assert.test("7. Missing declarations on incomplete surface coverage are NOT_DETECTED, not violations", () => {
    const fixture = MOCK_FIXTURES["insp-008"];
    assert.ok(fixture.inspection.image_coverage.front === true);
    assert.ok(fixture.inspection.image_coverage.back === false);

    const mrpRule = fixture.compliance.rule_results.find((r) => r.rule_id === "REQ-MVP-02");
    assert.equal(mrpRule.status, "NOT_DETECTED", "Missing MRP on front-only image must be NOT_DETECTED, not a violation");
  });

  // Test 8: All 11 fixtures load cleanly
  await assert.test("8. All 11 realistic mock compliance scenarios load and adhere to schema", () => {
    const fixtureKeys = Object.keys(MOCK_FIXTURES);
    assert.equal(fixtureKeys.length, 11, "Must contain exactly 11 distinct test fixtures");

    fixtureKeys.forEach((key) => {
      const f = MOCK_FIXTURES[key];
      assert.ok(f.inspection, `Fixture ${key} must have inspection model`);
      assert.ok(f.inspection.id, `Fixture ${key} inspection must have ID`);
      assert.ok(f.inspection.status, `Fixture ${key} inspection must have workflow status`);
      assert.ok(f.inspection.image_coverage, `Fixture ${key} must specify image_coverage`);
      if (f.compliance) {
        assert.ok(f.compliance.overall_status, `Fixture ${key} compliance must have overall status`);
        assert.ok(f.compliance.summary_counts, `Fixture ${key} compliance must have summary counts`);
      }
    });
  });
}
