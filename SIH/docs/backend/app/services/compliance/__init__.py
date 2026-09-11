from app.config import settings
from app.services.compliance.base import BaseComplianceEngine
from app.services.compliance.mock_compliance_service import MockComplianceEngine

def get_compliance_engine() -> BaseComplianceEngine:
    """
    SWAPPABLE COMPLIANCE ENGINE FACTORY
    -----------------------------------
    When P2 provides the real compliance engine:
    1. Import the real compliance engine class here.
    2. Ensure it implements BaseComplianceEngine (or adapt its evaluate method).
    3. Return an instance of it when settings.COMPLIANCE_ENGINE_TYPE == "real" or by default.
    """
    if settings.COMPLIANCE_ENGINE_TYPE == "mock":
        return MockComplianceEngine()
    # Fallback to mock for Phase 1
    return MockComplianceEngine()

__all__ = ["BaseComplianceEngine", "MockComplianceEngine", "get_compliance_engine"]
