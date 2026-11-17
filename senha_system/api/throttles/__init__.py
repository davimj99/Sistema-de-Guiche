from rest_framework.throttling import (
    AnonRateThrottle,
    UserRateThrottle,
    ScopedRateThrottle,
)
from .custom_throttles import (
    CustomAnonRateThrottle,
    CustomUserRateThrottle,
    TotemRateThrottle,
    PainelRateThrottle,
    ChamadaRateThrottle,
)

__all__ = [
    "AnonRateThrottle",
    "UserRateThrottle",
    "ScopedRateThrottle",
    "CustomAnonRateThrottle",
    "CustomUserRateThrottle",
    "TotemRateThrottle",
    "PainelRateThrottle",
    "ChamadaRateThrottle",
]
