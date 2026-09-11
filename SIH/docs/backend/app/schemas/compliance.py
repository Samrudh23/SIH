from datetime import datetime, timezone
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, model_validator

from app.schemas.common import (
    ResultState,
    EvidenceObject,
    ConflictObject,
    RuleVersionMetadata,
)

# Static table from Confidence_Status_Schema.md Section 7
RULE_VERSION_METADATA_TABLE: Dict[str, RuleVersionMetadata] = {
    "REQ-MVP-01": RuleVersionMetadata(
        source="01_Packaged_Commodities_Rules_2011.pdf",
        clause="Rule 6(1); exemption under Rule 26",
        gsr_number="G.S.R. 202(E) (Principal)",
        verification_status="VERIFIED — VERBATIM",
        last_verified="2026-09-05",
    ),
    "REQ-MVP-02": RuleVersionMetadata(
        source="01_Packaged_Commodities_Rules_2011.pdf",
        clause="Rule 2(m), Rule 6(1)(e)",
        gsr_number="G.S.R. 202(E) (Principal)",
        verification_status="VERIFIED — VERBATIM",
        last_verified="2026-09-05",
    ),
    "REQ-MVP-03": RuleVersionMetadata(
        source="01_Packaged_Commodities_Rules_2011.pdf",
        clause="Rule 13(1), (4), (5)",
        gsr_number="G.S.R. 202(E) (Principal)",
        verification_status="VERIFIED — VERBATIM",
        last_verified="2026-09-05",
    ),
    "REQ-MVP-04": RuleVersionMetadata(
        source="01_Packaged_Commodities_Rules_2011.pdf",
        clause="Rule 13(2), (3) + Proviso",
        gsr_number="G.S.R. 202(E) (Principal)",
        verification_status="CONFIRMED",
        last_verified="2026-09-05",
    ),
    "REQ-MVP-05": RuleVersionMetadata(
        source="01_Packaged_Commodities_Rules_2011.pdf",
        clause="Rule 12(6)",
        gsr_number="G.S.R. 202(E) (Principal)",
        verification_status="CONFIRMED",
        last_verified="2026-09-05",
    ),
    "REQ-MVP-06": RuleVersionMetadata(
        source="01_Packaged_Commodities_Rules_2011.pdf",
        clause="Rule 6(1)(d) + Proviso",
        gsr_number="G.S.R. 202(E) (Principal)",
        verification_status="CONFIRMED",
        last_verified="2026-09-05",
    ),
    "REQ-MVP-07": RuleVersionMetadata(
        source="01_Packaged_Commodities_Rules_2011.pdf",
        clause="Rule 6(2)",
        gsr_number="G.S.R. 202(E) (Principal)",
        verification_status="CONFIRMED",
        last_verified="2026-09-05",
    ),
    "REQ-MVP-08": RuleVersionMetadata(
        source="01_Packaged_Commodities_Rules_2011.pdf",
        clause="Rule 10(1) Explanation",
        gsr_number="G.S.R. 202(E) (Principal)",
        verification_status="CONFIRMED",
        last_verified="2026-09-05",
    ),
    "REQ-MVP-09": RuleVersionMetadata(
        source="01_Packaged_Commodities_Rules_2011.pdf",
        clause="Rule 10(1) Proviso 2",
        gsr_number="G.S.R. 202(E) (Principal)",
        verification_status="CONFIRMED",
        last_verified="2026-09-05",
    ),
    "REQ-MVP-10": RuleVersionMetadata(
        source="03_PCR_Second_Amendment_2025.pdf",
        clause="Rule 26(a) Second Proviso",
        gsr_number="G.S.R. 881(E) (2nd Amendment 2025)",
        verification_status="CONFIRMED",
        last_verified="2026-09-05",
    ),
    "REQ-MVP-11": RuleVersionMetadata(
        source="02_PCR_Amendment_2025_24-10-2025.pdf",
        clause="Rule 2(h)/7(2)/7(3) Provisos",
        gsr_number="G.S.R. 778(E) (Amendment 2025)",
        verification_status="CONFIRMED",
        last_verified="2026-09-05",
    ),
    "REQ-MVP-12": RuleVersionMetadata(
        source="01_Packaged_Commodities_Rules_2011.pdf",
        clause="Rule 5, Proviso",
        gsr_number="G.S.R. 202(E) (Principal)",
        verification_status="VERIFIED — VERBATIM",
        last_verified="2026-09-05",
    ),
    "REQ-MVP-13": RuleVersionMetadata(
        source="01_Packaged_Commodities_Rules_2011.pdf",
        clause="Rule 6(3)",
        gsr_number="G.S.R. 202(E) (Principal)",
        verification_status="VERIFIED — VERBATIM",
        last_verified="2026-09-05",
    ),
    "REQ-MVP-14": RuleVersionMetadata(
        source="01_Packaged_Commodities_Rules_2011.pdf",
        clause="Rule 8(1), Proviso",
        gsr_number="G.S.R. 202(E) (Principal)",
        verification_status="CONFIRMED",
        last_verified="2026-09-05",
    ),
    "REQ-MVP-15": RuleVersionMetadata(
        source="01_Packaged_Commodities_Rules_2011.pdf",
        clause="Rule 9(1) + Proviso (a)",
        gsr_number="G.S.R. 202(E) (Principal)",
        verification_status="CONFIRMED",
        last_verified="2026-09-05",
    ),
}

class RuleResult(BaseModel):
    """
    Per-Check Result Object from Confidence_Status_Schema.md Section 2.
    Two confidence numbers kept permanently separate — never combined into one score:
    - detection_confidence: how confident OCR/CV is about what it read
    - applicability_confidence: how confident the system is that this rule even applies
    """
    rule_id: str = Field(..., description="Unique rule ID e.g. REQ-MVP-02")
    status: ResultState = Field(..., description="One of the 6 allowed result states")
    detected_value: Optional[str] = Field(default=None, description="Observed raw/detected string")
    normalized_value: Optional[str] = Field(default=None, description="Normalized parsed structure")
    detection_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in what OCR/CV read")
    applicability_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence that this rule applies")
    reason: str = Field(..., description="Technical or legal explanation for the outcome")
    evidence: Optional[EvidenceObject] = Field(default=None, description="Preserved visual & textual evidence")
    explanation_for_inspector: str = Field(..., description="User-friendly explanation for enforcement official")
    conflicts: Optional[ConflictObject] = Field(default=None, description="Surface conflict details if any")
    rule_version: RuleVersionMetadata = Field(..., description="Verifiable legal citation metadata")

    @model_validator(mode="after")
    def validate_visual_aid_rules(self) -> "RuleResult":
        # Section 9 constraint: REQ-MVP-14 and REQ-MVP-15 must NEVER produce COMPLIANT or POTENTIAL_VIOLATION
        if self.rule_id in ("REQ-MVP-14", "REQ-MVP-15"):
            if self.status in (ResultState.COMPLIANT, ResultState.POTENTIAL_VIOLATION):
                raise ValueError(
                    f"Rule {self.rule_id} is an assistive visual aid only and can NEVER produce "
                    f"'{self.status}'. It must be restricted to 'NEEDS_MANUAL_REVIEW' or 'NOT_DETECTED' only."
                )
        return self

class SummaryCounts(BaseModel):
    total_rules: int = 15
    compliant: int = 0
    potential_violations: int = 0
    needs_manual_review: int = 0
    not_applicable: int = 0
    not_detected: int = 0
    analysis_failed: int = 0

class ComplianceResult(BaseModel):
    """
    Complete compliance analysis result for an inspection.
    """
    inspection_id: str
    overall_status: ResultState
    summary_counts: SummaryCounts
    rule_results: List[RuleResult]
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = Field(default="mock-v1.0.0")
