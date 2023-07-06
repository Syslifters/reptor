from enum import StrEnum

class RISK_RATING(StrEnum):
    INFO : str = "INFO"
    LOW : str = "LOW"
    MEDIUM : str = "MEDIUM"
    HIGH : str = "HIGH"
    CRITICAL : str = "CRITICAL"