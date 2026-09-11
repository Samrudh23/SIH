SIH26034 — Packaged Commodity Compliance System

AI-assisted compliance screening for packaged commodities under the Legal Metrology (Packaged Commodities) Rules, 2011

«Smart India Hackathon 2026 — Phase 1 Prototype»

---

Problem Statement

SIH26034 — Software System to check compliance of Packaged Commodities under Legal Metrology (Packaged Commodities) Rules, 2011 by scanning products, images and labels.

Packaged commodities are widely sold through retail stores, supermarkets, and e-commerce platforms across India. Under the Legal Metrology Act, 2009 and the Legal Metrology (Packaged Commodities) Rules, 2011, packaged commodities are required to carry mandatory declarations such as manufacturer/packer/importer details, net quantity, Maximum Retail Price (MRP), date information, consumer care details, and other prescribed declarations.

Manual inspection of large numbers of products is time-consuming and resource-intensive. Non-compliance may include missing declarations, inconsistent declarations, potentially incorrect MRP information, inadequate readability, and other issues requiring verification.

The objective of SIH26034 is to develop a software system capable of scanning product images, package labels, and product information to automatically extract relevant declarations and screen them against applicable requirements.

---

Our Solution

SIH26034 is an AI-assisted packaged-commodity compliance screening and inspection-support platform designed for enforcement officials.

The system combines:

- Product and package image processing
- OCR-based text extraction
- Declaration extraction
- Structured compliance rules
- Confidence-aware analysis
- Evidence generation
- Human verification
- Inspection records
- Compliance reporting
- Dashboard-based monitoring

An inspector can provide images of a packaged commodity. The system processes the available visual information, extracts relevant declarations, evaluates them against applicable compliance requirements, and presents the resulting findings with evidence and confidence information.

The system is intentionally designed as a screening and decision-support tool, rather than an autonomous legal decision-maker.

---

Core Workflow

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
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
          COMPLIANT             POTENTIAL VIOLATION
              │                         │
              └────────────┬────────────┘
                           ▼
                    EVIDENCE DISPLAY
                           │
                           ▼
                   HUMAN VERIFICATION
                           │
                           ▼
                    INSPECTION RECORD
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
              REPORT             DASHBOARD

---

Phase 1 — Completed Prototype

The Phase 1 implementation demonstrates the complete core workflow from product submission through analysis, review, reporting, and inspection storage.

Implemented workflow

Upload Product
      ↓
Upload / Process Images
      ↓
OCR + Declaration Extraction
      ↓
Compliance Analysis
      ↓
Generate Findings + Evidence
      ↓
Inspector Review / Verification
      ↓
Generate Inspection Report
      ↓
Save Inspection Record
      ↓
Dashboard / Inspection History

The prototype focuses on demonstrating a practical end-to-end system rather than attempting to cover every possible packaged commodity or every provision of the Legal Metrology framework.

---

Key Features

1. Product Scanning

Inspectors can provide images of packaged commodities and their labels for analysis.

The system supports the inspection workflow around package images rather than relying solely on manually entered product information.

---

2. AI / OCR-Based Analysis

The analysis pipeline processes package images to identify relevant text and candidate declaration regions.

The system can extract information such as:

- Product / commodity name
- Manufacturer / packer / importer information
- Address details
- Net quantity
- Maximum Retail Price (MRP)
- Date-related declarations
- Consumer care information
- Other applicable declarations

The extracted information is represented in a structured format so that downstream compliance checks do not depend directly on raw OCR output.

---

3. Confidence-Aware Extraction

The system does not treat every OCR or visual detection as equally reliable.

Extraction and applicability confidence are tracked separately where required.

This allows uncertain results to be routed for manual review instead of being presented as definitive conclusions.

---

4. Structured Compliance Engine

The compliance layer evaluates extracted declarations against a structured representation of applicable requirements.

The engine supports compliance states including:

COMPLIANT
POTENTIAL_VIOLATION
NEEDS_MANUAL_REVIEW
NOT_APPLICABLE
NOT_DETECTED
ANALYSIS_FAILED

This distinction is important because an item that was not detected is not necessarily legally non-compliant, and an uncertain AI result should not automatically become a violation.

---

5. Evidence-Based Findings

Potential issues are accompanied by supporting information wherever available.

Evidence can include:

- Source image
- Relevant image region
- Extracted text
- Applicable requirement
- Detection confidence
- Applicability confidence
- Explanation of the finding
- Inspection context

This makes the system's output reviewable rather than presenting unexplained AI-generated conclusions.

---

6. Multi-Observation and Conflict Detection

The system can handle multiple observations of declarations across different package surfaces.

For example:

Front MRP:       ₹100
Back MRP:        ₹120
                         ↓
                 CONFLICT DETECTED
                         ↓
              NEEDS_MANUAL_REVIEW

Similarly, conflicting net-quantity observations can be detected and routed for review.

This prevents the system from silently selecting one conflicting observation and treating it as authoritative.

---

7. MRP Analysis

MRP extraction and comparison use confidence-aware processing rather than relying exclusively on a single rigid textual pattern.

Where matching is uncertain, the system can route the result to:

NEEDS_MANUAL_REVIEW

instead of presenting an uncertain interpretation as a confirmed legal violation.

---

8. Medical Device Applicability Handling

The compliance workflow includes a medical-device applicability gate.

Where the product may fall under the Medical Devices Rules framework, the system does not silently bypass the relevant packaged-commodity checks.

Instead, the applicability decision can require confirmation/manual review before the appropriate compliance path is selected.

This is particularly important because applicability depends on the legal framework applicable to the specific product.

---

9. Visual Compliance Assistance

The prototype includes visual-analysis support for requirements such as:

- Readability
- Text visibility
- Contrast
- Visual presentation

These visual checks are treated as screening aids and do not automatically produce definitive legal compliance conclusions where the system cannot reliably establish the applicable legal standard.

---

10. Human Verification

The system is designed around a human-in-the-loop workflow.

AI/OCR findings are presented to the inspector for review.

The inspector can evaluate findings before they become part of the final inspection record.

The intended workflow is:

AI / OCR Detection
        ↓
Automated Screening
        ↓
Evidence + Confidence
        ↓
Inspector Review
        ↓
Verification / Decision

The system therefore assists enforcement officials rather than replacing their judgment.

---

11. Inspection Repository

The backend maintains structured inspection information including:

- Products
- Inspections
- Uploaded images
- Extracted declarations
- Compliance results
- Potential violations
- Evidence
- Inspection notes
- Reports
- Inspection history

This provides a foundation for maintaining a searchable inspection record rather than treating every scan as an isolated analysis.

---

12. Reports

The system supports generation of digital inspection/compliance reports.

Reports can contain relevant inspection information, extracted declarations, compliance findings, evidence, and verification information.

The reporting workflow is integrated with the inspection record so that analyzed products can be converted into a documented inspection output.

---

13. Dashboard

The administrative/inspection interface provides visibility into information such as:

- Inspection activity
- Compliance status
- Potential violations
- Product records
- Inspection history
- Compliance trends
- Generated reports

The dashboard provides a high-level view of the inspection system rather than requiring users to inspect every record individually.

---

Compliance Status Model

The system uses explicit status values to distinguish different outcomes.

Status| Meaning
"COMPLIANT"| The applicable check was successfully evaluated and no issue was identified by the screening engine.
"POTENTIAL_VIOLATION"| The system identified an issue that may indicate non-compliance and requires appropriate verification.
"NEEDS_MANUAL_REVIEW"| Available evidence or confidence is insufficient for an automated conclusion.
"NOT_APPLICABLE"| The requirement does not apply based on the available applicability determination.
"NOT_DETECTED"| The expected information was not detected by the extraction pipeline.
"ANALYSIS_FAILED"| The system could not successfully complete the relevant analysis.

These states are intentionally more expressive than a simple pass/fail model.

---

Architecture

The Phase 1 system follows a layered architecture:

┌─────────────────────────────────────────────┐
│              Frontend / UI                  │
│   Inspector Workflow • Dashboard • Reports  │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│                 Backend                     │
│        APIs • Business Logic • Orchestration│
└───────────────┬─────────────────┬───────────┘
                │                 │
                ▼                 ▼
┌──────────────────────┐   ┌───────────────────┐
│   AI / OCR Pipeline  │   │ Compliance Engine │
│                      │   │                   │
│ Image Processing     │   │ Rule Evaluation   │
│ OCR                  │   │ Applicability     │
│ Declaration          │   │ Confidence        │
│ Extraction           │   │ Status Generation │
└──────────────┬───────┘   └─────────┬─────────┘
               │                     │
               └──────────┬──────────┘
                          ▼
               ┌──────────────────────┐
               │ Structured Results   │
               │ + Evidence           │
               └──────────┬───────────┘
                          ▼
               ┌──────────────────────┐
               │ Inspection Repository│
               │ Products             │
               │ Inspections          │
               │ Findings             │
               │ Reports              │
               └──────────────────────┘

---

Technology Stack

The completed Phase 1 prototype uses the following major technologies/components:

Layer| Technology / Purpose
Frontend| Web-based inspector and administrative interface
Backend| FastAPI
Database / ORM| SQLAlchemy 2.0
Prototype Database| SQLite
API Documentation| FastAPI / OpenAPI ("/docs")
AI / OCR| OCR and computer-vision based declaration extraction pipeline
Compliance Engine| Structured rule-based compliance evaluation
File Handling| Local image/evidence storage for the prototype
Reporting| Digital inspection/compliance report generation
Testing| Automated backend and integration-oriented tests
Configuration| Environment-based configuration with ".env.example"

The Phase 1 prototype is intentionally lightweight and suitable for demonstrating the complete workflow.

Docker is not required for the current Phase 1 implementation.

---

Backend

The backend provides APIs for the core inspection workflow, including functionality for:

- Health checks
- Inspection management
- Product information
- Image handling
- Declaration extraction
- Compliance analysis
- Dashboard summaries
- Reports
- Inspection notes
- Medical-device applicability confirmation

The backend also provides a compatibility layer between the extraction output and compliance engine so that the AI/OCR pipeline and rule engine can evolve independently.

Health Check

The backend exposes a health endpoint for service verification.

GET /api/health

Interactive API documentation is available through FastAPI's generated documentation during local development:

/docs

---

Testing and Validation

The project includes automated validation of the backend and core workflows.

The final development process included validation of:

- API behavior
- Database operations
- Extraction payload compatibility
- Compliance workflow
- Multi-observation handling
- Conflicting declaration detection
- Medical-device applicability flow
- Inspection/report functionality
- Authentication/access-control related behavior
- Integration between major system components

The backend reached a validated test state with the project's automated test suite passing during final integration.

---

Project Structure

The repository contains the project's documentation, backend, frontend, AI/OCR, compliance, testing, and supporting implementation components.

A simplified representation is:

SIH26034/
│
├── README.md
├── PROJECT_STATE.md
├── CONTRIBUTING.md
├── .gitignore
├── .env.example
│
├── docs/
│   ├── PROJECT_SPEC.md
│   ├── REQUIREMENTS.md
│   ├── DEVELOPMENT_PLAN.md
│   ├── PCR_Compliance_Rules.md
│   └── Confidence_Status_Schema.md
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── ...
│   ├── tests/
│   └── ...
│
├── frontend/
│   └── ...
│
├── AI / OCR components
│   └── ...
│
├── compliance components
│   └── ...
│
└── testing / validation
    └── ...

The exact directory structure may contain additional implementation-specific files and modules.

---

Legal and Compliance Design

The compliance engine is designed around verified provisions of the applicable Legal Metrology framework.

The primary legal reference framework for the project includes:

- Legal Metrology Act, 2009
- Legal Metrology (Packaged Commodities) Rules, 2011
- Relevant amendments and notifications
- Authoritative material published by the relevant government authorities

The project maintains a separation between:

1. Legal interpretation and verification
2. Engineering representation of requirements
3. Automated screening
4. Human verification

This separation is intended to reduce the risk of treating an engineering assumption or uncertain OCR result as a legally confirmed conclusion.

---

Legal Disclaimer

This project is a software-assisted compliance screening and inspection-support system.

The output of OCR, computer vision, automated rules, and other AI-assisted components is not inherently a legally conclusive determination.

A finding such as:

POTENTIAL_VIOLATION

means that the system has identified information that may warrant further investigation. It does not, by itself, establish a legally confirmed violation.

Similarly:

NOT_DETECTED

does not necessarily mean that a declaration is legally absent. It may indicate that the system was unable to detect the declaration from the available input.

Final determination should be made by an appropriately authorized enforcement official based on the applicable law, the actual package, supporting evidence, and relevant government guidance.

---

Design Principles

The system was developed around several principles:

1. Human-in-the-loop

Automated analysis assists inspectors instead of replacing them.

2. Confidence-aware decisions

Uncertain detections should be surfaced as uncertainty rather than presented as facts.

3. Evidence-first analysis

Findings should be traceable to the underlying image, extracted text, and applicable requirement wherever possible.

4. Explicit applicability

Requirements should only be evaluated when they are applicable to the product and inspection context.

5. No silent assumptions

The system should avoid silently converting missing information, uncertain OCR, or ambiguous product classification into a definitive legal conclusion.

6. Separation of AI and legal logic

OCR/CV is responsible for extracting observations.

The compliance engine is responsible for evaluating structured observations against defined requirements.

7. Reviewability

Automated findings should be understandable and reviewable by an inspector.

---

Team

Member| Role| Primary Responsibility
P1| AI / OCR| Computer vision, OCR and declaration extraction
P2| Compliance| Legal rule mapping, compliance logic and compliance engine
P3| Backend| APIs, database, backend architecture and system integration
P4| Frontend / UX| Inspector-facing interface, dashboard and user experience
P5| Security & Testing| Security validation, access-control testing and QA
P6| Deployment & Polish| Deployment/infra work, final QA and UI/UX polish

The final prototype was produced through integration of these components into the main project branch.

---

Development Workflow

During development, the team used a member-oriented Git workflow with separate development branches and integration into "main".

Conceptually:

                         ┌── p1
                         ├── p2
                         ├── p3
                         ├── p4
main / integration ──────┼── p5
                         └── p6

The project has now reached the integrated Phase 1 prototype stage, with the completed work consolidated into the main project state.

---

Phase 2 — Future Expansion

If selected for the national-level stage of Smart India Hackathon, the Phase 1 prototype can be extended into a larger field-inspection platform.

A possible Phase 2 architecture is:

                    BACKEND PLATFORM
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
      INSPECTOR MOBILE APP       ADMIN WEB PORTAL
              │                         │
        Camera Scanning             Dashboard
        Field Inspection            Analytics
        Evidence Capture            Inspections
        Reports                     Reports
        Field Data                  Management
              │                         │
              └────────────┬────────────┘
                           ▼
                  CENTRALIZED PLATFORM

Potential future capabilities include:

- Native mobile field inspection
- Camera-based real-time scanning
- Barcode/product identification
- Offline or low-connectivity operation
- Synchronization of field inspections
- Advanced computer-vision models
- Improved OCR
- Expanded product and declaration coverage
- Expanded rule coverage
- Multi-level administrative access
- Centralized inspection management
- Advanced analytics
- Large-scale deployment
- Cloud-based infrastructure
- Multilingual support

These features are future expansion opportunities and are not represented as completed Phase 1 functionality.

---

Phase 1 Limitations

The internal hackathon prototype is intentionally limited in scope.

Important limitations include:

- OCR/CV performance depends on image quality, lighting, orientation, packaging design, and text visibility.
- Automated extraction may produce incorrect or incomplete observations.
- Legal applicability may require contextual information unavailable to the system.
- Visual characteristics such as readability and contrast cannot always be conclusively determined from an image.
- Not every possible packaged commodity or legal provision is covered.
- Automated findings require appropriate human verification.
- The Phase 1 deployment is a prototype rather than a production-scale government system.
- Local storage/database components used for the prototype can be replaced with scalable infrastructure in a future deployment.

---

Security Considerations

The project treats security as part of the system design rather than as an afterthought.

The prototype includes consideration of:

- Authentication
- Role-based access
- Authorization
- Input validation
- API security
- Access-control testing
- Secret management
- Environment-based configuration
- Protection against accidental exposure of credentials
- Separation of development/runtime artifacts from source control

Secrets such as API keys, passwords, and tokens should never be committed to the repository.

---

Repository Hygiene

The repository excludes runtime and sensitive artifacts through ".gitignore".

Examples include:

.env
__pycache__/
*.pyc
*.db
runtime-generated files
local uploads

Development and deployment-specific secrets should be supplied through environment configuration rather than committed to Git.

---

References

Primary Legal References

- Legal Metrology Act, 2009
- Legal Metrology (Packaged Commodities) Rules, 2011
- Relevant amendments and notifications
- Authoritative publications of the Department of Consumer Affairs / Legal Metrology authorities

Official Reference

Ministry / Department of Consumer Affairs — Legal Metrology:

https://consumeraffairs.gov.in/pages/legal-metrology-act

---

Project Status

Project: SIH26034 — Packaged Commodity Compliance System

Event: Smart India Hackathon 2026

Current Phase: Phase 1 — Internal Hackathon Prototype

Status: Completed

Phase 1 completion includes:

- [x] Project requirements and specification
- [x] Compliance-rule schema and mapping
- [x] AI/OCR extraction pipeline integration
- [x] Structured declaration representation
- [x] Compliance engine
- [x] Confidence-aware compliance states
- [x] Multi-observation handling
- [x] Declaration conflict detection
- [x] Medical-device applicability handling
- [x] Evidence-oriented findings
- [x] Human verification workflow
- [x] Backend APIs
- [x] Database and inspection persistence
- [x] Frontend inspection workflow
- [x] Dashboard
- [x] Report generation
- [x] Security/access-control validation
- [x] Automated testing
- [x] Final integration and QA

---

Final Note

SIH26034 demonstrates how OCR, computer vision, structured rule engines, confidence-aware decision making, and human verification can be combined into a practical compliance-screening workflow for packaged commodities.

The Phase 1 prototype is intended to demonstrate the feasibility of an end-to-end digital inspection workflow while maintaining an important distinction between automated screening and final legal determination.

The architecture provides a foundation that can be expanded into a production-oriented mobile and administrative inspection platform if the project proceeds to the national stage.