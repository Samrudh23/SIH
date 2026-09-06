/**
 * TypeScript Data Models for SIH26034 — Legal Metrology Compliance Scanner
 * Strictly matching backend schemas in app/schemas/common.py, compliance.py, extraction.py, inspection.py
 */

export enum ResultState {
  COMPLIANT = "COMPLIANT",
  POTENTIAL_VIOLATION = "POTENTIAL_VIOLATION",
  NEEDS_MANUAL_REVIEW = "NEEDS_MANUAL_REVIEW",
  NOT_APPLICABLE = "NOT_APPLICABLE",
  NOT_DETECTED = "NOT_DETECTED",
  ANALYSIS_FAILED = "ANALYSIS_FAILED",
}

export enum WorkflowStatus {
  CREATED = "CREATED",
  IMAGE_UPLOADED = "IMAGE_UPLOADED",
  EXTRACTION_RECEIVED = "EXTRACTION_RECEIVED",
  ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE",
  REPORT_GENERATED = "REPORT_GENERATED",
  FAILED = "FAILED",
}

export interface BoundingBox {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface ImageCoverage {
  front: boolean;
  back: boolean;
  side: boolean;
  top: boolean;
}

export interface EvidenceObject {
  image_id?: string;
  bounding_box?: BoundingBox;
  raw_ocr_text?: string;
  crop_url?: string;
}

export interface ConflictItem {
  value: any;
  image_id?: string;
  location?: string;
  confidence?: number;
  raw_text?: string;
}

export interface ConflictObject {
  field: string;
  values_found: ConflictItem[];
  resolution: string; // "NEEDS_MANUAL_REVIEW"
  reason: string;
}

export interface RuleVersionMetadata {
  source: string;
  clause: string;
  gsr_number: string;
  verification_status: string;
  last_verified: string;
}

export interface RuleResult {
  rule_id: string;
  status: ResultState;
  detected_value?: string;
  normalized_value?: string;
  detection_confidence: number;
  applicability_confidence: number;
  reason: string;
  evidence?: EvidenceObject;
  explanation_for_inspector: string;
  conflicts?: ConflictObject;
  rule_version: RuleVersionMetadata;
}

export interface SummaryCounts {
  total_rules: number;
  compliant: number;
  potential_violations: number;
  needs_manual_review: number;
  not_applicable: number;
  not_detected: number;
  analysis_failed: number;
}

export interface ComplianceResult {
  inspection_id: string;
  overall_status: ResultState;
  summary_counts: SummaryCounts;
  rule_results: RuleResult[];
  evaluated_at: string;
  engine_version: string;
}

export interface ExtractedField {
  value?: any;
  raw_text: string;
  confidence: number;
  bounding_box?: BoundingBox;
  image_id?: string;
  location?: string;
}

export interface NetQuantityExtraction {
  value?: number;
  unit?: string;
  raw_text: string;
  confidence: number;
  bounding_box?: BoundingBox;
  image_id?: string;
  surface_location?: string;
  location?: string;
  qualifiers?: string[];
  quiet_zone_clear?: boolean;
}

export interface MRPExtraction {
  value?: number;
  currency?: string;
  tax_inclusivity?: boolean;
  raw_text: string;
  confidence: number;
  bounding_box?: BoundingBox;
  image_id?: string;
  surface_location?: string;
  location?: string;
  is_sticker?: boolean;
  original_mrp?: number;
}

export interface DateExtraction {
  month?: string;
  year?: string;
  raw_text: string;
  confidence: number;
  bounding_box?: BoundingBox;
  image_id?: string;
  is_rubber_stamped?: boolean;
  has_overwriting?: boolean;
}

export interface AddressExtraction {
  premises?: string;
  street?: string;
  city?: string;
  state?: string;
  pin_code?: string;
  raw_text: string;
  confidence: number;
  bounding_box?: BoundingBox;
  image_id?: string;
}

export interface ConsumerCareExtraction {
  name_or_office?: string;
  address?: string;
  phone?: string;
  email?: string;
  raw_text: string;
  confidence: number;
  bounding_box?: BoundingBox;
  image_id?: string;
}

export interface ExtractionPayload {
  inspection_id?: string;
  product_name?: ExtractedField;
  commodity_category?: ExtractedField;
  manufacturer?: AddressExtraction;
  packer?: AddressExtraction;
  importer?: AddressExtraction;
  country_of_origin?: ExtractedField;
  is_importer_on_pdp?: boolean;
  net_quantity?: NetQuantityExtraction;
  net_quantity_observations?: NetQuantityExtraction[];
  mrp?: MRPExtraction;
  mrp_observations?: MRPExtraction[];
  date_of_manufacture?: DateExtraction;
  consumer_care?: ConsumerCareExtraction;
  medical_device_markers?: ExtractedField;
  non_standard_size_disclaimer?: ExtractedField;
  stickers_detected?: ExtractedField[];
  contrast_analysis?: ExtractedField;
  image_coverage: ImageCoverage;
  raw_ocr_blocks?: any[];
}

export interface InspectionResponse {
  id: string;
  created_at: string;
  updated_at: string;
  status: WorkflowStatus;
  compliance_status?: string;
  product_name?: string;
  brand_name?: string;
  commodity_category?: string;
  inspector_id: string;
  image_coverage: ImageCoverage;
  notes?: string;
  images_count: number;
  has_extraction: boolean;
  has_result: boolean;
}

export interface DashboardSummaryResponse {
  total_inspections: number;
  compliant_inspections: number;
  potential_violations: number;
  needs_manual_review: number;
  not_applicable: number;
  analysis_failed: number;
  pending_analysis: number;
  top_violated_rules: Array<{ rule_id: string; count: number; rule_name: string }>;
  recent_inspections: InspectionResponse[];
}
