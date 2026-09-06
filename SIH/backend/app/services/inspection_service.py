from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from fastapi import HTTPException

from app.models.inspection import (
    InspectionModel,
    ImageEvidenceModel,
    ExtractionModel,
    ComplianceResultModel,
)
from app.schemas.inspection import (
    InspectionCreate,
    InspectionResponse,
)
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    RuleViolationMetric,
)
from app.schemas.common import WorkflowStatus, ResultState, ImageCoverage
from app.schemas.extraction import ExtractionPayload
from app.schemas.compliance import ComplianceResult
from app.services.compliance import get_compliance_engine

class InspectionService:
    def create_inspection(self, db: Session, data: InspectionCreate) -> InspectionModel:
        inspection = InspectionModel(
            product_name=data.product_name,
            brand_name=data.brand_name,
            commodity_category=data.commodity_category,
            inspector_id=data.inspector_id,
            image_coverage=data.image_coverage.model_dump(),
            metadata_json=data.metadata or {},
            status=WorkflowStatus.CREATED.value,
            compliance_status="PENDING",
        )
        db.add(inspection)
        db.commit()
        db.refresh(inspection)
        return inspection

    def get_inspection(self, db: Session, inspection_id: str) -> InspectionModel:
        inspection = db.query(InspectionModel).filter(InspectionModel.id == inspection_id).first()
        if not inspection:
            raise HTTPException(status_code=404, detail=f"Inspection '{inspection_id}' not found.")
        return inspection

    def list_inspections(
        self,
        db: Session,
        status: Optional[str] = None,
        compliance_status: Optional[str] = None,
        product_query: Optional[str] = None,
        has_violations: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[int, List[InspectionModel]]:
        query = db.query(InspectionModel)

        if status:
            query = query.filter(InspectionModel.status == status)
        if compliance_status:
            query = query.filter(InspectionModel.compliance_status == compliance_status)
        if has_violations is True:
            query = query.filter(InspectionModel.compliance_status == ResultState.POTENTIAL_VIOLATION.value)
        elif has_violations is False:
            query = query.filter(InspectionModel.compliance_status != ResultState.POTENTIAL_VIOLATION.value)
        if product_query:
            pattern = f"%{product_query}%"
            query = query.filter(
                (InspectionModel.product_name.ilike(pattern))
                | (InspectionModel.brand_name.ilike(pattern))
                | (InspectionModel.commodity_category.ilike(pattern))
            )

        total = query.count()
        items = query.order_by(desc(InspectionModel.created_at)).offset(skip).limit(limit).all()
        return total, items

    def add_image_evidence(
        self,
        db: Session,
        inspection_id: str,
        evidence_id: str,
        file_name: str,
        original_file_name: str,
        file_path: str,
        file_size_bytes: int,
        mime_type: str,
        image_type: str = "package_image",
    ) -> ImageEvidenceModel:
        inspection = self.get_inspection(db, inspection_id)
        evidence = ImageEvidenceModel(
            id=evidence_id,
            inspection_id=inspection.id,
            file_name=file_name,
            original_file_name=original_file_name,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
            mime_type=mime_type,
            image_type=image_type,
        )
        db.add(evidence)

        # Update inspection state
        if inspection.status == WorkflowStatus.CREATED.value:
            inspection.status = WorkflowStatus.IMAGE_UPLOADED.value
        inspection.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(evidence)
        return evidence

    def save_extraction(
        self,
        db: Session,
        inspection_id: str,
        payload: ExtractionPayload,
    ) -> ExtractionModel:
        inspection = self.get_inspection(db, inspection_id)

        # Merge extracted product info if not already set on inspection
        if payload.product_name and payload.product_name.value and not inspection.product_name:
            inspection.product_name = str(payload.product_name.value)
        if payload.commodity_category and payload.commodity_category.value and not inspection.commodity_category:
            inspection.commodity_category = str(payload.commodity_category.value)

        # Update coverage if provided
        if payload.image_coverage:
            inspection.image_coverage = payload.image_coverage.model_dump()

        # Check existing extraction
        existing = db.query(ExtractionModel).filter(ExtractionModel.inspection_id == inspection_id).first()
        payload_dict = payload.model_dump()
        payload_dict["inspection_id"] = inspection_id

        if existing:
            existing.payload = payload_dict
            existing.created_at = datetime.now(timezone.utc)
            extraction_record = existing
        else:
            extraction_record = ExtractionModel(
                inspection_id=inspection.id,
                payload=payload_dict,
            )
            db.add(extraction_record)

        inspection.status = WorkflowStatus.EXTRACTION_RECEIVED.value
        inspection.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(extraction_record)
        return extraction_record

    def run_compliance_analysis(
        self,
        db: Session,
        inspection_id: str,
        is_medical_device_confirmed: Optional[bool] = None,
    ) -> ComplianceResultModel:
        inspection = self.get_inspection(db, inspection_id)
        extraction_model = db.query(ExtractionModel).filter(ExtractionModel.inspection_id == inspection_id).first()
        if not extraction_model:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot analyze inspection '{inspection_id}': no extraction data has been submitted yet."
            )

        extraction_payload = ExtractionPayload.model_validate(extraction_model.payload)
        coverage = ImageCoverage(**inspection.image_coverage)

        # Invoke swappable compliance engine
        engine = get_compliance_engine()
        eval_result = engine.evaluate(
            extraction=extraction_payload,
            image_coverage=coverage,
            is_medical_device_confirmed=is_medical_device_confirmed,
        )

        # Persist or update result
        existing_result = db.query(ComplianceResultModel).filter(ComplianceResultModel.inspection_id == inspection_id).first()
        result_dict = eval_result.model_dump(mode="json")

        if existing_result:
            existing_result.overall_status = eval_result.overall_status.value
            existing_result.summary_counts = result_dict["summary_counts"]
            existing_result.rule_results = result_dict["rule_results"]
            existing_result.evaluated_at = datetime.now(timezone.utc)
            existing_result.engine_version = eval_result.engine_version
            result_record = existing_result
        else:
            result_record = ComplianceResultModel(
                inspection_id=inspection.id,
                overall_status=eval_result.overall_status.value,
                summary_counts=result_dict["summary_counts"],
                rule_results=result_dict["rule_results"],
                evaluated_at=datetime.now(timezone.utc),
                engine_version=eval_result.engine_version,
            )
            db.add(result_record)

        inspection.compliance_status = eval_result.overall_status.value
        inspection.status = WorkflowStatus.ANALYSIS_COMPLETE.value
        inspection.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(result_record)
        return result_record

    def update_notes(self, db: Session, inspection_id: str, notes: str) -> InspectionModel:
        inspection = self.get_inspection(db, inspection_id)
        inspection.notes = notes
        inspection.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(inspection)
        return inspection

    def get_dashboard_summary(self, db: Session) -> DashboardSummaryResponse:
        total = db.query(InspectionModel).count()
        compliant = db.query(InspectionModel).filter(InspectionModel.compliance_status == ResultState.COMPLIANT.value).count()
        violations = db.query(InspectionModel).filter(InspectionModel.compliance_status == ResultState.POTENTIAL_VIOLATION.value).count()
        needs_review = db.query(InspectionModel).filter(InspectionModel.compliance_status == ResultState.NEEDS_MANUAL_REVIEW.value).count()
        not_applicable = db.query(InspectionModel).filter(InspectionModel.compliance_status == ResultState.NOT_APPLICABLE.value).count()
        failed = db.query(InspectionModel).filter(InspectionModel.compliance_status == ResultState.ANALYSIS_FAILED.value).count()
        pending = db.query(InspectionModel).filter(InspectionModel.compliance_status == "PENDING").count()

        recent_records = db.query(InspectionModel).order_by(desc(InspectionModel.created_at)).limit(5).all()
        recent_items = [self.to_response(rec) for rec in recent_records]

        # Calculate top violated rules from compliance_results JSON
        all_results = db.query(ComplianceResultModel).all()
        violation_counts: dict = {}
        for r in all_results:
            rules = r.rule_results or []
            for item in rules:
                if item.get("status") == ResultState.POTENTIAL_VIOLATION.value:
                    rid = item.get("rule_id", "Unknown")
                    violation_counts[rid] = violation_counts.get(rid, 0) + 1

        top_rules = [
            RuleViolationMetric(rule_id=rid, count=cnt, rule_name=f"Compliance Rule {rid}")
            for rid, cnt in sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        return DashboardSummaryResponse(
            total_inspections=total,
            compliant_inspections=compliant,
            potential_violations=violations,
            needs_manual_review=needs_review,
            not_applicable=not_applicable,
            analysis_failed=failed,
            pending_analysis=pending,
            top_violated_rules=top_rules,
            recent_inspections=recent_items,
        )

    def to_response(self, record: InspectionModel) -> InspectionResponse:
        images_count = len(record.images) if record.images else 0
        has_extraction = record.extraction is not None
        has_result = record.compliance_result is not None
        coverage_data = record.image_coverage or {}

        return InspectionResponse(
            id=record.id,
            created_at=record.created_at,
            updated_at=record.updated_at,
            status=WorkflowStatus(record.status),
            compliance_status=record.compliance_status,
            product_name=record.product_name,
            brand_name=record.brand_name,
            commodity_category=record.commodity_category,
            inspector_id=record.inspector_id,
            image_coverage=ImageCoverage(**coverage_data),
            notes=record.notes,
            images_count=images_count,
            has_extraction=has_extraction,
            has_result=has_result,
        )

inspection_service = InspectionService()
