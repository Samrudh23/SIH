# SIH26034 — P3 Backend API Integration Specification

> **System:** Legal Metrology (Packaged Commodities) Rules, 2011 Compliance Screening API  
> **Author:** P3 Backend Integration Architecture  
> **Date:** September 7, 2026  
> **Status:** Production-Ready & Verified (`p2-real-v1.0.0`)  
> **Standard Baseline:** `docs/legal/PCR_Compliance_Rules.md` & `docs/legal/Confidence_Status_Schema.md`

---

## 1. API Architecture Overview

The backend serves as the authoritative, deterministic integration boundary between:
- **P1 Extraction**: Optical Character Recognition (OCR) and computer vision models extracting package surface declarations into structured `ExtractionPayload` representations.
- **P2 Legal Compliance Engine**: The statutory rule evaluation engine (`RealComplianceEngine`) evaluating all 15 Legal Metrology MVP rules without lossy transformation or distortion of legal semantics.
- **P3 Backend & Persistence**: FastAPI application managing SQLite/PostgreSQL storage, inspection lifecycles, multi-surface observation reconciliation, and report generation.
- **P4/P4A Frontend**: The Single-Page Application (SPA) dashboard connecting to `/api` endpoints for inspections, surface uploads, manual reviews, and certificates.

```
PACKAGE IMAGES (front/pdp, back, side, top)
             │
             ▼
   P1 OCR & Extraction Pipeline (`p1_extractor.py`)
             │
             ▼
   P3 ExtractionPayload Validation (FastAPI / Pydantic)
             │
             ▼
   P2 RealComplianceEngine (`real_compliance_engine.py`)
             │
             ▼
   ComplianceResult (15 Rules + Dual Confidence + Conflicts)
             │
             ▼
   P3 Storage & REST API (`/api/...`)
             │
             ▼
   P4 Inspector UI (Dashboard, Review Workspace, Printable Certificates)
```

---

## 2. Complete Endpoint Reference Table

All endpoints are mounted under the `/api` prefix.

| Method | Path | Request Body | Response | Status Code | Description |
|---|---|---|---|---|---|
| `GET` | `/api/health` | None | `{ status, service, compliance_engine, environment }` | 200 | Service health check and telemetry |
| `GET` | `/api/dashboard/summary` | None | `DashboardSummaryResponse` | 200 | Aggregated KPI counts, top violated rules, recent queue |
| `GET` | `/api/inspections` | Query: `status`, `compliance_status`, `product`, `has_violations`, `skip`, `limit` | `InspectionListResponse` | 200 | Searchable, paginated audit list of inspections |
| `POST` | `/api/inspections` | `InspectionCreate` JSON | `InspectionResponse` | 201 | Initiates a new package inspection |
| `GET` | `/api/inspections/{id}` | None | `InspectionResponse` | 200 | Fetches details and lifecycle status of an inspection |
| `POST` | `/api/inspections/{id}/image` | Multipart: `file: UploadFile`, `image_type: Form(str)` | `ImageUploadResponse` | 201 | Uploads package surface image & updates coverage |
| `POST` | `/api/inspections/{id}/images` | Multipart: `file: UploadFile`, `image_type: Form(str)` | `ImageUploadResponse` | 201 | Plural alias for package image upload |
| `GET` | `/api/inspections/{id}/evidence` | None | `{ inspection_id, images[], rule_evidence[] }` | 200 | Retrieves all evidence images and optical findings |
| `GET` | `/api/inspections/{id}/images` | None | `{ inspection_id, images[], rule_evidence[] }` | 200 | Plural alias for evidence retrieval |
| `PATCH` | `/api/inspections/{id}/images/{ev_id}/surface` | `{ "surface": "front" \| "back" \| "side" \| "top" }` | `{ status, evidence_id, image_type }` | 200 | Assigns or updates package surface of an uploaded image |
| `POST` | `/api/inspections/{id}/images/{ev_id}/surface` | `{ "surface": "front" \| "back" \| "side" \| "top" }` | `{ status, evidence_id, image_type }` | 200 | POST alias for surface assignment |
| `PUT` | `/api/inspections/{id}/coverage` | `{ "coverage": { "front": bool, "back": bool, "side": bool, "top": bool } }` | `InspectionResponse` | 200 | Directly updates inspector surface coverage checklist |
| `POST` | `/api/inspections/{id}/extract` | None | `{ status, inspection_id, extraction_id, payload }` | 200 | Executes P1 OCR pipeline on uploaded images |
| `POST` | `/api/inspections/{id}/extraction` | `ExtractionPayload` JSON | `{ status, inspection_id, extraction_id }` | 200 | Manually submits or overrides P1 extraction JSON |
| `GET` | `/api/inspections/{id}/extraction` | None | `ExtractionPayload` JSON | 200 | Fetches stored P1 extraction declarations |
| `POST` | `/api/inspections/{id}/analyze` | None | `ComplianceResult` | 200 | Executes P2 `RealComplianceEngine` against extraction data |
| `GET` | `/api/inspections/{id}/result` | None | `ComplianceResult` | 200 | Retrieves stored compliance evaluation result |
| `GET` | `/api/inspections/{id}/rules/{rule_id}` | None | `RuleResult` JSON | 200 | Retrieves findings and evidence for a single rule ID |
| `GET` | `/api/inspections/{id}/result/rules/{rule_id}` | None | `RuleResult` JSON | 200 | Alias for single rule retrieval |
| `GET` | `/api/inspections/{id}/manual-review` | None | `{ inspection_id, unresolved_rules[], conflicts[] }` | 200 | Retrieves all items requiring manual review & conflicts |
| `GET` | `/api/inspections/{id}/review` | None | `{ inspection_id, unresolved_rules[], conflicts[] }` | 200 | Alias for manual review retrieval |
| `POST` | `/api/inspections/{id}/medical-device-confirmation` | `{ "is_confirmed_medical_device": bool }` | `ComplianceResult` | 200 | Submits inspector Fix 2 gate decision and re-evaluates |
| `POST` | `/api/inspections/{id}/notes` | `{ "notes": string }` | `InspectionResponse` | 200 | Updates inspector physical notes (e.g. caliper reading) |
| `GET` | `/api/reports/{id}` | None | Report JSON | 200 | Generates structured statutory compliance report |
| `GET` | `/api/reports/{id}/html` | None | HTML Document string | 200 | Generates printable compliance certificate |
| `GET` | `/api/inspections/{id}/report` | None | Report JSON | 200 | Convenience alias on inspection path |
| `GET` | `/api/inspections/{id}/report/html` | None | HTML Document string | 200 | Convenience alias for printable HTML certificate |
| `GET` | `/api/images/{file_name}` | None | Image Binary Stream | 200 | Serves stored evidence image file |

---

## 3. Core Request & Response Schemas

### 3.1 `ExtractionPayload` (P1 → P3 → P2 Contract)
Submitted to `POST /api/inspections/{id}/extraction` or emitted by `POST /api/inspections/{id}/extract`.

```json
{
  "inspection_id": "uuid-string",
  "product_name": {
    "value": "Parle-G Gold Glucose Biscuits",
    "raw_text": "Parle-G Gold Glucose Biscuits",
    "confidence": 0.98,
    "location": "front"
  },
  "commodity_category": {
    "value": "Biscuits",
    "raw_text": "Biscuits",
    "confidence": 0.99,
    "location": "front"
  },
  "country_of_origin": {
    "value": "India",
    "raw_text": "Country of Origin: India",
    "confidence": 0.99,
    "location": "back"
  },
  "is_importer_on_pdp": null,
  "manufacturer": {
    "premises": "Unit 4, Vile Parle East",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pin_code": "400057",
    "raw_text": "Mfg by: Parle Products, Vile Parle East, Mumbai, Maharashtra - 400057",
    "confidence": 0.96
  },
  "net_quantity": {
    "value": 100.0,
    "unit": "g",
    "raw_text": "Net Weight: 100 g",
    "confidence": 0.97,
    "surface_location": "front",
    "quiet_zone_clear": true
  },
  "net_quantity_observations": [
    {
      "value": 100.0,
      "unit": "g",
      "raw_text": "Net Weight: 100 g",
      "confidence": 0.97,
      "surface_location": "front",
      "image_id": "img_001"
    }
  ],
  "mrp": {
    "value": 30.0,
    "currency": "₹",
    "tax_inclusivity": true,
    "raw_text": "MRP ₹ 30.00 incl. of all taxes",
    "confidence": 0.96,
    "surface_location": "back",
    "is_sticker": false
  },
  "mrp_observations": [
    {
      "value": 30.0,
      "currency": "₹",
      "tax_inclusivity": true,
      "raw_text": "MRP ₹ 30.00 incl. of all taxes",
      "confidence": 0.96,
      "surface_location": "back",
      "image_id": "img_002"
    }
  ],
  "date_of_manufacture": {
    "month": "08",
    "year": "2026",
    "raw_text": "Mfg Date: 08/2026",
    "confidence": 0.95
  },
  "consumer_care": {
    "phone": "1800227788",
    "email": "care@parle.biz",
    "raw_text": "Customer Care: 1800227788, care@parle.biz",
    "confidence": 0.94
  },
  "medical_device_markers": null,
  "image_coverage": {
    "front": true,
    "back": true,
    "side": false,
    "top": false
  }
}
```

### 3.2 `ComplianceResult` (P2 → P3 → P4 Contract)
Emitted by `POST /api/inspections/{id}/analyze` and `GET /api/inspections/{id}/result`.

```json
{
  "inspection_id": "uuid-string",
  "overall_status": "COMPLIANT",
  "engine_version": "p2-real-v1.0.0",
  "evaluated_at": "2026-09-07T08:00:00Z",
  "summary_counts": {
    "total_rules": 15,
    "compliant": 10,
    "potential_violations": 0,
    "needs_manual_review": 2,
    "not_applicable": 3,
    "not_detected": 0,
    "analysis_failed": 0
  },
  "rule_results": [
    {
      "rule_id": "REQ-MVP-01",
      "status": "COMPLIANT",
      "detected_value": "All 5 mandatory declaration blocks detected",
      "normalized_value": "mandatory_presence=true",
      "detection_confidence": 0.96,
      "applicability_confidence": 1.0,
      "reason": "All five mandatory declarations are clearly declared on submitted panels.",
      "explanation_for_inspector": "All 5 mandatory declarations identified on packaging.",
      "conflicts": null,
      "rule_version": {
        "source": "01_Packaged_Commodities_Rules_2011.pdf",
        "clause": "Rule 6(1); exemption under Rule 26",
        "gsr_number": "G.S.R. 202(E) (Principal)",
        "verification_status": "VERIFIED — VERBATIM"
      }
    }
  ]
}
```

---

## 4. Inspection Lifecycle State Machine

```
   [ CREATED ]
        │
        ▼ (Upload surface images via POST /images)
   [ IMAGE_UPLOADED ]
        │
        ▼ (Execute extraction via POST /extract or submit via POST /extraction)
   [ EXTRACTION_RECEIVED ]
        │
        ▼ (Run RealComplianceEngine via POST /analyze)
   [ ANALYSIS_COMPLETE ]
        │
        ├───────────────────────────────┐
        ▼ (If overall_status != PENDING) ▼ (If manual review needed)
   [ REPORT_GENERATED ]           [ MANUAL_REVIEW_WORKSPACE ]
        │                               │
        │                               ▼ (Inspector confirms Fix 2 gate or caliper)
        │                         [ RE-EVALUATION ]
        ▼                               │
   PRINTABLE STATUTORY REPORT ◄─────────┘
```

---

## 5. Multi-Surface Semantics & Conflict Detection

Package surfaces are classified into four canonical panels:
- `front` / `pdp`: Principal Display Panel.
- `back`: Back panel.
- `side`: Left/right lateral panels.
- `top`: Top/bottom closures.

### Observation Preservation
When an inspection contains images of multiple surfaces, P1 extracts declarations per surface and records them in:
- `mrp_observations`: `List[MRPExtraction]`
- `net_quantity_observations`: `List[NetQuantityExtraction]`

### Conflict Escalation (Section 6)
If numeric values disagree across surfaces (e.g. ₹100 on front, ₹120 on back):
1. The backend **never** silently resolves the conflict or picks an arbitrary scalar.
2. `RealComplianceEngine` flags REQ-MVP-02 (MRP) or REQ-MVP-03 (Net Quantity) as `NEEDS_MANUAL_REVIEW`.
3. A `ConflictObject` is attached with all observations preserved side-by-side (`values_found`, `image_id`, `location`).

---

## 6. Medical Device Confirmation Workflow (Fix 2)

Under G.S.R. 778(E), certified medical devices are governed by the Medical Devices Rules, 2017 and exempt from standard PCR 2011 declarations. To prevent silent automated bypass:

1. **Detection**: If P1 detects medical device markers (e.g. `Mfg Lic MD-123`, `CDSCO`), the initial evaluation produces `NEEDS_MANUAL_REVIEW` on REQ-MVP-11.
2. **Three-State Persistence**:
   - `is_medical_device_confirmed = None`: Pending officer decision. REQ-MVP-11 remains `NEEDS_MANUAL_REVIEW`.
   - `is_medical_device_confirmed = True`: Explicit confirmation. REQ-MVP-11 produces `NOT_APPLICABLE`, standard PCR rules are suppressed, and overall status becomes `NOT_APPLICABLE`.
   - `is_medical_device_confirmed = False`: Explicit rejection. REQ-MVP-11 produces `COMPLIANT`, and product is evaluated under standard PCR 2011.
3. **API Action**: Submissions to `POST /api/inspections/{id}/medical-device-confirmation` persist the decision in `InspectionModel.is_medical_device_confirmed` and automatically re-evaluate compliance.

---

## 7. Dual Confidence & Visual-Aid-Only Rules

### 7.1 Separation of Confidences
- `detection_confidence`: Optical clarity / OCR recognition confidence (0.0 to 1.0).
- `applicability_confidence`: Statutory applicability confidence (0.0 to 1.0).
- **Prohibition**: Confidence scores are **never** presented as "% legally compliant".

### 7.2 Low Confidence De-escalation (Fix 1)
On REQ-MVP-02, if tax-inclusivity wording (`incl. of all taxes`) is found but `detection_confidence < 0.75`, the engine de-escalates to `NEEDS_MANUAL_REVIEW` rather than issuing a false `POTENTIAL_VIOLATION`.

### 7.3 Visual-Aid-Only Rules (REQ-MVP-14 & REQ-MVP-15)
- REQ-MVP-14 (Quiet Zone clearance) and REQ-MVP-15 (Contrast ratio) are qualitative visual aids.
- Under statutory principles, they **never** emit `COMPLIANT` or `POTENTIAL_VIOLATION`. They are schema-restricted to `NEEDS_MANUAL_REVIEW` or `NOT_DETECTED`.

---

## 8. Error and Failure Contract

Technical failures are never represented as legal violations:

| Scenario | HTTP Status | Response Shape | Remedial Action |
|---|---|---|---|
| Unknown inspection ID | 404 | `{ "detail": "Inspection '...' not found." }` | Verify inspection UUID |
| Missing extraction & images on analyze | 400 | `{ "detail": "Cannot analyze inspection: no extraction data or images." }` | Upload images or submit extraction payload |
| Malformed payload / Schema mismatch | 422 | `{ "detail": "Extraction Schema Validation Failure", "errors": [...] }` | Correct field types/constraints |
| Unknown rule ID on single rule retrieval | 404 | `{ "detail": "Rule '...' not found in compliance results." }` | Verify rule ID (e.g. `REQ-MVP-01`) |
| Image file exceeds 10MB | 400 | `{ "detail": "File size exceeds limit." }` | Compress image before upload |
| Unsupported file extension | 400 | `{ "detail": "Unsupported file format." }` | Use JPEG, PNG, WEBP, or BMP |

---

## 9. Deployment Configuration & Environment Variables

| Variable | Default | Purpose | Production Setting |
|---|---|---|---|
| `APP_ENV` | `development` | Deployment environment tier | `production` |
| `COMPLIANCE_ENGINE_TYPE` | `real` | Production rule engine (`real` or `mock`) | Must be `real` |
| `DATABASE_URL` | `sqlite:///sih26034.db` | SQLAlchemy database connection URI | PostgreSQL URI (e.g. `postgresql://...`) |
| `UPLOAD_DIR` | `uploads/` | Physical image storage directory | Persistent volume mount path |
| `MAX_FILE_SIZE_BYTES` | `10485760` (10MB) | Max uploaded image size limit | Configure per infrastructure limits |
| `ALLOWED_ORIGINS` | `http://localhost:3000,...` | Comma-separated CORS allowed origins | Deployed frontend origin (e.g. `https://sih.gov.in`) |
| `PORT` | `8000` | HTTP listening port | `8000` or port assigned by cloud host |
| `HOST` | `0.0.0.0` | HTTP binding interface | `0.0.0.0` |

> [!CAUTION]
> In production environments with authentication or credentials, wildcard `allow_origins=["*"]` is strictly prohibited. Specify explicit frontend origins in `ALLOWED_ORIGINS`.

---

## 10. Frontend Integration Verification Matrix

| Frontend API Call (`api.js`) | Backend Endpoint | Status | Verified |
|---|---|---|---|
| `apiService.checkBackendHealth()` | `GET /api/health` | Matching | ✓ PASS |
| `apiService.getDashboardSummary()` | `GET /api/dashboard/summary` | Matching | ✓ PASS |
| `apiService.listInspections(query)` | `GET /api/inspections` | Matching | ✓ PASS |
| `apiService.getInspection(id)` | `GET /api/inspections/{id}` | Matching | ✓ PASS |
| `apiService.createInspection(payload)` | `POST /api/inspections` | Matching | ✓ PASS |
| `apiService.uploadInspectionImage(id, file, type)` | `POST /api/inspections/{id}/image` & `/images` | Matching | ✓ PASS |
| `apiService.getEvidence(id)` | `GET /api/inspections/{id}/evidence` & `/images` | Matching | ✓ PASS |
| `apiService.getExtraction(id)` | `GET /api/inspections/{id}/extraction` | Matching | ✓ PASS |
| `apiService.submitExtraction(id, payload)` | `POST /api/inspections/{id}/extraction` | Matching | ✓ PASS |
| `apiService.analyzeInspection(id)` | `POST /api/inspections/{id}/analyze` | Matching | ✓ PASS |
| `apiService.getComplianceResult(id)` | `GET /api/inspections/{id}/result` | Matching | ✓ PASS |
| `apiService.confirmMedicalDevice(id, bool)` | `POST /api/inspections/{id}/medical-device-confirmation` | Matching | ✓ PASS |
| `apiService.updateNotes(id, notes)` | `POST /api/inspections/{id}/notes` | Matching | ✓ PASS |
| `apiService.getReportData(id)` | `GET /api/reports/{id}` & `/inspections/{id}/report` | Matching | ✓ PASS |
| `apiService.getReportHtml(id)` | `GET /api/reports/{id}/html` & `/inspections/{id}/report/html` | Matching | ✓ PASS |
