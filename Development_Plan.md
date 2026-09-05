## 1. Purpose

This document defines the development roadmap for SIH26034.

The development strategy is:

> **Build the smallest complete end-to-end system first, then expand it.**

The team should avoid spending the majority of the hackathon building isolated features that cannot be demonstrated together.

---

# 2. Development Strategy

The project will be developed in stages:

```
FOUNDATION
    ↓
ARCHITECTURE
    ↓
INDIVIDUAL COMPONENT PROTOTYPES
    ↓
FIRST END-TO-END PIPELINE
    ↓
INTEGRATION
    ↓
REPORTING + DASHBOARD
    ↓
TESTING
    ↓
UI / UX POLISH
    ↓
DEMO STABILIZATION
```

---

# 3. Team Structure

|Member|Primary Area|
|---|---|
|**P1**|AI / OCR / Computer Vision|
|**P2**|Compliance / Rules Engine|
|**P3**|Backend / Database / APIs|
|**P4**|Frontend / UX|
|**P5**|Dashboard / Reports|
|**P6**|QA / Data / Integration|

The team should collaborate across boundaries rather than treating these as completely isolated projects.

---

# 4. Development Principles

## 4.1 End-to-End First

The first major technical objective is:

```
Package Image
     ↓
OCR
     ↓
Extracted Fields
     ↓
Rule Check
     ↓
Finding
     ↓
Evidence
```

Once this works, the team can add persistence, reports, dashboards, and polish.

---

## 4.2 Contract Before Integration

When two components interact, define their expected input/output before implementing the integration.

Example:

```
P1 AI/OCR
     ↓
Structured OCR Result
     ↓
P3 Backend
```

The structure should be agreed upon before both sides independently implement incompatible formats.

---

## 4.3 Prototype Before Optimization

The internal hackathon is primarily about proving feasibility.

Do not prematurely optimize:

- Infrastructure
    
- Model size
    
- Database scaling
    
- Complex authentication
    
- Microservices
    
- Advanced analytics
    

unless they directly improve the prototype.

---

# 5. Sprint 0 — Foundation

## Objective

Establish the project foundation before major development begins.

### Tasks

- Select SIH26034.
    
- Define team roles.
    
- Define Git workflow.
    
- Create repository.
    
- Protect `main`.
    
- Create P1–P6 branches.
    
- Create documentation structure.
    
- Finalize communication workflow.
    
- Establish coding/review standards.
    

### Deliverable

A clean repository with agreed project scope and development process.

---

# 6. Sprint 1 — Research & Architecture

## Objective

Turn the problem statement into an implementable system.

### P1 — AI/OCR

- Investigate OCR approaches.
    
- Test representative package images.
    
- Identify image-quality problems.
    
- Evaluate candidate OCR systems.
    
- Define extraction output format.
    

### P2 — Compliance

- Obtain authoritative legal/reference material.
    
- Identify relevant declarations.
    
- Build initial rule inventory.
    
- Identify applicability conditions.
    
- Define machine-readable rule structure.
    
- Identify requirements that cannot reliably be assessed from images alone.
    

### P3 — Backend

- Evaluate backend technology.
    
- Design API boundaries.
    
- Design initial database model.
    
- Define storage strategy.
    
- Define AI/backend integration.
    

### P4 — Frontend

- Map inspector workflow.
    
- Create low-fidelity wireframes.
    
- Define key screens.
    
- Define design system direction.
    
- Prototype upload → analysis → result flow.
    

### P5 — Dashboard/Reports

- Define report structure.
    
- Identify dashboard metrics.
    
- Design inspection-history interface.
    
- Determine PDF generation approach.
    

### P6 — QA/Data

- Build initial test dataset.
    
- Define ground-truth methodology.
    
- Define test cases.
    
- Create evaluation criteria.
    
- Identify expected failure cases.
    

### Deliverable

A finalized initial architecture and a clear MVP implementation plan.

---

# 7. Sprint 2 — Component Prototypes

## Objective

Build the first functional version of the major components.

### P1

Build:

```
Image
 ↓
Preprocessing
 ↓
OCR
 ↓
Structured Extraction
```

### P2

Build:

```
Input Fields
 ↓
Rule Evaluation
 ↓
Compliance Result
```

The first rules should focus on a manageable subset suitable for demonstration.

### P3

Build:

```
API
 ↓
Inspection
 ↓
Database
```

### P4

Build:

```
Upload Screen
 ↓
Analysis State
 ↓
Results Screen
```

### P5

Build initial:

```
Inspection Summary
Report Layout
Dashboard Skeleton
```

### P6

Build:

```
Test Dataset
Test Cases
Basic Validation
```

### Deliverable

Each major component works independently.

---

# 8. Sprint 3 — First End-to-End Integration

## Objective

Connect the core components.

Target flow:

```
                  USER
                   │
                   ▼
              FRONTEND
                   │
                   ▼
              BACKEND API
                   │
             ┌─────┴─────┐
             ▼           ▼
           AI/OCR      DATABASE
             │
             ▼
       EXTRACTED DATA
             │
             ▼
        RULE ENGINE
             │
             ▼
          FINDINGS
             │
             ▼
          EVIDENCE
             │
             ▼
          FRONTEND
```

### Priority

This sprint is extremely important.

The team should prefer:

> **One complete working workflow**

over:

> Ten impressive but disconnected features.

---

# 9. Sprint 4 — Human Verification & Evidence

## Objective

Make the system usable as an actual inspection-support tool.

Implement:

- Finding review.
    
- Evidence display.
    
- Highlighted image regions.
    
- Extracted text display.
    
- Inspector notes.
    
- Confirm/reject/correct actions.
    
- Inspection status.
    
- Persisted verification.
    

Target flow:

```
AI Finding
    ↓
Evidence
    ↓
Inspector Review
    ↓
Confirm / Reject / Correct
    ↓
Final Inspection Record
```

---

# 10. Sprint 5 — Reports & Repository

## Objective

Turn analysis into a complete inspection record.

Implement:

- Inspection history.
    
- Search.
    
- Filtering.
    
- Report generation.
    
- PDF export.
    
- Evidence inclusion.
    
- Inspection metadata.
    
- Report retrieval.
    

Target:

```
Inspection
    ↓
Analysis
    ↓
Verification
    ↓
Saved Record
    ↓
Report
```

---

# 11. Sprint 6 — Dashboard

## Objective

Provide an administrative overview.

Implement:

- Total inspections.
    
- Compliance status.
    
- Potential violation counts.
    
- Recent inspections.
    
- Finding categories.
    
- Basic trends.
    
- Search/filtering.
    

The dashboard should be based on actual stored inspection data rather than static demo numbers wherever possible.

---

# 12. Sprint 7 — Testing & Evaluation

## Objective

Measure whether the prototype actually works.

### P6 leads this phase.

Evaluate:

### OCR

- Text extraction accuracy.
    
- Declaration extraction accuracy.
    
- Failure cases.
    

### Compliance

- Correct rule application.
    
- False positives.
    
- False negatives.
    
- Unclear cases.
    

### UI

- User workflow.
    
- Error states.
    
- Loading states.
    
- Mobile/desktop responsiveness.
    

### Backend

- API behaviour.
    
- Error handling.
    
- Persistence.
    
- Integration.
    

### End-to-end

Test:

```
Image
 ↓
OCR
 ↓
Extraction
 ↓
Compliance
 ↓
Finding
 ↓
Evidence
 ↓
Verification
 ↓
Report
```

---

# 13. Sprint 8 — Demo Stabilization

## Objective

Create a reliable SIH demonstration.

### Freeze major architecture changes.

Focus on:

- Bug fixing.
    
- UI consistency.
    
- Performance.
    
- Error handling.
    
- Demo dataset.
    
- Report quality.
    
- Loading states.
    
- Empty states.
    
- Failure states.
    
- Presentation quality.
    

---

# 14. Critical Demo Path

The team should define one **golden demo workflow**.

Example:

```
1. Login
      ↓
2. Create inspection
      ↓
3. Upload package image
      ↓
4. Analyze
      ↓
5. OCR extracts declarations
      ↓
6. Compliance engine evaluates them
      ↓
7. Potential issue is identified
      ↓
8. Evidence is highlighted
      ↓
9. Inspector reviews finding
      ↓
10. Inspector verifies result
      ↓
11. Inspection is saved
      ↓
12. Report generated
      ↓
13. Dashboard updated
```

This workflow must work reliably before the final presentation.

---

# 15. Parallel Development Model

The team should work in parallel where dependencies allow.

```
             ┌── P1 AI/OCR ─────┐
             │                   │
             ├── P2 Rules ──────┤
             │                   │
             ├── P3 Backend ────┼──→ INTEGRATION
             │                   │
             ├── P4 Frontend ───┤
             │                   │
             ├── P5 Reports ────┤
             │                   │
             └── P6 QA/Data ────┘
```

However, parallel development requires clearly defined interfaces.

---

# 16. Key Dependencies

## P1 → P3

P1 provides the AI/OCR output structure.

P3 integrates it into the backend.

---

## P2 → P3

P2 defines the rule structure and compliance logic.

P3 integrates the compliance engine into the application.

---

## P3 → P4

P3 provides backend APIs.

P4 consumes those APIs.

---

## P3 → P5

P3 provides inspection/report data.

P5 uses that data for dashboards and reports.

---

## P6 → Everyone

P6 validates:

- AI
    
- Rules
    
- Backend
    
- Frontend
    
- Integration
    
- Final workflow
    

---

# 17. Integration Milestones

## Integration M1 — AI

```
Image → OCR → Structured Text
```

---

## Integration M2 — Compliance

```
Structured Text → Rules → Findings
```

---

## Integration M3 — Backend

```
Frontend → API → AI/Rules → Database
```

---

## Integration M4 — Evidence

```
Finding → Image Region + Explanation
```

---

## Integration M5 — Verification

```
Finding → Inspector → Final Status
```

---

## Integration M6 — Reporting

```
Inspection → Report
```

---

## Integration M7 — Dashboard

```
Stored Inspections → Dashboard
```

---

# 18. Definition of Done

A feature is not considered complete merely because the AI coding tool generated code.

A feature is done when:

```
Requirement defined
      ↓
Implementation complete
      ↓
Local testing
      ↓
Edge cases considered
      ↓
Documentation updated
      ↓
PR created
      ↓
Review
      ↓
QA / integration
      ↓
Approved
      ↓
Merged into main
```

---

# 19. Vibe Coding Strategy

AI coding tools may be used extensively.

The team should use AI primarily for:

- Boilerplate.
    
- UI implementation.
    
- API scaffolding.
    
- Refactoring.
    
- Test generation.
    
- Documentation.
    
- Integration assistance.
    
- Debugging.
    
- Prototyping.
    

AI should **not independently determine**:

- Legal requirements.
    
- Compliance interpretations.
    
- Security architecture.
    
- Critical data models.
    
- Final API contracts.
    
- Major architectural decisions.
    

Those decisions require human review.

---

# 20. Anti-Overengineering Rules

During Phase 1, avoid unnecessary complexity.

Do not introduce:

- Microservices without a clear need.
    
- Multiple databases without justification.
    
- Complex distributed infrastructure.
    
- Advanced ML training pipelines before baseline feasibility.
    
- Excessive authentication complexity.
    
- Large-scale cloud architecture.
    
- Features unrelated to the core inspection workflow.
    

The prototype should be:

> **Simple enough to build quickly, structured enough to extend later.**

---

# 21. Scope Control

Every proposed feature should be classified:

```
MUST HAVE
SHOULD HAVE
NICE TO HAVE
PHASE 2
```

If a nice-to-have feature threatens the core workflow, postpone it.

Priority order:

```
Core compliance workflow
        ↓
Reliability
        ↓
Evidence
        ↓
Reports
        ↓
Dashboard
        ↓
UX polish
        ↓
Advanced features
```

---

# 22. Testing Strategy

Testing should occur continuously rather than only at the end.

### Component Testing

Each owner tests their own component.

### Integration Testing

P6 and relevant owners test component interactions.

### End-to-End Testing

The full workflow is tested from image upload to report.

### Regression Testing

After significant changes, previously working flows must be retested.

---

# 23. Demo Dataset Strategy

The team should maintain a controlled demo/test dataset containing representative package images.

Ideally include:

```
Clearly compliant examples
Potentially non-compliant examples
Missing declaration examples
Poor-quality images
Small text
Different package layouts
Different lighting
Different orientations
Ambiguous cases
```

Each test image should have an expected/ground-truth result where possible.

---

# 24. Technical Debt Policy

Technical shortcuts are acceptable during the hackathon when:

- They are intentional.
    
- They are documented.
    
- They do not compromise the demo.
    
- They can reasonably be replaced later.
    

Record significant shortcuts in:

`docs/KNOWN_LIMITATIONS.md`

---

# 25. Phase 2 Development Plan

If selected for the national stage:

## Stage 1 — Production Architecture

- Re-evaluate Phase 1 architecture.
    
- Harden backend.
    
- Improve security.
    
- Improve data model.
    
- Establish scalable infrastructure.
    

## Stage 2 — Mobile Application

Build inspector-facing mobile application:

```
Login
 ↓
Inspection
 ↓
Camera
 ↓
Scan
 ↓
AI Analysis
 ↓
Compliance
 ↓
Evidence
 ↓
Verification
```

## Stage 3 — Admin Platform

Expand administrative web portal:

- Inspector management.
    
- Inspection management.
    
- Advanced dashboard.
    
- Analytics.
    
- Reports.
    
- Rule management where appropriate.
    

## Stage 4 — Field Reliability

Potentially implement:

- Offline operation.
    
- Synchronization.
    
- Retry mechanisms.
    
- Local evidence storage.
    

## Stage 5 — AI Improvement

Improve:

- OCR.
    
- Text detection.
    
- Declaration extraction.
    
- Image quality handling.
    
- Layout understanding.
    
- Evidence localization.
    

## Stage 6 — Expanded Compliance Coverage

Expand the verified rule repository and support additional product categories and applicable conditions.

---

# 26. Final Phase 1 Deliverable

The final internal-hackathon prototype should be capable of demonstrating:

```
                SIH26034 PROTOTYPE

                       USER
                        │
                        ▼
                WEB APPLICATION
                        │
                        ▼
                 PRODUCT IMAGE
                        │
                        ▼
                    AI / OCR
                        │
                        ▼
              DECLARATION EXTRACTION
                        │
                        ▼
                COMPLIANCE ENGINE
                        │
                        ▼
                POTENTIAL FINDINGS
                        │
                        ▼
                    EVIDENCE
                        │
                        ▼
                HUMAN VERIFICATION
                        │
                        ▼
                INSPECTION RECORD
                    ┌───┴───┐
                    ▼       ▼
                 REPORT  DASHBOARD
```

This complete flow is the **primary definition of the Phase 1 prototype**.

---

# 27. Development Priority

When the team has limited time, use this order:

### Priority 1 — Core Pipeline

```
Image → OCR → Extraction → Rules → Finding
```

### Priority 2 — Evidence

```
Finding → Evidence → Explanation
```

### Priority 3 — Human Verification

```
Finding → Inspector → Final Result
```

### Priority 4 — Persistence

```
Inspection → Database → History
```

### Priority 5 — Reporting

```
Inspection → PDF Report
```

### Priority 6 — Dashboard

```
Inspection Data → Dashboard
```

### Priority 7 — Polish

```
UX → Performance → Visual Design → Demo
```

---

# 28. Project Completion Criteria

Phase 1 is ready for final demonstration when:

- Core inspection workflow works end-to-end.
    
- OCR/extraction works on the selected demo dataset.
    
- Compliance rules produce structured results.
    
- Findings have supporting evidence.
    
- Human verification works.
    
- Inspection records persist.
    
- Reports can be generated.
    
- Dashboard displays real prototype data.
    
- Major failure cases are handled.
    
- No known critical bugs remain.
    
- Main branch contains the stable demo version.
    
- The complete demo can be reproduced by the team.
    

---

# 29. Current Development Status

**Phase:** Phase 1 — Internal Hackathon  
**Sprint:** Sprint 0 — Foundation  
**Status:** Planning / Repository Initialization

The project will advance through the development stages described above as the team completes the foundation and architecture work.

---

# 30. Document Status

**Version:** 0.1  
**Stage:** Initial Development Plan

This document is a living roadmap. Sprint timing and feature priorities may be adjusted according to:

- Technical feasibility.
    
- Team progress.
    
- Prototype performance.
    
- SIH deadlines.
    
- Testing results.
    
- New project requirements.
    

Changes should be documented rather than silently altering the plan.