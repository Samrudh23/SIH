
> Internal project status and coordination document.

---

## Current Status

|Item|Status|
|---|---|
|Problem Statement|✅ Selected|
|Team Structure|✅ Defined|
|Git Workflow|✅ Defined|
|Repository Foundation|🔄 In Progress|
|Requirements Analysis|🔄 In Progress|
|Compliance Rule Mapping|⏳ Not Started|
|Architecture|⏳ Not Finalized|
|Technology Stack|⏳ Not Finalized|
|AI/OCR Prototype|⏳ Not Started|
|Compliance Engine|⏳ Not Started|
|Backend|⏳ Not Started|
|Frontend|⏳ Not Started|
|Dashboard|⏳ Not Started|
|Testing Dataset|⏳ Not Started|
|End-to-End Prototype|⏳ Not Started|

---

# Current Phase

## Phase 1 — Internal Hackathon

The immediate objective is to build a **working web-based prototype** demonstrating the complete packaged-commodity compliance workflow.

### Current sprint

**Sprint 0 — Foundation & Planning**

### Current goal

Establish a common understanding of:

1. What SIH26034 requires.
    
2. What our product will do.
    
3. Which requirements are included in the MVP.
    
4. How the system will be architected.
    
5. How the Legal Metrology rules will be represented.
    
6. How the six team members will work together.
    
7. How AI-generated code will be reviewed and integrated.
    

---

# Product Definition

The project is an **AI-assisted compliance screening system for packaged commodities**.

The intended workflow is:

```
Package / Product
       ↓
Image Capture / Upload
       ↓
Image Processing
       ↓
OCR / Computer Vision
       ↓
Declaration Extraction
       ↓
Compliance Rule Engine
       ↓
Potential Compliance Findings
       ↓
Supporting Evidence
       ↓
Human Verification
       ↓
Inspection Record
       ↓
Report + Dashboard
```

The system should assist an enforcement official in identifying potential issues efficiently while keeping human verification in the inspection workflow.

---

# Phase 1 MVP

The internal prototype should prioritize the following:

### Must demonstrate

- Product/package image upload
    
- Image analysis
    
- OCR/text extraction
    
- Mandatory declaration detection
    
- Structured declaration extraction
    
- Missing declaration detection
    
- Basic declaration validation
    
- Compliance result generation
    
- Potential violation identification
    
- Supporting evidence
    
- Human review/verification
    
- Inspection record creation
    
- Inspection history
    
- Compliance report
    
- Basic administrative dashboard
    

### Important but dependent on feasibility

- Font-size analysis
    
- Readability analysis
    
- Declaration placement analysis
    
- Detection of misleading/non-standard declarations
    
- Editable report export
    
- Advanced search/filtering
    
- Role-based access
    

### Not a Phase 1 priority

- Native mobile application
    
- Offline-first field operation
    
- Large-scale deployment
    
- Advanced predictive analytics
    
- Extensive product-category coverage
    
- Production-grade nationwide infrastructure
    

These may be considered during Phase 2.

---

# Compliance Principle

The system must maintain a clear distinction between:

```
AI
 ↓
"What does the package appear to say/show?"
```

and

```
RULE ENGINE
 ↓
"Does the extracted information satisfy the applicable requirement?"
```

and

```
HUMAN INSPECTOR
 ↓
"Should this finding be accepted as part of the inspection?"
```

AI-generated output must not be treated as an automatic legal determination.

Compliance rules must be based on verified legal/reference material.

---

# Team Responsibilities

## P1 — AI / OCR

Primary focus:

- Image preprocessing
    
- OCR
    
- Text detection
    
- Declaration extraction
    
- Bounding boxes/evidence regions
    
- Confidence scores
    
- AI pipeline evaluation
    

---

## P2 — Compliance

Primary focus:

- Study applicable Legal Metrology requirements
    
- Build compliance-rule inventory
    
- Define validation logic
    
- Identify applicable conditions
    
- Create machine-readable rule structures
    
- Validate compliance-engine behaviour
    

---

## P3 — Backend

Primary focus:

- Backend architecture
    
- API design
    
- Database
    
- Authentication
    
- File/evidence storage
    
- AI integration
    
- Compliance-engine integration
    
- System orchestration
    

---

## P4 — Frontend / UX

Primary focus:

- Inspector workflow
    
- Product scanning interface
    
- Upload/capture interface
    
- Analysis state
    
- Compliance results
    
- Evidence/violation interface
    
- Human verification flow
    
- Overall usability
    

---

## P5 — Dashboard / Reports

Primary focus:

- Administrative dashboard
    
- Inspection history interface
    
- Compliance analytics
    
- Violation summaries
    
- Report generation
    
- PDF/editable report output
    

---

## P6 — QA / Data / Integration

Primary focus:

- Test dataset
    
- Ground-truth results
    
- Test cases
    
- AI/OCR evaluation
    
- Integration testing
    
- Regression testing
    
- Bug tracking
    
- Final prototype validation
    

P6 also acts as an additional quality gate during integration.

---

# Git & Integration State

## Branches

```
main
├── p1
├── p2
├── p3
├── p4
├── p5
└── p6
```

### `main`

Must remain:

- Stable
    
- Reviewed
    
- Runnable
    
- Free of known breaking changes
    

### Member branches

Each member develops primarily on their assigned branch.

```
p1 → P1
p2 → P2
p3 → P3
p4 → P4
p5 → P5
p6 → P6
```

Work reaches `main` through Pull Requests and review.

---

# Current Development Flow

```
Task
 ↓
Assigned to member
 ↓
Member works on personal branch
 ↓
Local testing
 ↓
Pull Request
 ↓
Code review
 ↓
QA / integration check where applicable
 ↓
Team lead approval
 ↓
Merge into main
 ↓
Update project state
```

---

# Current Tasks

### Repository / Leadership

- Select SIH26034
    
- Define six team roles
    
- Define branch strategy
    
- Create repository foundation
    
- Protect `main`
    
- Create P1–P6 branches
    
- Finalize development workflow
    

### Requirements

- Convert PS into functional requirements
    
- Define MVP
    
- Define Phase 2 scope
    
- Identify technical constraints
    
- Identify unresolved questions
    

### Compliance

- Obtain and study authoritative Legal Metrology material
    
- Identify applicable declarations
    
- Map requirements to validation logic
    
- Define rule representation
    
- Identify category-specific requirements
    

### Architecture

- Finalize technology stack
    
- Design system architecture
    
- Define data model
    
- Define API contracts
    
- Define AI/backend interface
    
- Define compliance-engine interface
    

### AI

- Collect representative package images
    
- Select OCR approach
    
- Test OCR accuracy
    
- Design declaration extraction
    
- Define confidence/evidence output
    

### Application

- Design inspector workflow
    
- Design dashboard
    
- Implement backend
    
- Implement frontend
    
- Implement compliance engine
    
- Integrate AI/OCR
    
- Implement reports
    

### QA

- Build ground-truth dataset
    
- Define acceptance criteria
    
- Create test cases
    
- Perform component testing
    
- Perform end-to-end testing
    
- Measure prototype performance
    

---

# Project Rules

### 1. Do not code before understanding the requirement

A feature should have a defined purpose before implementation.

### 2. Do not treat AI output as legal truth

AI assists extraction and screening. Rules and human review remain important.

### 3. Do not invent legal requirements

Compliance logic must be traceable to verified source material.

### 4. Do not commit secrets

API keys, passwords, tokens, private credentials, and `.env` files must never be committed.

### 5. Do not break `main`

If a feature is unfinished or unstable, it stays on the development branch.

### 6. AI-generated code still requires human review

The person responsible for a branch is responsible for understanding, testing, and reviewing the code produced with AI assistance.

---

# First Major Milestone

## M1 — First End-to-End Compliance Analysis

The first major technical milestone is:

```
REAL PACKAGE IMAGE
       ↓
OCR / AI
       ↓
STRUCTURED DECLARATIONS
       ↓
COMPLIANCE RULES
       ↓
POTENTIAL FINDINGS
       ↓
EVIDENCE
       ↓
COMPLIANCE RESULT
```

The team should prioritize achieving this before expanding into secondary features.

---

# Future Milestones

### M1

First successful end-to-end analysis.

### M2

Working web-based inspection workflow.

### M3

Compliance engine integrated with verified rules.

### M4

Evidence + human verification implemented.

### M5

Reports + inspection repository implemented.

### M6

Admin dashboard integrated.

### M7

Full internal-hackathon demo stabilized.

### M8 — If advancing

Begin Phase 2 mobile + admin platform development.

---

# Update Policy

This file should be updated whenever there is a meaningful change to:

- Current phase
    
- Sprint
    
- Major milestone
    
- Team responsibility
    
- Architecture decision
    
- Blocker
    
- MVP scope
    
- Project status
    

Keep this document **short and current**.

It is a project coordination document, not a detailed technical specification.