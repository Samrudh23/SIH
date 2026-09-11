# SIH26034 — Packaged Commodity Compliance System

> **Smart compliance screening for packaged commodities under the Legal Metrology (Packaged Commodities) Rules, 2011**

## Problem Statement

**SIH26034 — Software System to check compliance of Packaged Commodities under Legal Metrology (Packaged Commodities) Rules, 2011 by scanning products, images and labels.**

Packaged commodities are widely sold through retail stores, supermarkets, and e-commerce platforms across India. Under the Legal Metrology Act, 2009 and the Legal Metrology (Packaged Commodities) Rules, 2011, packaged commodities are required to carry mandatory declarations such as manufacturer/packer/importer details, net quantity, Maximum Retail Price (MRP), date information, consumer care details, and other prescribed declarations.

Manual inspection of large numbers of products is time-consuming and resource-intensive. Non-compliance may include missing declarations, incorrect presentation, improper MRP declarations, inadequate readability, and other violations.

The objective of SIH26034 is to develop a software system capable of scanning product images, package labels, and product information to automatically extract and assess these declarations and identify potential non-compliance.

---

## Our Solution

We are developing an **AI-assisted packaged-commodity compliance screening platform** for enforcement officials.

The system will allow an inspector to upload or capture images of a packaged commodity. Computer vision and OCR-based processing will identify relevant text and declarations. A structured compliance engine will then evaluate the extracted information against the applicable requirements of the Legal Metrology (Packaged Commodities) Rules, 2011.

Potential issues will be presented with supporting evidence so that an enforcement official can review and verify the findings before they become part of an inspection record.

### Core workflow

```
                    PACKAGED COMMODITY
                           │
                           ▼
                  IMAGE / LABEL CAPTURE
                           │
                           ▼
                   IMAGE PROCESSING
                           │
                           ▼
                       OCR / CV
                           │
                           ▼
                 DECLARATION EXTRACTION
                           │
                           ▼
                  COMPLIANCE RULE ENGINE
                           │
                           ▼
                 COMPLIANCE ANALYSIS
                    ┌──────┴──────┐
                    ▼             ▼
                 PASS /         POTENTIAL
                 REVIEW         VIOLATION
                                  │
                                  ▼
                              EVIDENCE
                                  │
                                  ▼
                         HUMAN VERIFICATION
                                  │
                                  ▼
                         INSPECTION RECORD
                           ┌──────┴──────┐
                           ▼             ▼
                        REPORT       DASHBOARD
```

---

# Objectives

The system is being designed to:

- Scan and analyze images of packaged commodities.
    
- Automatically detect and extract mandatory declarations.
    
- Validate extracted information against applicable legal requirements.
    
- Identify missing or potentially non-compliant declarations.
    
- Analyze readability and apparent text/font characteristics where technically feasible.
    
- Check declaration placement and presentation where technically feasible.
    
- Highlight evidence associated with potential violations.
    
- Generate compliance and inspection reports.
    
- Maintain a searchable repository of scanned products and inspection history.
    
- Provide dashboards for enforcement and administrative monitoring.
    
- Support role-based access and secure authentication.
    
- Provide a foundation for future mobile-based field inspections.
    

---

# Core Features

### 1. Product Scanning

Inspectors can upload or capture images of packaged commodities and labels for analysis.

### 2. AI / OCR Analysis

The system processes package images to identify text, relevant regions, and candidate declarations.

Potential extracted information includes:

- Product/commodity name
    
- Manufacturer / packer / importer information
    
- Address details
    
- Net quantity
    
- Maximum Retail Price (MRP)
    
- Date-related declarations
    
- Consumer care details
    
- Other applicable declarations
    

### 3. Compliance Checking

Extracted declarations are evaluated against a structured representation of the applicable Legal Metrology requirements.

The system should distinguish between:

- Detected and apparently compliant
    
- Missing
    
- Potentially invalid
    
- Unclear / requires review
    
- Not applicable
    

### 4. Evidence

Potential issues should be accompanied by supporting evidence such as:

- Source image
    
- Relevant image region
    
- Extracted text
    
- Applicable requirement
    
- Detection confidence
    
- Explanation of the finding
    

### 5. Human Verification

AI-generated findings are intended to **assist enforcement officials**, not replace their judgment.

An inspector should be able to review, confirm, or reject potential findings.

### 6. Inspection Repository

The system will maintain:

- Product records
    
- Inspection records
    
- Uploaded images
    
- Extracted declarations
    
- Compliance results
    
- Potential violations
    
- Evidence
    
- Reports
    
- Inspection history
    

### 7. Reports

The system will generate digital inspection/compliance reports, including PDF and, where implemented, editable formats.

### 8. Dashboard

Administrative users will be able to monitor:

- Inspection activity
    
- Compliance status
    
- Potential violations
    
- Product history
    
- Inspection trends
    
- Generated reports
    

---

# Development Phases

## Phase 1 — Internal Hackathon Prototype

The first version will be a **web-based prototype** focused on demonstrating the complete core workflow.

### Target flow

```
Upload Product
      ↓
Analyze Images
      ↓
Extract Declarations
      ↓
Run Compliance Checks
      ↓
Show Findings + Evidence
      ↓
Inspector Verification
      ↓
Generate Report
      ↓
Save Inspection
```

The goal of Phase 1 is to demonstrate a convincing **end-to-end working prototype**, rather than attempting to implement every possible feature.

---

## Phase 2 — National-Level System

If selected for the national stage, the platform can be expanded into:

```
                    BACKEND PLATFORM
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       INSPECTOR MOBILE APP       ADMIN WEB PORTAL
              │                         │
          Camera                    Dashboard
          Scanning                  Analytics
          Evidence                 Inspections
          Reports                  Reports
          Field Data               Management
```

Potential Phase 2 capabilities include:

- Native/mobile field inspection
    
- Camera-based scanning
    
- Faster field workflows
    
- Barcode/product identification
    
- Offline or low-connectivity support
    
- Synchronization
    
- Advanced analytics
    
- Multi-level administrative access
    
- Centralized inspection management
    
- Improved AI/CV models
    
- Expanded product/rule coverage
    

Phase 2 features will be introduced only after the Phase 1 architecture has been validated.

---

# Compliance & Legal Disclaimer

This project is intended as a **software-assisted compliance screening and inspection support system**.

AI/OCR output is not inherently a legally conclusive determination. Extracted information and automatically detected issues should be reviewed against the applicable legal provisions and, where appropriate, verified by an authorized enforcement official.

The compliance engine must be based on verified provisions of the applicable Legal Metrology framework rather than generated assumptions.

The primary reference material for the project is the **Legal Metrology Act, 2009 and Legal Metrology (Packaged Commodities) Rules, 2011**, along with authoritative material published by the relevant government authorities.

---

# Technology

The final technology stack is currently being evaluated.

The architecture is expected to include components for:

|Layer|Purpose|
|---|---|
|Frontend|Inspector and administrative interfaces|
|Backend|APIs, business logic and orchestration|
|AI / OCR|Image analysis, text extraction and field detection|
|Compliance Engine|Rule-based validation|
|Database|Users, products, inspections and results|
|File Storage|Package images and evidence|
|Reporting|PDF and editable report generation|
|Authentication|Secure role-based access|
|Deployment|Web/cloud infrastructure|

Specific technologies will be finalized during the architecture phase.

---

# Team

|   |   |   |
|---|---|---|
|Member|Role|Primary Responsibility|
|**P1**|AI / OCR|Computer vision, OCR and declaration extraction|
|**P2**|Compliance|Legal rules, rule mapping and compliance engine|
|**P3**|Backend|APIs, database, authentication and system integration|
|**P4**|Frontend / UX|Inspector-facing interface and user experience|
|**P5**|Security Testing|Vulnerability testing, auth/access-control checks|
|**P6**|Deployment and Polish|CI/CD, hosting/infra setup, final QA pass, UI/UX polish|

Responsibilities may evolve as the project develops.

---

# Git Workflow

The repository uses a **branch-per-member workflow**.

```
                         ┌── p1
                         ├── p2
                         ├── p3
                         ├── p4
             main ───────┼── p5
                         └── p6
```

### Branch ownership

- `main` — stable, reviewed project
    
- `p1` — P1's development branch
    
- `p2` — P2's development branch
    
- `p3` — P3's development branch
    
- `p4` — P4's development branch
    
- `p5` — P5's development branch
    
- `p6` — P6's development branch
    

### Rules

- Do **not** push directly to `main`.
    
- Develop on your assigned branch.
    
- Test your changes before requesting a merge.
    
- Submit a Pull Request to merge work into `main`.
    
- Changes must be reviewed before merging.
    
- Do not commit API keys, passwords, tokens, or other secrets.
    
- Avoid unrelated changes in a PR.
    
- Keep `main` in a runnable and stable state.
    

See `[CONTRIBUTING.md](app://-/CONTRIBUTING.md)` for the complete workflow.

---

# Repository Structure

The repository will evolve as development begins.

The initial structure is intentionally documentation-focused:

```
SIH26034/
│
├── README.md
├── PROJECT_STATE.md
├── CONTRIBUTING.md
├── .gitignore
├── .env.example
│
└── docs/
    ├── PROJECT_SPEC.md
    ├── REQUIREMENTS.md
    └── DEVELOPMENT_PLAN.md
```

Application code, AI pipelines, backend services, frontend applications, datasets, and other implementation-specific directories will be introduced through the respective development branches after the architecture is finalized.

---

# References

- Ministry / Department of Consumer Affairs — Legal Metrology resources
    
- Legal Metrology Act, 2009
    
- Legal Metrology (Packaged Commodities) Rules, 2011
    

Official reference material:

[https://consumeraffairs.gov.in/pages/legal-metrology-act](https://consumeraffairs.gov.in/pages/legal-metrology-act)

---

# Project Status

**Current Phase:** Phase 1 — Internal Hackathon  
**Current Stage:** Repository Initialization / Planning

The project is currently establishing its requirements, compliance-rule mapping, architecture, technology stack, and development workflow.

---

## Important

This project is being developed for the **Smart India Hackathon 2026** and is currently a prototype.

Features, architecture, implementation details, and compliance coverage may evolve throughout development.