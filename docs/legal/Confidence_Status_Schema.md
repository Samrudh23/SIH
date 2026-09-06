# SIH26034 — Step B: Confidence / Status Schema

**Companion document to:** `pcr-compliance-rule-specification-v2-FINAL.md`
**Purpose:** Defines how the rule engine represents, scores, and escalates every compliance check output. This is a software-engineering design document, not a legal document — it contains no new legal claims and makes no statutory interpretations. All rule citations below are inherited as-is from the finalized legal spec.

---

## 1. Result States (Final Set — 6 States)

| State | Meaning | Never means |
|---|---|---|
| `COMPLIANT` | Evidence is sufficient and the applicable requirement appears satisfied. | "Legally guaranteed compliant." |
| `POTENTIAL_VIOLATION` | Evidence is sufficient and indicates the requirement is likely violated. | A final legal determination. |
| `NEEDS_MANUAL_REVIEW` | Evidence is ambiguous, incomplete, low-confidence, or requires human/physical judgment. | A system failure — this is a correct, intended outcome. |
| `NOT_APPLICABLE` | An exemption/exception is established with sufficient evidence. | An assumption made from a weak signal. |
| `NOT_DETECTED` | Expected information was not found. | Proof that the declaration is missing. |
| `ANALYSIS_FAILED` | The technical pipeline (OCR/CV) failed or was unreliable. | A compliance judgment of any kind. |

**Governing principle (Section 26, prior audit instructions — carried forward here):** automate wherever evidence is strong and legally unambiguous; escalate to `NEEDS_MANUAL_REVIEW` only where uncertainty genuinely matters. Do not turn every check into a manual-review check by default — that defeats the purpose of the system.

---

## 2. Per-Check Result Object (applies to all 15 rules)

```json
{
  "rule_id": "REQ-MVP-02",
  "status": "NEEDS_MANUAL_REVIEW",
  "detected_value": "incl of taxes ₹99",
  "normalized_value": "MRP=99.00; tax_inclusive=true",
  "detection_confidence": 0.71,
  "applicability_confidence": 1.0,
  "reason": "Tax-inclusivity phrase detected but OCR confidence is below threshold.",
  "evidence": {
    "image_id": "img_003",
    "bounding_box": { "x": 120, "y": 340, "w": 200, "h": 40 },
    "raw_ocr_text": "incl of taxes ₹99",
    "crop_url": "..."
  },
  "explanation_for_inspector": "Price and tax-inclusion phrase were found, but confidence is low due to image clarity. Please confirm manually.",
  "conflicts": null,
  "rule_version": {
    "source": "01_Packaged_Commodities_Rules_2011.pdf",
    "clause": "Rule 2(m), Rule 6(1)(e)",
    "gsr_number": "G.S.R. 202(E)",
    "verification_status": "VERIFIED — VERBATIM"
  }
}
```

**Two confidence numbers, kept permanently separate — never combined into one score:**
- `detection_confidence` — how confident OCR/CV is about *what it read*.
- `applicability_confidence` — how confident the system is that *this rule even applies* to this product (relevant to REQ-MVP-01 small-package exemption, REQ-MVP-02 Bidi/LPG exemption, REQ-MVP-09 import-origin routing, REQ-MVP-10 Pan Masala routing, REQ-MVP-11 medical-device routing, REQ-MVP-12 Second Schedule classification).

Never phrase either number as "% legally compliant." That framing is explicitly prohibited — it misrepresents a screening signal as a legal conclusion.

`raw_ocr_text` must always be preserved as-is alongside `normalized_value`. Normalization must never overwrite or discard the original observation.

---

## 3. Fix 1 — REQ-MVP-02 (MRP Layout): Fuzzy Matching + Manual-Review Fallback

**Problem being fixed:** the legal spec's software-interpretation language ("exact legal layout templates") is legally accurate as a description of the ideal declaration, but implementing it as rigid string/regex matching produces false positives on real packaging, which varies in wording, spacing, and punctuation far more than a fixed template allows for. The original `Possible System Results` for this rule also had no manual-review fallback, meaning every OCR ambiguity became a hard `POTENTIAL_VIOLATION`. Both are fixed at the schema/pipeline level below — no change to the legal spec document is needed, since the legal requirement itself is correctly stated there.

```
OCR text extracted near price region
              │
              ▼
    Contains a price figure? (₹ symbol OR "Rs"/"MRP" + numeral)
              │
         ┌────┴────┐
        NO         YES
         │           │
         ▼           ▼
   NOT_DETECTED   Contains a tax-inclusivity keyword family?
                  ("incl", "inclusive", "taxes" — fuzzy match,
                   not exact phrase)
                       │
                  ┌────┴────┐
                 NO         YES
                  │           │
                  ▼           ▼
          POTENTIAL_      detection_confidence ≥ 0.75?
          VIOLATION              │
          "Tax-inclusivity   ┌───┴───┐
          phrase not found" YES      NO
                              │        │
                              ▼        ▼
                         COMPLIANT  NEEDS_MANUAL_REVIEW
                                    "Price/tax phrase found
                                    but OCR confidence too
                                    low to confirm."
```

`NOT_APPLICABLE` remains available separately when REQ-MVP-01's exemption logic (product classified as Bidi/domestic LPG) is triggered — this flow only governs the price/tax-phrase detection step itself.

---

## 4. Fix 2 — REQ-MVP-11 (Medical Devices): Confirmation Gate Before Bypass

**Problem being fixed:** the legal spec correctly describes the statutory routing exemption, but its `Possible System Results` (`NOT_APPLICABLE` only, automatically triggered) means a single keyword match silently disables all standard PCR checks. A missed/garbled license marker would wrongly apply full PCR checks to an actual medical device; a false keyword match would wrongly exempt a normal product with nobody noticing either way. This is fixed by inserting a mandatory human confirmation step before the terminal `NOT_APPLICABLE` state is reached.

```
Medical license / CDSCO marker pattern detected in OCR text
              │
              ▼
    applicability_confidence ≥ 0.85?
              │
         ┌────┴────┐
        YES         NO
         │           │
         ▼           ▼
  NEEDS_MANUAL_    NEEDS_MANUAL_REVIEW
  REVIEW           "Classification signal detected
  "Probable         but confidence too low to route
  medical device     automatically."
  detected. Confirm
  before switching
  rule sets?"
  [Inspector: Yes/No]
         │
         ▼ (only on explicit inspector confirmation = Yes)
  NOT_APPLICABLE
  (routed to Medical Devices Rules,
  2017 module; standard PCR checks
  suppressed for this inspection)
         │
         ▼ (if inspector selects No)
  Standard PCR checks proceed normally;
  system records the false-positive
  signal for later model tuning.
```

**REQ-MVP-10 (Pan Masala) is intentionally NOT given this gate.** The stakes are asymmetric: a false Pan Masala match just runs extra checks on a normal product (low cost), whereas a missed medical-device match or false medical-device exemption silently skips real compliance checks (high cost). Pan Masala routing can remain automatic per the legal spec as written.

---

## 5. Image-Coverage-Aware `NOT_DETECTED` Handling

Applies to: REQ-MVP-01, REQ-MVP-07, REQ-MVP-08, REQ-MVP-09, REQ-MVP-13 (any rule where the relevant declaration could plausibly exist on a package surface not submitted).

```
Expected declaration not found in OCR output
              │
              ▼
    Was sufficient package surface area submitted?
    (inspector-confirmed checklist: front / back / side / top,
     relevant to this declaration type — not computer vision)
              │
         ┌────┴────┐
        YES         NO
         │           │
         ▼           ▼
   POTENTIAL_    NEEDS_MANUAL_REVIEW
   VIOLATION     "Submitted images may not show this
                 declaration — please upload additional
                 package surfaces."
```

This requires one lightweight field per inspection: `image_coverage: { front: bool, back: bool, side: bool, top: bool }`, set by the inspector at upload time. No automated "did I see the whole package" computer vision is needed for Phase 1 — that would be Phase 2 scope.

---

## 6. Conflict Detection (Scoped to MRP and Net Quantity Only)

General-purpose conflict detection across all 15 rules is explicitly **out of scope for Phase 1** — it's real engineering effort for a scenario your demo likely won't showcase. Scope it to the two fields most likely to actually disagree across package surfaces:

```json
{
  "conflicts": {
    "field": "mrp",
    "values_found": [
      { "value": "₹100", "image_id": "img_001", "location": "front" },
      { "value": "₹120", "image_id": "img_002", "location": "back" }
    ],
    "resolution": "NEEDS_MANUAL_REVIEW",
    "reason": "Conflicting MRP values detected across submitted package surfaces."
  }
}
```

Do not silently select one value when two submitted surfaces disagree — always route to `NEEDS_MANUAL_REVIEW` with both values preserved as evidence.

**Phase 2:** extend conflict detection to net quantity, manufacturer address, and date fields once the Phase 1 demo has validated the core pattern.

---

## 7. Rule Versioning Metadata (All 15 Rules)

Pulled directly from the finalized legal spec — no new legal claims made here.

| Rule ID | Clause | G.S.R. / Amendment | Source Document | Verification Status |
|---|---|---|---|---|
| REQ-MVP-01 | Rule 6(1); exemption under Rule 26 | G.S.R. 202(E) (Principal) | `01_Packaged_Commodities_Rules_2011.pdf` | VERIFIED — VERBATIM |
| REQ-MVP-02 | Rule 2(m), Rule 6(1)(e) | G.S.R. 202(E) (Principal) | `01_Packaged_Commodities_Rules_2011.pdf` | VERIFIED — VERBATIM |
| REQ-MVP-03 | Rule 13(1), (4), (5) | G.S.R. 202(E) (Principal) | `01_Packaged_Commodities_Rules_2011.pdf` | VERIFIED — VERBATIM |
| REQ-MVP-04 | Rule 13(2), (3) + Proviso | G.S.R. 202(E) (Principal) | `01_Packaged_Commodities_Rules_2011.pdf` | CONFIRMED |
| REQ-MVP-05 | Rule 12(6) | G.S.R. 202(E) (Principal) | `01_Packaged_Commodities_Rules_2011.pdf` | CONFIRMED |
| REQ-MVP-06 | Rule 6(1)(d) + Proviso | G.S.R. 202(E) (Principal) | `01_Packaged_Commodities_Rules_2011.pdf` | CONFIRMED |
| REQ-MVP-07 | Rule 6(2) | G.S.R. 202(E) (Principal) | `01_Packaged_Commodities_Rules_2011.pdf` | CONFIRMED |
| REQ-MVP-08 | Rule 10(1) Explanation | G.S.R. 202(E) (Principal) | `01_Packaged_Commodities_Rules_2011.pdf` | CONFIRMED |
| REQ-MVP-09 | Rule 10(1) Proviso 2 | G.S.R. 202(E) (Principal) | `01_Packaged_Commodities_Rules_2011.pdf` | CONFIRMED |
| REQ-MVP-10 | Rule 26(a) Second Proviso | G.S.R. 881(E) (2nd Amendment 2025) | `03_PCR_Second_Amendment_2025.pdf` | CONFIRMED |
| REQ-MVP-11 | Rule 2(h)/7(2)/7(3) Provisos | G.S.R. 778(E) (Amendment 2025) | `02_PCR_Amendment_2025_24-10-2025.pdf` | CONFIRMED |
| REQ-MVP-12 | Rule 5, Proviso | G.S.R. 202(E) (Principal) | `01_Packaged_Commodities_Rules_2011.pdf` | VERIFIED — VERBATIM |
| REQ-MVP-13 | Rule 6(3) | G.S.R. 202(E) (Principal) | `01_Packaged_Commodities_Rules_2011.pdf` | VERIFIED — VERBATIM |
| REQ-MVP-14 | Rule 8(1), Proviso | G.S.R. 202(E) (Principal) | `01_Packaged_Commodities_Rules_2011.pdf` | CONFIRMED |
| REQ-MVP-15 | Rule 9(1) + Proviso (a) | G.S.R. 202(E) (Principal) | `01_Packaged_Commodities_Rules_2011.pdf` | CONFIRMED |

`last_verified`: 2026-09-05 (date of final narrow verification pass) for all rows.

---

## 8. Manual Review Triggers — Centralized List

Any of the following should route a check to `NEEDS_MANUAL_REVIEW`, regardless of which rule is being evaluated:

- Insufficient image coverage for the declaration type in question
- OCR/detection confidence below the rule's threshold
- Conflicting values for the same field across submitted surfaces (MRP, net quantity — Phase 1 scope)
- Uncertain product classification where routing depends on it (medical device, Pan Masala, Second Schedule category)
- Physical measurement required (font height, quiet-zone clearance, contrast ratio)
- Ambiguous OCR output with multiple plausible readings materially affecting the result
- Applicability of an exemption/exception cannot be established with sufficient confidence

---

## 9. Rules That Never Produce `COMPLIANT` / `POTENTIAL_VIOLATION` (Visual-Aid-Only)

Per the legal spec, REQ-MVP-14 (quiet-zone clearance) and REQ-MVP-15 (contrast) are restricted to `NEEDS_MANUAL_REVIEW` / `NOT_DETECTED` only. This restriction is enforced at the schema level: the rule engine must reject any attempt to emit `COMPLIANT` or `POTENTIAL_VIOLATION` for these two rule IDs. This is a hard constraint, not a convention — Rule 9(1)'s contrast requirement is confirmed qualitative-only with no numeric threshold in the statute, so a hard pass/fail result would misrepresent the law.

---

## 10. Phase 1 / Phase 2 Boundary

**Phase 1 (build now):**
- All 6 result states
- `detection_confidence` / `applicability_confidence` split
- Image-coverage-aware `NOT_DETECTED` handling (inspector-confirmed checklist, not CV-based)
- Conflict detection — MRP and net quantity only
- Medical-device confirmation gate
- Rule-versioning metadata (static table above, not a full version-control system)
- English-only OCR and text matching

**Phase 2 (do not build yet):**
- General-purpose conflict detection across all 15 rules
- Multilingual OCR, extraction, and declaration matching (Hindi + other Indian languages)
- Full rule-dependency graph engine
- Automated image-coverage detection via computer vision (replacing the inspector checklist)
- Ambiguous-extraction multi-candidate resolution beyond a single manual-review flag

---

## 11. What This Document Deliberately Does Not Contain

- No new legal claims, quotes, or citations beyond what already exists in `pcr-compliance-rule-specification-v2-FINAL.md`.
- No changes to any rule's stated Automation Level, Legal Requirement, or Exceptions/Applicability text.
- No database schema or API endpoint design (Step C/D scope).
- No OCR/CV model selection or pipeline implementation detail (Step D scope).

This document's only job is to define how results are represented, scored, and escalated — Step C (rule engine structure) and Step D (OCR/CV pipeline) are built against this schema next.
