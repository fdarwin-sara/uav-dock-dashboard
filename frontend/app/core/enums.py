from enum import Enum


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class MissionPhase(str, Enum):
    APPROACH = "Approach"
    ALIGNMENT = "Alignment"
    LANDING = "Landing"
    BATTERY_CHECK = "Battery check"
    COMPLETE = "Complete"


class DockMechanismState(str, Enum):
    READY = "Ready"
    UAV_DETECTED = "UAV detected"
    VERIFYING = "Verifying"
    MAINTENANCE = "Maintenance"

