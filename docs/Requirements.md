
## 1. Purpose

This document converts the SIH26034 problem statement into a structured set of software requirements.

Requirements are categorized by:

- Functional requirements
    
- Non-functional requirements
    
- AI/OCR requirements
    
- Compliance requirements
    
- Evidence requirements
    
- Reporting requirements
    
- Security requirements
    
- Phase 1 / Phase 2 scope
    

Each requirement should eventually have an implementation status and owner.

---

# 2. Priority Definitions

|Priority|Meaning|
|---|---|
|**MUST**|Required for the Phase 1 prototype|
|**SHOULD**|Important if technically feasible|
|**COULD**|Useful enhancement|
|**PHASE 2**|Primarily intended for national-stage development|

---

# 3. Core Functional Requirements

## FR-01 — Product Image Upload

**Priority:** MUST  
**Phase:** 1

The system shall allow an inspector to upload an image of a packaged commodity for analysis.

### Acceptance criteria

- User can select an image.
    
- Supported image types are validated.
    
- Invalid files are rejected gracefully.
    
- Upload progress/status is communicated.
    
- The uploaded image is associated with an inspection.
    

---

## FR-02 — Multiple Image Support

**Priority:** SHOULD  
**Phase:** 1

The system should allow multiple images of the same product where required.

Examples:

- Front label
    
- Back label
    
- Side panel
    
- Top/bottom
    
- Additional evidence
    

---

## FR-03 — Image Quality Assessment

**Priority:** SHOULD  
**Phase:** 1

The system should identify images that may be unsuitable for reliable analysis.

Potential conditions:

- Excessive blur
    
- Very low resolution
    
- Poor lighting
    
- Severe obstruction
    
- Extreme perspective
    
- Insufficient visible text
    

The system should warn the user rather than silently producing unreliable results.

---

## FR-04 — Image Preprocessing

**Priority:** MUST  
**Phase:** 1

The analysis pipeline shall support appropriate preprocessing before OCR/CV analysis where required.

Potential operations:

- Resizing
    
- Cropping
    
- Rotation
    
- Contrast enhancement
    
- Noise reduction
    
- Perspective correction
    

Specific techniques will depend on the selected AI pipeline.

---

# 4. OCR & Information Extraction

## FR-05 — OCR/Text Extraction

**Priority:** MUST  
**Phase:** 1

The system shall extract machine-readable text from submitted package images.

---

## FR-06 — Text Region Detection

**Priority:** SHOULD  
**Phase:** 1

The system should identify the image regions associated with extracted text.

This enables evidence highlighting and downstream analysis.

---

## FR-07 — Declaration Identification

**Priority:** MUST  
**Phase:** 1

The system shall identify text that appears to correspond to relevant packaged-commodity declarations.

---

## FR-08 — Structured Field Extraction

**Priority:** MUST  
**Phase:** 1

The system shall transform relevant OCR output into structured fields.

Potential fields include:

- Product name
    
- Manufacturer
    
- Packer
    
- Importer
    
- Address
    
- Net quantity
    
- MRP
    
- Date information
    
- Consumer care information
    
- Other applicable declarations
    

Applicability shall be determined using the compliance layer.

---

## FR-09 — Extraction Confidence

**Priority:** SHOULD  
**Phase:** 1

Where supported by the AI/OCR pipeline, extracted values should contain confidence information.

Low-confidence extraction should be marked for review.

---

## FR-10 — Extraction Correction

**Priority:** SHOULD  
**Phase:** 1

The inspector should be able to correct incorrectly extracted information before final verification.

Corrections should be distinguishable from original automated extraction where practical.

---

# 5. Compliance Engine

## FR-11 — Rule Repository

**Priority:** MUST  
**Phase:** 1

The system shall maintain a structured representation of applicable compliance requirements.

Each rule should have a unique identifier.

Conceptually:

```
Rule ID
Requirement
Applicability
Validation Logic
Evidence Requirement
Source Reference
Version
```

---

## FR-12 — Rule Applicability

**Priority:** MUST  
**Phase:** 1

The system shall determine which checks are applicable based on available product information and rule conditions.

---

## FR-13 — Mandatory Declaration Checking

**Priority:** MUST  
**Phase:** 1

The system shall check whether applicable required declarations have been detected.

Possible result states:

```
PRESENT
MISSING
UNCLEAR
NOT APPLICABLE
```

---

## FR-14 — Declaration Validation

**Priority:** MUST  
**Phase:** 1

The system shall validate extracted declarations against applicable structured rules.

Examples of validation categories may include:

- Presence
    
- Format
    
- Value consistency
    
- Required information
    
- Presentation
    

The precise legal validation must be derived from verified source material.

---

## FR-15 — Potential Non-Compliance Detection

**Priority:** MUST  
**Phase:** 1

The system shall identify potential non-compliance based on failed or uncertain compliance checks.

The result should explain:

- What was detected.
    
- What requirement was checked.
    
- Why the result was flagged.
    
- What evidence supports the finding.
    

---

## FR-16 — Compliance Status

**Priority:** MUST  
**Phase:** 1

Each inspection should receive a structured status.

Suggested statuses:

```
COMPLIANT
POTENTIAL_NON_COMPLIANCE
REQUIRES_REVIEW
ANALYSIS_FAILED
```

The system should not present an AI-generated result as a definitive legal finding.

---

## FR-17 — Rule Traceability

**Priority:** MUST  
**Phase:** 1

Each compliance check should be traceable to its underlying verified requirement.

---

# 6. Font & Readability Analysis

## FR-18 — Readability Assessment

**Priority:** SHOULD  
**Phase:** 1

The system should assess whether relevant text appears sufficiently readable for automated screening.

Potential factors:

- Resolution
    
- Contrast
    
- Blur
    
- Occlusion
    
- Character clarity
    

---

## FR-19 — Font Size Estimation

**Priority:** SHOULD  
**Phase:** 1

The system should investigate whether apparent font size can be estimated from the submitted image.

The system must account for the limitations of estimating physical dimensions from ordinary photographs.

Where reliable measurement is not possible, the result should be:

```
REQUIRES PHYSICAL / HUMAN VERIFICATION
```

rather than an unsupported legal conclusion.

---

## FR-20 — Placement Analysis

**Priority:** SHOULD  
**Phase:** 1

The system should investigate whether relevant declarations appear to be placed appropriately based on technically detectable criteria.

---

# 7. Evidence

## FR-21 — Source Image Preservation

**Priority:** MUST  
**Phase:** 1

The system shall retain the source image associated with an inspection.

---

## FR-22 — Evidence Region

**Priority:** MUST  
**Phase:** 1

Where technically possible, the system shall associate a finding with the relevant image region.

---

## FR-23 — Evidence Text

**Priority:** MUST  
**Phase:** 1

The system should display the extracted text associated with a finding.

---

## FR-24 — Evidence Explanation

**Priority:** MUST  
**Phase:** 1

Every potential finding should contain a human-readable explanation.

---

## FR-25 — Inspector Notes

**Priority:** SHOULD  
**Phase:** 1

The inspector should be able to add notes to an inspection or finding.

---

# 8. Human Verification

## FR-26 — Finding Review

**Priority:** MUST  
**Phase:** 1

The inspector shall be able to review automatically generated findings.

---

## FR-27 — Finding Verification

**Priority:** MUST  
**Phase:** 1

The inspector should be able to mark findings as:

```
CONFIRMED
REJECTED
CORRECTED
REQUIRES FURTHER REVIEW
```

Exact terminology may be refined during UX development.

---

## FR-28 — Verification Record

**Priority:** SHOULD  
**Phase:** 1

The system should retain the verification state and relevant notes.

---

# 9. Inspection Repository

## FR-29 — Inspection Creation

**Priority:** MUST  
**Phase:** 1

The system shall create a unique inspection record.

---

## FR-30 — Inspection Persistence

**Priority:** MUST  
**Phase:** 1

Inspection data shall be persisted for later retrieval.

---

## FR-31 — Inspection History

**Priority:** MUST  
**Phase:** 1

Users shall be able to access previous inspection records according to their permissions.

---

## FR-32 — Inspection Search

**Priority:** SHOULD  
**Phase:** 1

Users should be able to search inspection records.

Potential filters:

- Inspection ID
    
- Date
    
- Product
    
- Compliance status
    
- Finding category
    
- Inspector
    

---

# 10. Reports

## FR-33 — Compliance Report Generation

**Priority:** MUST  
**Phase:** 1

The system shall generate a structured inspection/compliance report.

---

## FR-34 — PDF Export

**Priority:** MUST  
**Phase:** 1

The system shall support PDF report generation.

---

## FR-35 — Editable Report

**Priority:** SHOULD  
**Phase:** 1

The system should support an editable report format where technically feasible.

---

## FR-36 — Evidence in Report

**Priority:** MUST  
**Phase:** 1

Relevant evidence should be included or referenced in generated reports.

---

# 11. Dashboard

## FR-37 — Inspection Dashboard

**Priority:** MUST  
**Phase:** 1

The system shall provide a dashboard summarizing inspection activity.

---

## FR-38 — Compliance Summary

**Priority:** MUST  
**Phase:** 1

The dashboard shall display compliance status information.

---

## FR-39 — Violation Summary

**Priority:** MUST  
**Phase:** 1

The dashboard shall summarize potential violations/findings.

---

## FR-40 — Inspection Trends

**Priority:** SHOULD  
**Phase:** 1

The dashboard should display useful inspection trends where sufficient data exists.

---

# 12. Authentication & Authorization

## FR-41 — Authentication

**Priority:** MUST  
**Phase:** 1

The system shall provide secure user authentication.

The exact implementation may be simplified for the prototype.

---

## FR-42 — Role-Based Access

**Priority:** SHOULD  
**Phase:** 1

The system should support role-based access.

Initial conceptual roles:

```
Inspector
Supervisor
Administrator
```

---

# 13. Security Requirements

## SEC-01 — Secret Protection

**Priority:** MUST

The system shall not expose API keys, passwords, tokens, or other secrets in source control.

---

## SEC-02 — Input Validation

**Priority:** MUST

Uploaded files and user inputs shall be validated.

---

## SEC-03 — Access Control

**Priority:** MUST

Users should only access resources permitted by their role.

---

## SEC-04 — Secure Data Handling

**Priority:** MUST

Inspection information and uploaded evidence should be handled using appropriate security practices.

---

# 14. AI / System Reliability Requirements

## AI-01 — Uncertainty Handling

**Priority:** MUST

The system shall represent uncertain AI/OCR results rather than presenting them as certain.

---

## AI-02 — Failure Handling

**Priority:** MUST

If OCR or AI analysis fails, the system shall provide a meaningful error or review state.

---

## AI-03 — Evidence Association

**Priority:** MUST

Where possible, AI-generated findings should retain their source image/text association.

---

## AI-04 — Human Review

**Priority:** MUST

AI-generated potential findings shall be reviewable by a human inspector.

---

# 15. Non-Functional Requirements

## NFR-01 — Usability

The primary inspection workflow should be understandable to a non-technical enforcement user.

---

## NFR-02 — Responsiveness

The web interface should work across common desktop and mobile-sized screens where practical.

---

## NFR-03 — Maintainability

AI/OCR, compliance logic, backend, database, and frontend components should remain sufficiently modular.

---

## NFR-04 — Extensibility

New compliance rules and product categories should be addable without major UI redesign.

---

## NFR-05 — Explainability

Potential findings should provide enough information for an inspector to understand why they were generated.

---

## NFR-06 — Error Recovery

The system should gracefully handle:

- Invalid images
    
- OCR failure
    
- Missing data
    
- Backend errors
    
- Network errors
    
- Unsupported inputs
    

---

# 16. Phase 2 Requirements

These are primarily reserved for national-level development.

## P2-01 — Mobile Application

Native/mobile inspector application.

## P2-02 — Camera-Based Scanning

Direct package scanning using the device camera.

## P2-03 — Offline Operation

Inspection capability during limited connectivity.

## P2-04 — Synchronization

Synchronization of field inspections with the central platform.

## P2-05 — Advanced Product Identification

Potential barcode/product recognition capabilities.

## P2-06 — Advanced Analytics

Expanded administrative analytics.

## P2-07 — Scalable Infrastructure

Production-grade infrastructure for larger inspection volumes.

## P2-08 — Expanded Rule Coverage

Broader and more detailed coverage of applicable requirements.

---

# 17. Requirement Status

Implementation status should be tracked using:

```
NOT STARTED
PLANNED
IN DEVELOPMENT
IN REVIEW
TESTING
COMPLETED
BLOCKED
DEFERRED
```

Each implemented requirement should eventually have:

```
Requirement ID
Owner
Implementation
Test Status
PR
Notes
```

---

# 18. MVP Definition

For the internal hackathon, the MVP should prioritize:

```
IMAGE
  ↓
OCR
  ↓
DECLARATION EXTRACTION
  ↓
RULE CHECK
  ↓
POTENTIAL FINDING
  ↓
EVIDENCE
  ↓
HUMAN REVIEW
  ↓
REPORT
```

Features outside this flow should not delay the first end-to-end prototype.

---

# 19. Requirements Governance

Requirements may evolve as the project progresses.

However:

- New features should have a documented purpose.
    
- Legal requirements must be verified.
    
- Major scope changes should be discussed by the team.
    
- Phase 2 features should not unnecessarily consume Phase 1 development time.
    
- AI suggestions should not automatically become requirements.
    

---

# 20. Document Status

**Version:** 0.1  
**Stage:** Initial Requirements Definition  
**Phase:** Internal Hackathon — Phase 1

This is a living requirements document.