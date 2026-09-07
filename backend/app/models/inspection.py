import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    Text,
    ForeignKey,
    JSON,
    Boolean,
)
from sqlalchemy.orm import relationship

from app.database.base import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class InspectionModel(Base):
    __tablename__ = "inspections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    status = Column(String(32), default="CREATED", nullable=False)
    compliance_status = Column(String(32), default="PENDING", nullable=False)
    product_name = Column(String(255), nullable=True)
    brand_name = Column(String(255), nullable=True)
    commodity_category = Column(String(128), nullable=True)
    inspector_id = Column(String(64), default="inspector_default", nullable=False)
    image_coverage = Column(
        JSON,
        default=lambda: {"front": False, "back": False, "side": False, "top": False},
        nullable=False,
    )
    notes = Column(Text, nullable=True)
    is_medical_device_confirmed = Column(Boolean, nullable=True, default=None)
    metadata_json = Column(JSON, default=dict, nullable=False)

    # Relationships
    images = relationship("ImageEvidenceModel", back_populates="inspection", cascade="all, delete-orphan")
    extraction = relationship("ExtractionModel", back_populates="inspection", uselist=False, cascade="all, delete-orphan")
    compliance_result = relationship("ComplianceResultModel", back_populates="inspection", uselist=False, cascade="all, delete-orphan")
    reports = relationship("ReportModel", back_populates="inspection", cascade="all, delete-orphan")


class ImageEvidenceModel(Base):
    __tablename__ = "image_evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    inspection_id = Column(String(36), ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    original_file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(64), nullable=False)
    image_type = Column(String(32), default="package_image", nullable=False)
    uploaded_at = Column(DateTime, default=utc_now, nullable=False)
    metadata_json = Column(JSON, default=dict, nullable=False)

    inspection = relationship("InspectionModel", back_populates="images")


class ExtractionModel(Base):
    __tablename__ = "extractions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    inspection_id = Column(String(36), ForeignKey("inspections.id", ondelete="CASCADE"), unique=True, nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    inspection = relationship("InspectionModel", back_populates="extraction")


class ComplianceResultModel(Base):
    __tablename__ = "compliance_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    inspection_id = Column(String(36), ForeignKey("inspections.id", ondelete="CASCADE"), unique=True, nullable=False)
    overall_status = Column(String(32), nullable=False)
    summary_counts = Column(JSON, nullable=False)
    rule_results = Column(JSON, nullable=False)
    evaluated_at = Column(DateTime, default=utc_now, nullable=False)
    engine_version = Column(String(64), default="mock-v1.0.0", nullable=False)

    inspection = relationship("InspectionModel", back_populates="compliance_result")


class ReportModel(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    inspection_id = Column(String(36), ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False)
    report_format = Column(String(16), default="JSON", nullable=False)
    file_path = Column(String(512), nullable=True)
    status = Column(String(32), default="GENERATED", nullable=False)
    content_summary = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    inspection = relationship("InspectionModel", back_populates="reports")
