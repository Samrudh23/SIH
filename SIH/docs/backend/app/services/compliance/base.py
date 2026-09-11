from abc import ABC, abstractmethod
from typing import Optional
from app.schemas.extraction import ExtractionPayload
from app.schemas.common import ImageCoverage
from app.schemas.compliance import ComplianceResult

class BaseComplianceEngine(ABC):
    """
    Abstract interface for compliance evaluation.
    Allows swapping between mock engine and real compliance engine (P2)
    without modifying API endpoints or database logic.
    """
    @abstractmethod
    def evaluate(
        self,
        extraction: ExtractionPayload,
        image_coverage: Optional[ImageCoverage] = None,
        is_medical_device_confirmed: Optional[bool] = None,
    ) -> ComplianceResult:
        """
        Evaluates extracted packaging declarations against legal metrology rules.
        """
        pass
