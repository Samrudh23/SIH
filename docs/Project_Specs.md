## 1. Project Overview

**Problem Statement:**  
**Software System to check compliance of Packaged Commodities under Legal Metrology (Packaged Commodities) Rules, 2011 by scanning products, images and labels.**

SIH26034 proposes a software system that assists enforcement officials in checking packaged commodities for potential non-compliance with the applicable requirements of the Legal Metrology framework.

The system will use **computer vision, OCR, information extraction, and rule-based validation** to analyze package images and product information, identify relevant mandatory declarations, compare extracted information against applicable requirements, and present potential violations with supporting evidence.

The system is intended to function as a **compliance screening and inspection-support tool**, with human verification remaining an important part of the workflow.

---

# 2. Problem Context

Packaged commodities are sold in large volumes across:

- Retail stores
    
- Supermarkets
    
- Wholesale markets
    
- E-commerce platforms
    
- Other commercial channels
    

Applicable packaged commodities are required to carry prescribed declarations and information. These declarations are important for:

- Consumer transparency
    
- Fair trade
    
- Price transparency
    
- Quantity disclosure
    
- Manufacturer/packer/importer identification
    
- Consumer grievance mechanisms
    
- Regulatory enforcement
    

Traditional inspection processes can require officials to manually examine large numbers of products and labels.

This creates several challenges:

1. Large inspection volumes.
    
2. Time-consuming manual examination.
    
3. Difficulty identifying small or poorly positioned text.
    
4. Repetitive verification work.
    
5. Difficulty maintaining structured inspection histories.
    
6. Difficulty aggregating violations across inspections.
    
7. Limited automation for preliminary screening.
    

SIH26034 aims to reduce this burden by providing an automated first-level screening system.

---

# 3. Product Vision

> **Build an AI-assisted inspection platform that can transform package images into structured compliance findings and evidence, allowing enforcement officials to inspect packaged commodities faster and more consistently.**

The system should not simply answer:

> "Is this product legal?"

Instead, it should provide:

> "Here is what we detected, here is the applicable requirement being checked, here is the evidence, and here is the potential issue that requires review."

---

# 4. Target Users

## 4.1 Primary User — Enforcement Inspector

An inspector should be able to:

- Create an inspection.
    
- Upload or capture product images.
    
- Analyze package labels.
    
- Review extracted declarations.
    
- View potential violations.
    
- Inspect supporting evidence.
    
- Correct extraction errors where appropriate.
    
- Confirm/reject findings.
    
- Generate an inspection report.
    
- Access previous inspection records.
    

---

## 4.2 Administrative User

An administrator/supervisor should be able to:

- View inspection activity.
    
- Search inspection records.
    
- Monitor compliance trends.
    
- Review violations.
    
- Access generated reports.
    
- Monitor inspectors and inspection activity where applicable.
    
- Manage system-level configuration where implemented.
    

---

## 4.3 Future Users

The Phase 2 system may support additional administrative roles and organizational hierarchies.

These should not be unnecessarily implemented in Phase 1.

---

# 5. Product Scope

## Phase 1 — Internal Hackathon

The first product will be a **web-based prototype**.

The primary objective is to demonstrate a complete working workflow:

```
Product Image
     ↓
Image Upload
     ↓
Image Processing
     ↓
OCR / Computer Vision
     ↓
Declaration Extraction
     ↓
Applicable Rule Identification
     ↓
Compliance Validation
     ↓
Potential Findings
     ↓
Evidence
     ↓
Human Verification
     ↓
Inspection Record
     ↓
Report
     ↓
Dashboard / History
```

The Phase 1 product should prioritize a convincing end-to-end demonstration over excessive feature breadth.

---

# 6. Phase 1 MVP

The minimum viable product should demonstrate:

### Input

- Product/package image upload.
    
- Support for one or more images where practical.
    
- Basic image quality handling.
    

### Analysis

- OCR/text extraction.
    
- Detection of relevant declaration text.
    
- Extraction of structured fields.
    
- Confidence information where available.
    

### Compliance

- Identification of applicable checks.
    
- Rule-based validation.
    
- Missing declaration detection.
    
- Potentially invalid/non-compliant declaration detection.
    
- Clear distinction between:
    
    - Compliant
        
    - Potentially non-compliant
        
    - Unclear / requires review
        
    - Not applicable
        

### Evidence

- Original image.
    
- Relevant image region where available.
    
- Extracted text.
    
- Finding explanation.
    
- Applicable rule/reference.
    
- Detection confidence where available.
    

### Inspector Review

- Review extracted information.
    
- Review potential findings.
    
- Accept/reject/correct findings.
    
- Add inspection notes.
    

### Records

- Save inspection.
    
- Save product information.
    
- Save analysis results.
    
- Save evidence.
    
- Retrieve previous inspections.
    

### Reports

- Generate compliance/inspection report.
    
- Export PDF.
    
- Include evidence and findings.
    

### Dashboard

- Basic inspection statistics.
    
- Compliance status.
    
- Potential violations.
    
- Inspection history.
    
- Search/filter functionality where feasible.
    

---

# 7. Core System Workflow

## 7.1 Create Inspection

The inspector begins a new inspection.

```
New Inspection
      ↓
Product Information
      ↓
Upload/Capture Images
```

---

## 7.2 Image Analysis

The system evaluates the submitted images.

Potential processing steps:

```
Input Image
    ↓
Quality Assessment
    ↓
Preprocessing
    ↓
Text / Region Detection
    ↓
OCR
    ↓
Text Structuring
```

---

## 7.3 Declaration Extraction

OCR output should be transformed into structured information.

Potential fields include:

```
Product Name
Manufacturer
Packer
Importer
Address
Net Quantity
MRP
Date Information
Consumer Care Information
Other Applicable Declarations
```

The exact fields and applicability must be determined from verified requirements.

---

# 8. Compliance Analysis

The compliance layer should operate separately from the OCR layer.

```
                 IMAGE
                   ↓
                 OCR/CV
                   ↓
            Extracted Data
                   ↓
          ┌─────────────────┐
          │ Compliance      │
          │ Rule Engine     │
          └─────────────────┘
                   ↓
             Findings
```

This separation is important.

### AI should primarily answer:

> "What appears to be present in the image?"

### The compliance engine should answer:

> "Does the extracted information satisfy the applicable rule/check?"

### The inspector should ultimately determine:

> "Should the finding be accepted for the inspection?"

---

# 9. Compliance Finding Model

Each finding should ideally contain:

```
Finding ID
Inspection ID
Rule ID
Category
Requirement
Observed Value
Expected Condition
Status
Severity/Priority
Evidence
Confidence
Explanation
Inspector Verification
Notes
```

Example conceptual result:

```
Finding:
MRP Declaration

Observed:
₹XXX

Status:
REQUIRES REVIEW

Reason:
The system detected an MRP-related declaration but
requires verification of its format/presentation.

Evidence:
Image region + extracted text

Rule:
[Verified Rule Reference]
```

The system must avoid presenting uncertain AI results as definitive legal conclusions.

---

# 10. Evidence Model

Evidence is a core part of the product.

For every potential issue, the system should attempt to preserve:

- Source image.
    
- Image region/bounding box.
    
- Extracted text.
    
- Relevant rule/check.
    
- Detection confidence.
    
- Explanation.
    
- Inspector comments.
    
- Verification status.
    

Conceptually:

```
Potential Violation
        │
        ├── Source Image
        ├── Highlighted Region
        ├── Extracted Text
        ├── Rule Reference
        ├── Explanation
        └── Verification
```

---

# 11. Human-in-the-Loop Design

The system should not be designed as a fully autonomous legal decision-maker.

Instead:

```
AI Detection
     ↓
Potential Finding
     ↓
Inspector Review
     ↓
Confirmed / Rejected / Corrected
     ↓
Final Inspection Record
```

This approach also provides a practical mechanism for handling:

- OCR errors
    
- Poor image quality
    
- Ambiguous declarations
    
- Category-specific requirements
    
- Uncertain rule applicability
    

---

# 12. Inspection Repository

Each inspection should be represented as a structured record.

Conceptually:

```
Inspection
│
├── Inspector
├── Date / Time
├── Product
│
├── Images
│
├── Extracted Declarations
│
├── Compliance Checks
│
├── Findings
│
├── Evidence
│
├── Verification
│
└── Report
```

The repository should support retrieval based on appropriate fields such as:

- Inspection ID
    
- Product
    
- Date
    
- Compliance status
    
- Finding type
    
- Inspector
    
- Other relevant metadata
    

---

# 13. Reporting

Reports should provide a clear summary of an inspection.

A report may include:

### Inspection Information

- Inspection ID
    
- Date/time
    
- Inspector
    
- Product information
    

### Analysis

- Images analyzed
    
- Extracted declarations
    
- Compliance checks performed
    

### Findings

- Potential violations
    
- Applicable requirement
    
- Observed information
    
- Evidence
    
- Verification status
    

### Final Assessment

The report should clearly distinguish between:

- Automated screening results.
    
- Inspector-verified findings.
    

### Attachments

Relevant photographs/evidence should be included where practical.

---

# 14. Dashboard

The dashboard should provide an overview of inspection activity.

Potential metrics:

```
Total Inspections
Compliant
Potentially Non-Compliant
Requires Review
Recent Inspections
Common Finding Categories
```

Potential visualizations:

- Compliance distribution
    
- Inspection activity over time
    
- Finding categories
    
- Product/category distribution where available
    

The dashboard should prioritize **actionable information** rather than decorative analytics.

---

# 15. Authentication & Roles

The final system should support secure authentication and role-based access.

Phase 1 may use a simplified implementation suitable for demonstration.

Potential roles:

```
Inspector
Supervisor
Administrator
```

Permissions should follow the principle of least privilege.

---

# 16. AI System Requirements

The AI/OCR pipeline should ideally return structured results rather than only raw text.

Conceptual output:

```
{
  "field": "mrp",
  "value": "₹100",
  "confidence": 0.94,
  "source_region": {
    "x": 120,
    "y": 240,
    "width": 180,
    "height": 60
  }
}
```

The exact schema will be finalized during architecture development.

The pipeline should preserve enough information to allow downstream components to:

- Validate fields.
    
- Display evidence.
    
- Explain findings.
    
- Handle uncertainty.
    

---

# 17. Font Size & Readability

Font-size and readability analysis are technically challenging because package photographs may have:

- Perspective distortion.
    
- Unknown physical scale.
    
- Variable camera distance.
    
- Curved surfaces.
    
- Reflections.
    
- Shadows.
    
- Compression.
    
- Different print technologies.
    

Therefore, the system should distinguish between:

### Directly measurable properties

Properties that can be estimated reliably from available information.

### Estimated properties

Properties that can only be approximated.

### Requires physical verification

Properties that cannot be reliably established from an ordinary photograph alone.

The implementation should avoid claiming legally conclusive font-size measurements unless the system has sufficient information to support the measurement.

---

# 18. Product Categories

The system should be designed so that compliance rules can vary according to:

- Product category.
    
- Applicable conditions.
    
- Packaging characteristics.
    
- Other legally relevant factors.
    

The architecture should therefore avoid hard-coding every requirement into the UI.

Instead:

```
Product Category
      ↓
Applicable Rules
      ↓
Checks
      ↓
Findings
```

---

# 19. Non-Functional Goals

The prototype should prioritize:

### Usability

An inspector should understand the result without needing technical knowledge.

### Explainability

Every potential finding should have an understandable reason.

### Reliability

The system should fail gracefully when OCR or analysis is uncertain.

### Maintainability

AI, compliance logic, backend, and UI should remain reasonably separated.

### Security

Sensitive information and credentials must not be exposed.

### Extensibility

The architecture should allow Phase 2 expansion without rebuilding the entire system.

### Performance

The prototype should provide reasonable response times for normal package-image analysis.

---

# 20. Out of Scope for Phase 1

The following should not become blockers for the internal hackathon:

- Full nationwide deployment.
    
- Production-scale infrastructure.
    
- Native mobile application.
    
- Offline-first field operation.
    
- Complete coverage of every possible packaged commodity.
    
- Perfect OCR accuracy.
    
- Fully autonomous legal enforcement decisions.
    
- Complex organizational hierarchy.
    
- Advanced predictive analytics.
    
- Large-scale automated web crawling.
    
- Integration with government systems unless explicitly required and feasible.
    

---

# 21. Phase 2 Vision

If the project advances to the national stage, the system can evolve into a broader inspection platform.

```
                  CENTRAL PLATFORM
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
       INSPECTOR APP          ADMIN PORTAL
             │                     │
        Camera Scan            Dashboard
        Field Inspection       Analytics
        Evidence               Reports
        Verification           Management
             │                     │
             └──────────┬──────────┘
                        ▼
                    BACKEND
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
       AI/CV          RULES          DATABASE
```

Potential additions:

- Mobile camera scanning.
    
- Offline capability.
    
- Synchronization.
    
- Barcode/product identification.
    
- Improved computer vision.
    
- Larger rule repository.
    
- Advanced analytics.
    
- Multi-level administration.
    
- Centralized inspection management.
    
- Production-grade security and infrastructure.
    

---

# 22. Success Criteria

The Phase 1 prototype should be considered successful if it can demonstrate:

1. A package image can be submitted.
    
2. The system can extract relevant information from the image.
    
3. Extracted information can be mapped to compliance checks.
    
4. At least a meaningful subset of applicable checks can be demonstrated.
    
5. Potential issues can be identified.
    
6. Evidence can be shown for findings.
    
7. An inspector can review findings.
    
8. An inspection can be saved.
    
9. A report can be generated.
    
10. Previous inspections can be retrieved.
    
11. The dashboard can summarize inspection information.
    
12. The complete workflow can be demonstrated reliably.
    

---

# 23. Guiding Principles

### Principle 1 — Evidence over assertion

Every important finding should be supported by evidence.

### Principle 2 — AI assists, rules validate

AI should primarily handle perception and extraction; deterministic compliance logic should handle rule evaluation where possible.

### Principle 3 — Human verification matters

The system assists inspectors rather than replacing statutory decision-making.

### Principle 4 — Traceable compliance

Compliance checks should be traceable to verified source material.

### Principle 5 — MVP first

Build the complete core workflow before adding advanced features.

### Principle 6 — Explainability

A user should be able to understand why something was flagged.

### Principle 7 — Design for expansion

Phase 1 should establish foundations that can support the Phase 2 mobile + admin system.

---

# 24. Specification Status

**Version:** 0.1  
**Stage:** Initial Product Specification  
**Phase:** Internal Hackathon — Phase 1

This document is a living specification.

Requirements may change as:

- Official requirements are analyzed.
    
- Technical feasibility is evaluated.
    
- Prototype results become available.
    
- Team architecture decisions are finalized.
    
- SIH feedback is received.
    

Major changes should be documented rather than silently changing the product scope.