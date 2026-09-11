from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.inspection import InspectionModel, ReportModel
from app.schemas.common import WorkflowStatus

class ReportService:
    def generate_report_data(self, db: Session, inspection_id: str) -> dict:
        inspection = db.query(InspectionModel).filter(InspectionModel.id == inspection_id).first()
        if not inspection:
            raise HTTPException(status_code=404, detail=f"Inspection '{inspection_id}' not found.")

        result = inspection.compliance_result
        extraction = inspection.extraction
        images = inspection.images or []

        report_data = {
            "title": "LEGAL METROLOGY (PACKAGED COMMODITIES) SCREENING REPORT",
            "statutory_framework": "Legal Metrology Act, 2009 & Packaged Commodities Rules, 2011",
            "system_identifier": "SIH26034 Automated Inspection Support System",
            "disclaimer": (
                "LEGAL DISCLAIMER: This report is an AI-assisted compliance screening record. "
                "The findings contained herein reflect automated preliminary observations and do not "
                "constitute a final statutory determination until verified and confirmed by an authorized "
                "Legal Metrology Enforcement Officer."
            ),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "inspection": {
                "id": inspection.id,
                "created_at": inspection.created_at.isoformat(),
                "inspector_id": inspection.inspector_id,
                "product_name": inspection.product_name or "N/A",
                "brand_name": inspection.brand_name or "N/A",
                "commodity_category": inspection.commodity_category or "Standard Pre-packaged Commodity",
                "workflow_status": inspection.status,
                "overall_compliance_status": inspection.compliance_status,
                "image_coverage": inspection.image_coverage,
                "notes": inspection.notes or "None",
            },
            "evidence_images": [
                {
                    "evidence_id": img.id,
                    "file_name": img.file_name,
                    "image_type": img.image_type,
                    "file_size_bytes": img.file_size_bytes,
                    "uploaded_at": img.uploaded_at.isoformat(),
                }
                for img in images
            ],
            "extracted_declarations": extraction.payload if extraction else {},
            "compliance_evaluation": {
                "overall_status": result.overall_status if result else "NOT_EVALUATED",
                "engine_version": result.engine_version if result else "N/A",
                "evaluated_at": result.evaluated_at.isoformat() if result else None,
                "summary_counts": result.summary_counts if result else {},
                "findings": result.rule_results if result else [],
            },
        }

        # Persist report record
        report_record = ReportModel(
            inspection_id=inspection.id,
            report_format="JSON",
            status="GENERATED",
            content_summary=report_data["inspection"],
        )
        db.add(report_record)
        if inspection.status != WorkflowStatus.REPORT_GENERATED.value:
            inspection.status = WorkflowStatus.REPORT_GENERATED.value
        db.commit()

        return report_data

    def generate_html_report(self, db: Session, inspection_id: str) -> str:
        data = self.generate_report_data(db, inspection_id)
        insp = data["inspection"]
        comp = data["compliance_evaluation"]
        findings = comp.get("findings", [])

        status_color = {
            "COMPLIANT": "#16a34a",
            "POTENTIAL_VIOLATION": "#dc2626",
            "NEEDS_MANUAL_REVIEW": "#d97706",
            "NOT_APPLICABLE": "#4b5563",
            "NOT_DETECTED": "#9333ea",
            "ANALYSIS_FAILED": "#000000",
        }.get(insp["overall_compliance_status"], "#2563eb")

        findings_rows = ""
        for f in findings:
            badge_color = {
                "COMPLIANT": "#16a34a",
                "POTENTIAL_VIOLATION": "#dc2626",
                "NEEDS_MANUAL_REVIEW": "#d97706",
                "NOT_APPLICABLE": "#4b5563",
                "NOT_DETECTED": "#9333ea",
            }.get(f.get("status"), "#6b7280")

            findings_rows += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; font-weight: bold;">{f.get('rule_id')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">
                    <span style="background-color: {badge_color}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">
                        {f.get('status')}
                    </span>
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; font-size: 13px;">{f.get('detected_value') or '—'}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; font-size: 12px; color: #4b5563;">{f.get('explanation_for_inspector')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; font-size: 11px; color: #6b7280;">{f.get('rule_version', {}).get('clause', 'N/A')}</td>
            </tr>
            """

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Compliance Report — {insp['id']}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 40px; color: #1f2937; line-height: 1.5; }}
        .header {{ border-bottom: 3px solid #1e3a8a; padding-bottom: 15px; margin-bottom: 25px; }}
        .title {{ font-size: 22px; font-weight: bold; color: #1e3a8a; margin: 0; }}
        .subtitle {{ font-size: 13px; color: #4b5563; margin-top: 4px; }}
        .disclaimer {{ background-color: #fef2f2; border-left: 4px solid #dc2626; padding: 12px; margin: 20px 0; font-size: 12px; color: #991b1b; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px; }}
        .card {{ background: #f9fafb; padding: 15px; border-radius: 6px; border: 1px solid #e5e7eb; }}
        .card h3 {{ margin-top: 0; font-size: 14px; color: #374151; border-bottom: 1px solid #e5e7eb; padding-bottom: 6px; }}
        .status-badge {{ display: inline-block; background-color: {status_color}; color: white; padding: 6px 14px; border-radius: 6px; font-size: 14px; font-weight: bold; margin-top: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }}
        th {{ background-color: #f3f4f6; text-align: left; padding: 10px; border-bottom: 2px solid #d1d5db; font-size: 12px; text-transform: uppercase; }}
        .footer {{ margin-top: 40px; font-size: 11px; color: #9ca3af; border-top: 1px solid #e5e7eb; padding-top: 15px; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1 class="title">{data['title']}</h1>
        <div class="subtitle">{data['statutory_framework']} &bull; {data['system_identifier']}</div>
    </div>

    <div class="disclaimer">
        <strong>IMPORTANT:</strong> {data['disclaimer']}
    </div>

    <div class="grid">
        <div class="card">
            <h3>Inspection Overview</h3>
            <div><strong>Inspection ID:</strong> {insp['id']}</div>
            <div><strong>Date Generated:</strong> {data['generated_at']}</div>
            <div><strong>Inspector:</strong> {insp['inspector_id']}</div>
            <div><strong>Product Name:</strong> {insp['product_name']}</div>
            <div><strong>Brand:</strong> {insp['brand_name']}</div>
            <div><strong>Commodity Category:</strong> {insp['commodity_category']}</div>
            <div><strong>Notes:</strong> {insp['notes']}</div>
        </div>
        <div class="card">
            <h3>Automated Screening Summary</h3>
            <div>Overall Result:</div>
            <div class="status-badge">{insp['overall_compliance_status']}</div>
            <div style="margin-top: 15px;"><strong>Total Rules Checked:</strong> {comp.get('summary_counts', {}).get('total_rules', 15)}</div>
            <div><strong>Compliant Rules:</strong> {comp.get('summary_counts', {}).get('compliant', 0)}</div>
            <div><strong>Potential Violations:</strong> {comp.get('summary_counts', {}).get('potential_violations', 0)}</div>
            <div><strong>Manual Review Items:</strong> {comp.get('summary_counts', {}).get('needs_manual_review', 0)}</div>
        </div>
    </div>

    <h3>Detailed Rule Findings</h3>
    <table>
        <thead>
            <tr>
                <th style="width: 15%;">Rule ID</th>
                <th style="width: 18%;">Status</th>
                <th style="width: 25%;">Observed Value</th>
                <th style="width: 27%;">Inspector Explanation</th>
                <th style="width: 15%;">Legal Reference</th>
            </tr>
        </thead>
        <tbody>
            {findings_rows}
        </tbody>
    </table>

    <div class="footer">
        Generated by SIH26034 Backend Prototype &bull; For Official Enforcement Use Only
    </div>
</body>
</html>
"""
        return html

report_service = ReportService()
