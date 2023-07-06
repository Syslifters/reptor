from enum import StrEnum, auto


class RISK_RATING(StrEnum):
    INFO = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()
