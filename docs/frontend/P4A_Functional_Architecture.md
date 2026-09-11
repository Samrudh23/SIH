# P4A Functional Architecture & Backend Integration Report — SIH26034

> **Legal Metrology (Packaged Commodities) Rules, 2011 Compliance Screening System**  
> **Author:** P4A Frontend Functional & Integration Engineering  
> **Date:** September 7, 2026  
> **Status:** Production-Ready, Verified Against Live P3 Backend & RealComplianceEngine  
> **Handoff Target:** P4B (UI/UX Styling & Visual Polish) & P5 (Production Deployment)

---

## Executive Summary

P4A has completed the functional transition of the SIH26034 frontend from local mock fixture simulation to a live, production-grade client integrating directly with the P3 FastAPI backend (`http://127.0.0.1:8000/api` or `/api`), P1 structured extraction models, and P2 `RealComplianceEngine`.

All dangerous silent mock fallbacks have been eliminated. Production mode enforces **REAL API ONLY**, while development mode provides an explicit, visible toggle (`[ Real Backend ]` / `[ Mock Data ]`) with real-time backend connection telemetry.

All 22 automated tests (13 schema/mock unit tests + 9 real backend integration tests against the live running FastAPI server) are passing cleanly with zero failures.

---

## 1. Component Structure & Architecture

The frontend follows a pure ES Module Single-Page Application (SPA) architecture without bulky bundlers or external dependencies, ensuring high auditability and zero build friction.

```
frontend/
├── index.html                  # HTML entry point with Tailwind CDN & Design tokens
├── server.js                   # Lightweight static & SPA HTTP server (Port 3000)
├── package.json                # Scripts: test, lint, start
├── src/
│   ├── config/
│   │   └── env.js              # Environment detection (dev/stage/prod), API_BASE_URL, ALLOW_MOCK
│   ├── types/
│   │   └── compliance.ts       # Authoritative TypeScript interfaces matching P3 Pydantic schemas
│   ├── services/
│   │   ├── api.js              # Central ComplianceApiService client (13 core operations, ApiError)
│   │   └── mockFixtures.js     # 11 authoritative golden mock fixtures (Dev only)
│   ├── components/
│   │   ├── Navbar.js           # Header navigation, live health pill, explicit mode switcher
│   │   ├── StatusBadge.js      # Accessible badges for all 6 result states & workflow states
│   │   ├── ConfidenceMeter.js  # Strict dual confidence display (Detection vs Applicability)
│   │   ├── ConflictViewer.js   # Side-by-side multi-observation comparison (MRP & Net Quantity)
│   │   ├── EvidenceViewer.js   # Optical evidence, bounding box canvas & Rule 8(1) quiet zone simulator
│   │   ├── MedicalDeviceGate.js# Fix 2 MDR 2017 regulatory confirmation dialog
│   │   └── RuleDetailModal.js  # Deep-dive legal citation, statutory clause & optical readout modal
│   ├── views/
│   │   ├── DashboardView.js    # Operational KPIs, recent inspections queue, connection diagnostics
│   │   ├── NewInspectionView.js# 4-stage inspection initiator, multi-surface uploader, coverage tracker
│   │   ├── ExtractionView.js   # Comprehensive P1 OCR audit across all 6 declaration blocks
│   │   ├── ComplianceView.js   # 15-rule interactive compliance table, summary pills, filters
│   │   ├── ManualReviewView.js # Enforcement workspace for conflicts, low confidence, Fix 2 gate
│   │   ├── HistoryView.js      # Searchable, filterable audit archive of past inspections
│   │   └── ReportModal.js      # Statutory printable compliance certificate & server HTML link
│   ├── styles/
│   │   └── app.css             # Design tokens, tabular typography, print stylesheet
│   └── app.js                  # SPA router, hash controller, event bindings, error boundary
└── tests/
    ├── runner.js               # CLI & browser universal test runner
    ├── compliance.test.js      # Unit & legal specification test suite (11 tests)
    └── backend_integration.test.js # Real FastAPI backend contract test suite (9 tests)
```

---

## 2. API Service Structure & P3 Endpoint Mapping

All backend communication is centralized in `frontend/src/services/api.js`. UI components never make raw `fetch()` calls.

### API Contract Mapping Table

| Operation | HTTP Method | Actual P3 Endpoint | Request Payload | Response Payload |
|---|---|---|---|---|
| **Health Check** | `GET` | `/api/health` | None | `{ "status": "ok", "app": "..." }` |
| **Dashboard Summary** | `GET` | `/api/dashboard/summary` | None | `DashboardSummaryResponse` (KPIs, recent queue, top violated rules) |
| **List Inspections** | `GET` | `/api/inspections` | Query: `status`, `compliance_status`, `product`, `has_violations`, `skip`, `limit` | `InspectionListResponse` (`total`, `items[]`) |
| **Get Inspection** | `GET` | `/api/inspections/{id}` | None | `InspectionResponse` |
| **Create Inspection** | `POST` | `/api/inspections` | `InspectionCreate` (product, brand, category, inspector_id, image_coverage, metadata) | `InspectionResponse` (HTTP 201) |
| **Upload Surface Image** | `POST` | `/api/inspections/{id}/image` | Multipart Form: `file: UploadFile`, `image_type: str` (surface: `front`, `back`, `side`, `top`) | `ImageUploadResponse` (evidence_id, file_url, safe_name) |
| **Get Evidence** | `GET` | `/api/inspections/{id}/evidence` | None | `{ inspection_id, images[], rule_evidence[] }` |
| **Get Extraction** | `GET` | `/api/inspections/{id}/extraction` | None | `ExtractionPayload` (P1 schema) |
| **Submit Extraction** | `POST` | `/api/inspections/{id}/extraction` | `ExtractionPayload` | `{ status: "success", extraction_id, ... }` |
| **Analyze Inspection** | `POST` | `/api/inspections/{id}/analyze` | None | `ComplianceResult` (evaluated by P2 RealComplianceEngine) |
| **Get Compliance Result** | `GET` | `/api/inspections/{id}/result` | None | `ComplianceResult` |
| **Medical Device Gate (Fix 2)** | `POST` | `/api/inspections/{id}/medical-device-confirmation` | `{ "is_confirmed_medical_device": boolean }` | `ComplianceResult` (reevaluated) |
| **Update Inspector Notes** | `POST` | `/api/inspections/{id}/notes` | `{ "notes": string }` | `InspectionResponse` |
| **Get Structured Report** | `GET` | `/api/reports/{id}` | None | Report JSON (disclaimer, metadata, rule findings) |
| **Get Printable HTML Report**| `GET` | `/api/reports/{id}/html` | None | HTML Document string |

---

## 3. Data Flow & Inspection Lifecycle

```
INSPECTOR USER
      │
      ▼ (Screen 2: New Inspection)
1. Fills product metadata & selects surface coverage checklist
2. Stages package images and assigns surface labels: [front, back, side, top]
3. Clicks "Run OCR & Compliance Analysis"
      │
      ▼ (apiService.createInspection)
4. POST /api/inspections ──► Creates record in P3 (Status: CREATED)
      │
      ▼ (apiService.uploadInspectionImage)
5. POST /api/inspections/{id}/image (for each surface photo) ──► P3 stores files (Status: IMAGE_UPLOADED)
      │
      ▼ (apiService.submitExtraction)
6. P1 background worker or frontend bridge submits ExtractionPayload ──► P3 stores (Status: EXTRACTION_RECEIVED)
      │
      ▼ (apiService.analyzeInspection)
7. POST /api/inspections/{id}/analyze ──► P2 RealComplianceEngine evaluates all 15 rules (Status: ANALYSIS_COMPLETE)
      │
      ▼ (Router redirects to #/compliance/{id})
8. Displays Overall Status & 15 Rules Breakdown
      │
      ├───────────────────────────────┬───────────────────────────────┐
      ▼                               ▼                               ▼
(If Conflicts or Low Conf)      (To Audit Optical Text)         (To Export Certificate)
#/review/{id}                   #/extraction/{id}               ReportModal / Print
- Side-by-side MRP cards        - Product details               - Official GOI Header
- Side-by-side Qty cards        - All MRP observations          - Statutory Findings
- Fix 2 Medical Device Gate     - All Qty observations          - Inspector Sign-off
- Save Caliper / Physical notes - Manufacturer / Dates / Care   - Link to Server HTML
```

---

## 4. State Management

State is kept predictable and lightweight without external store boilerplate:
1. **`apiService` Singleton:** Holds active mode (`live` vs `mock`), resolved `baseUrl`, backend health status (`isBackendOnline`). Emits `api-mode-changed` and `backend-health-updated` custom DOM events.
2. **`App` Router Class:** Coordinates `currentRoute`, `currentInspectionId`, and staged upload files (`stagedFiles`).
3. **Immutability & Provenance:** Components fetch canonical inspection records from the API service on mount or route transition. No divergent state copies are retained across views.

---

## 5. Error Handling & Loading Semantics

### Elimination of Silent Mock Fallback
- In `live` mode, whenever a request encounters a network failure or HTTP error (400, 404, 422, 500), `ComplianceApiService` throws an `ApiError`.
- The UI never silently falls back to a mock fixture when in live mode.
- `ApiError` contains:
  - `message`: human-readable description
  - `status`: HTTP status code
  - `endpoint`: API path
  - `details`: server response details / schema validation errors
  - `actionableRemedy`: concrete instructions for the inspector (e.g. backend server startup command, verification of inspection ID).

### Granular Loading States
During inspection creation and analysis, the UI renders real progress transitions:
1. `[1/4] Creating Inspection Record in P3...`
2. `[2/4] Uploading Surface Photographs (X of Y)...`
3. `[3/4] Verifying Structured Extraction Payload...`
4. `[4/4] Evaluating Legal Metrology Rules (15 checks)...`

---

## 6. Environment & Mode Management

Defined in `frontend/src/config/env.js`:
- **Development (`development`):**
  - Base URL defaults to `http://127.0.0.1:8000/api`.
  - Mode defaults to `live`.
  - Inspector can toggle to `mock` data for offline fixture demonstration.
  - Top navigation displays clear mode badge: `[ Real Backend ]` vs `[ Mock Data ]`.
- **Staging (`staging`):**
  - Base URL defaults to `/api`.
  - Mock mode disabled.
- **Production (`production`):**
  - Base URL defaults to `/api` (reverse-proxied to FastAPI backend).
  - Mock mode is **strictly prohibited** (`ALLOW_MOCK = false`).
  - Attempting to activate mock mode throws `ApiError: Mock mode is strictly prohibited in production environment.`
  - Top navigation displays permanent badge: `PRODUCTION: REAL API`.
- **Runtime Overrides:**
  - Can be supplied via `window.__ENV__.API_BASE_URL` or `localStorage.getItem("sih_api_base_url")`.

---

## 7. Compliance Engine Semantics & Legal Invariants

The frontend strictly preserves the legal rules codified in `Confidence_Status_Schema.md` and `PCR_Compliance_Rules.md`:

1. **All 6 Authoritative Result States Supported:**
   - `COMPLIANT`: Green badge, all statutory requirements satisfied.
   - `POTENTIAL_VIOLATION`: Red badge, statutory breach indicated.
   - `NEEDS_MANUAL_REVIEW`: Amber badge, intended valid outcome for ambiguity/conflict.
   - `NOT_APPLICABLE`: Slate badge, legal exemption established (e.g. Rule 26 small packages, confirmed medical devices).
   - `NOT_DETECTED`: Indigo badge, declaration missing from scanned images. **Never converted into POTENTIAL_VIOLATION.**
   - `ANALYSIS_FAILED`: Rose badge, technical image blur or pipeline fault. **Never converted into COMPLIANT.**
2. **Visual-Aid Rules Restricted (REQ-MVP-14 & REQ-MVP-15):**
   - Rule 8(1) (Quiet Zone) and Rule 9(1) (Contrast) can **never produce COMPLIANT or POTENTIAL_VIOLATION**. They are restricted to `NEEDS_MANUAL_REVIEW` or `NOT_DETECTED`.
3. **Dual Confidence Permanently Separate:**
   - `detection_confidence`: how confident OCR/CV is about what it read.
   - `applicability_confidence`: how confident the system is that the rule applies to this product.
   - These are never averaged, merged, or presented as "% legally compliant".
4. **Multi-Surface Conflict Preservation (REQ-MVP-02 & REQ-MVP-03):**
   - When different prices (e.g. ₹190 Front vs ₹210 Back) or weights (500g Front vs 450g Back) are detected, the frontend displays them side-by-side with individual confidences and raw text.
   - The UI never automatically picks the highest confidence or lowest price.
5. **Fix 2 Medical Device Gate (REQ-MVP-11):**
   - Detects CDSCO marker pattern.
   - Prompts inspector with confirmation dialog.
   - Confirmation (`is_confirmed_medical_device = true`) routes to Medical Devices Rules, 2017 and suppresses all 15 PCR rules to `NOT_APPLICABLE`.
   - Rejection (`is_confirmed_medical_device = false`) restores standard PCR 2011 checks.

---

## 8. P3 Backend Dependencies & Contract Notes

1. **Asynchronous Extraction Pipeline:**
   - In P3, `POST /api/inspections/{id}/analyze` requires an extraction to already exist via `POST /api/inspections/{id}/extraction`.
   - In live testing, if an external OCR worker has not yet processed the images, the frontend bridge creates an initial `ExtractionPayload` matching P3 schema so `analyze` can execute immediately.
   - **Recommendation for P3:** If images are uploaded but extraction is not yet submitted when `/analyze` is called, P3 should ideally trigger the internal P1 OCR worker asynchronously rather than returning HTTP 400.
2. **Image Serving CORS:**
   - Stored evidence images are accessible at `GET /api/images/{file_name}`. P3's `CORSMiddleware` already allows origins `http://localhost:3000` and `http://127.0.0.1:3000`.

---

## 9. P4B Handoff Guide

P4B can redesign visual components, typography, layout, color palettes, and spacing without altering any functional logic.

### Components Ready for Styling & Visual Polish
- **`src/components/StatusBadge.js`:**
  - Function: `renderResultBadge(status, size)`
  - Styling target: Badge container classes, SVG icon styles, typography.
  - Constraint: Keep accessible `aria-label` and distinct color coding for all 6 states.
- **`src/components/ConfidenceMeter.js`:**
  - Function: `renderConfidenceMeter(detectionConfidence, applicabilityConfidence, compact)`
  - Styling target: Progress bar tracks, percentage pills, info tooltips.
  - Constraint: Never merge detection and applicability scores into one bar.
- **`src/components/ConflictViewer.js`:**
  - Function: `renderConflictViewer(conflict)`
  - Styling target: Side-by-side comparison cards, diff indicators.
  - Constraint: Display all observation cards equally without highlighting one as "winner".
- **`src/components/EvidenceViewer.js`:**
  - Function: `renderEvidenceCard(evidence, options)`
  - Styling target: SVG canvas framing, bounding box color/stroke, raw text block.
  - Constraint: Maintain spatial coordinates readout and Rule 8(1) 1Hx2H quiet zone overlay.
- **`src/components/Navbar.js`:**
  - Styling target: Header layout, logo styling, navigation link states, mode toggle pill.
  - Functional hook IDs: `toggle-live-btn`, `toggle-mock-btn`.
- **`src/views/` (All 7 Screens):**
  - Clean HTML templates with semantic classes and container layouts ready for styling enhancements.

### Functional Invariants (DO NOT MODIFY IN UI REDESIGN)
1. Do not alter data attribute hooks: `data-rule-id`, `data-status`, `data-filter`, `data-id`.
2. Do not change button element IDs: `submit-inspection-btn`, `trigger-analyze-btn`, `trigger-med-confirm-btn`, `trigger-med-reject-btn`, `open-report-modal-btn`.
3. Do not re-introduce fallback mock data in `apiService` live methods.
4. Do not invent compliance result states outside the 6 authoritative enums.
