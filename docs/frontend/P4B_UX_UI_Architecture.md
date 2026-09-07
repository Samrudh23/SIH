# P4B UX/UI Architecture Specification — SIH26034

> **Legal Metrology (Packaged Commodities) Rules, 2011 Compliance Screening System**  
> **Author:** P4B Frontend UX/UI & Visual Design Engineering  
> **Date:** September 7, 2026  
> **Status:** Specification & Architecture Baseline (Revised)  
> **Target:** Professional Regulatory Inspection Workstation

---

## 1. Executive Summary & Design Principles

P4B builds upon the verified, production-ready functional architecture delivered in P4A (commit `365fd76`). P4A integrated the frontend with the live P3 FastAPI backend, P1 structured extractions, and P2 `RealComplianceEngine`.

The mandate of P4B is to transform the functional frontend into a **distinguished, restrained, trustworthy, and accessible regulatory inspection workstation** benchmarking against premier enterprise, regulatory, and audit interfaces (such as Refero benchmarks for compliance, audit, and legal workflows).

### 1.1 Design Priority Stack
All design and implementation decisions strictly follow this priority hierarchy:
1. **UX clarity:** The inspector's immediate comprehension of product status, evidence, and required actions.
2. **Information hierarchy:** Clear spatial grouping, prominent primary metrics, and structured secondary details.
3. **Functional correctness:** Zero regressions in P1 extraction handling, P2 compliance logic, or API contracts.
4. **Accessibility (WCAG 2.1 AA/AAA):** Universal keyboard operability, visible focus rings, ARIA dialog roles, and screen-reader readiness.
5. **Responsive behaviour:** High usability across desktop workstations, field laptops, tablets, and mobile screens.
6. **Visual consistency:** Cohesive typography, spacing, surface borders, and component tokens throughout.
7. **Professional visual polish:** Restrained, authoritative enterprise aesthetics without generic SaaS fluff.
8. **Motion polish:** Subtlety, purposeful state feedback, continuity; strictly non-decorative and respects `prefers-reduced-motion`.

> [!CAUTION]
> Never sacrifice a higher-priority item for a lower-priority visual effect.

---

## 2. Refero → SIH26034 Design Translation Mapping

Refero interface references serve as the **first-class visual benchmark** for this application. Rather than copying any single interface, P4B analyzes professional patterns across enterprise compliance dashboards, data tables, regulatory inspection forms, and audit logs, translating them directly into SIH26034:

| Design Dimension | Refero Enterprise / Regulatory Benchmark Pattern | SIH26034 Concrete Implementation |
|---|---|---|
| **1. Page Composition** | Clean structured header; breadcrumb / workflow contextual strip; primary metric row; split view for analytical tables and contextual side-panels. | Top bar with live system status; 5-stage workflow stepper strip; 6-state metric summary strip; full-width high-density rule table with slide-over detail modals. |
| **2. Typography** | Strict dual-type hierarchy: neutral clean sans-serif for UI labels paired with fixed-pitch tabular monospace for all audit data. | Sans-serif UI stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto`); tabular numbers (`ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas`) for rule IDs, prices, net weights, timestamps, and coordinates. |
| **3. Spacing & Rhythm** | Compact 4px base grid (space-1 = 4px, space-2 = 8px, space-3 = 12px, space-4 = 16px, space-6 = 24px) with predictable visual groupings. | Uniform compact padding (`p-4` to `p-5` for cards, `py-2.5` to `py-3` for table rows) ensuring high information density without visual crowding. |
| **4. Navigation** | Persistent top shell with clear environment telemetry; secondary horizontal workflow breadcrumbs; responsive slide-out mobile drawer. | Fixed top bar with P3 health telemetry and live/mock toggle; 5-stage horizontal stepper (`01 Evidence` &rarr; `02 Extraction` &rarr; `03 Compliance` &rarr; `04 Review` &rarr; `05 Report`); responsive mobile menu. |
| **5. Information Density** | Data-dense without feeling noisy; critical screening signals prominent; secondary audit details accessible via progressive disclosure. | Screening verdict badge and rule summary pills visible at glance; deep statutory citations, spatial bounding boxes, and raw OCR strings in slide-over modals. |
| **6. Tables** | Flat border-bottom rows; clear column headers with alignment by data type (text left, numbers/IDs mono, actions right); row hover feedback; keyboard focus rings. | 15-rule compliance table with sticky header; row hover styling; full keyboard row activation (`Enter`/`Space`); tabular numeric alignment. Responsive card-stack fallback on mobile. |
| **7. Forms** | Explicit fieldsets; clear label/input proximity; dedicated helper/error text; structured multi-surface drag-and-drop dropzones. | Inspection initiator with Section 5 coverage checklist; multi-surface image dropzone with surface selector tags (`Front`, `Back`, `Side`, `Top`); validation banners. |
| **8. Detail Views** | Structured drawer/modal with tabbed navigation: Summary, Statutory Citations, Optical Evidence, Audit Trail. | `RuleDetailModal` featuring authoritative legal citations, dual confidence meters, optical bounding box SVG canvas, and engine audit log. |
| **9. Status Presentation** | Multi-attribute status tokens combining background tint, high-contrast solid border, saturated text, and semantic SVG icon. Never color alone. | All 6 authoritative compliance states (`COMPLIANT`, `POTENTIAL_VIOLATION`, `NEEDS_MANUAL_REVIEW`, `NOT_APPLICABLE`, `NOT_DETECTED`, `ANALYSIS_FAILED`) styled with distinct icon + text + border tokens. |
| **10. Dashboards** | Balanced operational overview: KPI counter cards with state-coded indicators, distribution bars for common infractions, and recent activity queue. | 6-card KPI grid; Top Flagged Rules analytics card with proportional distribution meters; recent inspection queue with instant inspection links. |
| **11. Responsive Behaviour** | Graceful degradation from multi-column desktop workstation to single-column field tablet/mobile without hiding core data. | Tables collapse to mobile card stacks; KPI grid wraps from 6-col to 3-col to 2-col; full-screen touch-friendly modal drawers on viewports < 768px. |
| **12. Visual Hierarchy** | High-contrast neutral canvases (`#f8fafc` background, `#ffffff` card containers, `#e2e8f0` borders) allowing status badges to command visual focus. | Slate-900 typography on pure white cards with crisp 1px borders; zero heavy dropshadows or gradient cards; badges and conflict alerts act as focal points. |
| **13. Component Consistency** | Standardized button variants (Primary Solid, Secondary Outline, Destructive, Ghost) and uniform dialog backdrops (`bg-slate-900/60` blur). | Unified button tokens; standardized card radius (`rounded-xl`); consistent dialog backdrop with focus trapping and `Escape` dismissals. |

---

## 3. Brand Identity & Regulatory Tone (Zero Fabricated Assets)

> [!IMPORTANT]
> **Strict Policy on Official Seals & Government Marks:**
> - P4B will **NOT fabricate or generate** fake national emblems, government seals, ministry logos, or certification marks.
> - The application must look appropriate for government/regulatory use through **rigorous typography, authoritative hierarchy, disciplined color palettes, and precise legal structure**, without falsely presenting itself as an officially issued government system.
> - Official branding is used **only** when an authoritative project-provided asset exists in the repository.
> - The same restriction applies to inspection reports and certificates: they utilize clean, restrained administrative formatting with placeholder verification spaces, without counterfeit insignia.

---

## 4. Legal Metrology Content & Invariants

> [!IMPORTANT]
> **Statutory Documentation is Authoritative:**
> - P4B must **NOT independently interpret, reword, or invent** statutory requirements.
> - P2 and the existing legal documentation (`PCR_Compliance_Rules.md`, `Confidence_Status_Schema.md`, `RULE_METADATA`) remain authoritative.
> - All statutory clause numbers, source document citations, G.S.R. gazette notifications, and inspector explanations displayed in the UI are strictly derived from authoritative project schemas.
> - P4B improves visual hierarchy, readability, grouping, and scannability, but never alters statutory semantics.

### 4.1 The Six Authoritative Compliance Result States
| State | Visual Treatment | Icon | Legal Meaning |
|---|---|---|---|
| `COMPLIANT` | Green (`#065f46`, bg: `#ecfdf5`, border: `#a7f3d0`) | Checkmark | Statutory requirement fully satisfied with sufficient evidence. |
| `POTENTIAL_VIOLATION` | Red (`#991b1b`, bg: `#fef2f2`, border: `#fecaca`) | X Mark | Clear statutory breach detected. Actionable non-compliance. |
| `NEEDS_MANUAL_REVIEW` | Amber (`#92400e`, bg: `#fffbeb`, border: `#fde68a`) | Alert Triangle | Ambiguity, multi-surface conflict, low OCR confidence, or physical verification needed. |
| `NOT_APPLICABLE` | Slate (`#334155`, bg: `#f1f5f9`, border: `#cbd5e1`) | Prohibited Slash | Statutory exemption established (e.g. Rule 26 small packs, confirmed medical device). |
| `NOT_DETECTED` | Indigo (`#3730a3`, bg: `#eef2ff`, border: `#c7d2fe`) | Magnifying Glass | Declaration missing on scanned panels. **Never converted to violation.** |
| `ANALYSIS_FAILED` | Rose (`#9f1239`, bg: `#fff1f2`, border: `#fecdd3`) | Octagon Alert | Technical image fault (blur/occlusion). **No legal determination made.** |

---

## 5. Inspector Workflow Architecture

The application workflow mirrors the physical inspection process:

```
01 Evidence          ──►  02 Extraction        ──►  03 Compliance        ──►  04 Manual Review     ──►  05 Statutory Report
(#/new)                   (#/extraction/:id)        (#/compliance/:id)        (#/review/:id)            (ReportModal)
Upload container          Verify OCR readings       15-rule statutory         Resolve conflicts,        Official compliance
photos & coverage         across 6 blocks           screening & metrics       CDSCO gate & notes        certificate & print
```

### Every major screen answers:
1. **WHERE AM I?** (Persistent 5-stage Workflow Stepper indicates active stage and status).
2. **WHAT DID THE SYSTEM FIND?** (Prominent overall badge, clear findings, dual confidence telemetry).
3. **WHAT DO I NEED TO DO NEXT?** (Clear primary action: e.g. "Review 2 Conflicts", "Inspect Extraction", "Export Certificate").

---

## 6. Motion & Interaction Policy

### 6.1 Dependency Decision: `MOTION.DEV = OPTIONAL / EVALUATE DURING IMPLEMENTATION`
- The baseline implementation will utilize clean, accessible **native CSS transitions and keyframes**.
- During **Checkpoint G (Motion/Interactions)**, each interactive component will be evaluated to determine whether Motion.dev provides genuine interaction quality (e.g. complex layout animations, orchestrated evidence switching, drag physics) that justifies introducing the dependency.
- If native CSS achieves the required interaction with superior performance and zero runtime bloat, native CSS will be retained.
- Motion is strictly prohibited from being used for decorative effects (no bouncing cards, no parallax, no particle effects).
- All motion must strictly respect:
  ```css
  @media (prefers-reduced-motion: reduce) {
    *, ::before, ::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }
  }
  ```

---

## 7. Component Architecture: Reuse vs Refactor

| Component | Target File | Architecture Role & Refinements |
|---|---|---|
| **Navbar** | `src/components/Navbar.js` | Professional header with system title, PCR 2011 badge, live P3 health pill, mode toggles, and responsive mobile drawer. |
| **WorkflowStepper** | `src/components/WorkflowStepper.js` *(NEW)* | Reusable 5-stage progression stepper across all inspection views answering "Where am I?". |
| **StatusBadge** | `src/components/StatusBadge.js` | WCAG AAA contrast badges for all 6 result states + workflow states with semantic icons. |
| **ConfidenceMeter** | `src/components/ConfidenceMeter.js` | Strict separation of OCR Detection Confidence vs Rule Applicability Confidence. |
| **ConflictViewer** | `src/components/ConflictViewer.js` | Equal-weight side-by-side surface comparison cards displaying raw OCR and confidence without picking a winner. |
| **EvidenceViewer** | `src/components/EvidenceViewer.js` | Optical evidence canvas with Rule 8(1) 1Hx2H quiet zone overlay simulator and raw text selection. |
| **MedicalDeviceGate** | `src/components/MedicalDeviceGate.js` | Fix 2 regulatory confirmation dialog under G.S.R. 778(E) with keyboard focus management. |
| **RuleDetailModal** | `src/components/RuleDetailModal.js` | Deep-dive dialog with statutory citations, detected vs expected, evidence canvas, and focus trapping. |
| **ReportModal** | `src/views/ReportModal.js` | Clean statutory compliance certificate with official formatting, seal placeholder, and print stylesheet. |

---

## 8. Functional Hooks & Invariants Preserved

All existing functional hooks and selectors must remain intact:
- `#submit-inspection-btn`
- `#trigger-analyze-btn`
- `#trigger-med-confirm-btn`
- `#trigger-med-reject-btn`
- `#open-report-modal-btn`
- `#close-report-modal`, `#print-report-btn`, `#report-modal-backdrop`
- `#close-rule-modal`, `#close-rule-modal-btn`, `#rule-detail-modal`
- `#toggle-live-btn`, `#toggle-mock-btn`
- `#drop-zone`, `#file-input`, `#new-inspection-form`
- `#product_name`, `#brand_name`, `#commodity_category`, `#inspector_id`
- `#cov_front`, `#cov_back`, `#cov_side`, `#cov_top`
- `#inspector-notes-form`, `#inspector-notes-input`, `#notes-status-msg`, `#save-notes-btn`
- `#history-filter-form`, `#history-search`, `#history-status-filter`, `#history-workflow-filter`, `#reset-history-filter`
- `#quick-fixture-select`
- Attributes: `data-rule-id`, `data-status`, `data-filter`, `data-id`, `data-idx`
- Classes: `.rule-row`, `.rule-filter-btn`, `.rule-filter-btn.active`, `.surface-picker`, `.remove-staged-btn`

---

## 9. Staged Implementation Checkpoints

To ensure controlled, verifiable delivery without functional regression:

- **CHECKPOINT A:** UX architecture + Refero analysis + design system proposal *(Current)*
- **CHECKPOINT B:** App shell + navigation + workflow stepper
- **CHECKPOINT C:** Evidence + Extraction views
- **CHECKPOINT D:** Compliance + Manual Review views
- **CHECKPOINT E:** History archive + Report modal
- **CHECKPOINT F:** Responsive layouts + accessibility refinement
- **CHECKPOINT G:** Motion / interaction evaluation (evaluating Motion.dev vs native CSS)
- **CHECKPOINT H:** Full regression verification (13 frontend tests + 104 backend tests)
