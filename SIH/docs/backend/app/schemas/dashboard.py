from typing import List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.inspection import InspectionResponse

class RuleViolationMetric(BaseModel):
    rule_id: str
    count: int
    rule_name: str

class DashboardSummaryResponse(BaseModel):
    """
    Computed live from stored database inspection records.
    """
    total_inspections: int = 0
    compliant_inspections: int = 0
    potential_violations: int = 0
    needs_manual_review: int = 0
    not_applicable: int = 0
    analysis_failed: int = 0
    pending_analysis: int = 0
    top_violated_rules: List[RuleViolationMetric] = Field(default_factory=list)
    recent_inspections: List[InspectionResponse] = Field(default_factory=list)
