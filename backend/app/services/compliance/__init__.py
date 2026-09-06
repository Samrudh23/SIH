from app.config import settings
from app.services.compliance.base import BaseComplianceEngine
from app.services.compliance.mock_compliance_service import MockComplianceEngine
from app.services.compliance.real_compliance_engine import RealComplianceEngine

def get_compliance_engine() -> BaseComplianceEngine:
    """
    SWAPPABLE COMPLIANCE ENGINE FACTORY
    -----------------------------------
    Switches between MockComplianceEngine and RealComplianceEngine (P2)
    based on settings.COMPLIANCE_ENGINE_TYPE.
    Defaults to RealComplianceEngine when COMPLIANCE_ENGINE_TYPE != "mock".
    """
    if settings.COMPLIANCE_ENGINE_TYPE == "mock":
        return MockComplianceEngine()
    return RealComplianceEngine()

__all__ = [
    "BaseComplianceEngine",
    "MockComplianceEngine",
    "RealComplianceEngine",
    "get_compliance_engine",
]

