from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from app.core.enums import DockMechanismState, MissionPhase, Severity


@dataclass(frozen=True)
class UAVStatus:
    connected: bool
    operational_state: str
    battery_percent: float
    latitude: float
    longitude: float
    altitude_m: float
    speed_mps: float
    heading_deg: float


@dataclass(frozen=True)
class DockStatus:
    connected: bool
    uav_present: bool
    battery_present: bool
    mechanism: DockMechanismState
    verification: str


@dataclass(frozen=True)
class TelemetrySample:
    timestamp: datetime
    altitude_m: float
    battery_voltage_v: float


@dataclass(frozen=True)
class MissionStatus:
    mission_id: str
    state: str
    phase: MissionPhase
    progress_percent: float
    elapsed_seconds: int
    communication: str
    updated_at: datetime


@dataclass(frozen=True)
class AlertEvent:
    severity: Severity
    message: str
    source: str
    timestamp: datetime
    acknowledged: bool = False


@dataclass(frozen=True)
class DashboardSnapshot:
    uav: UAVStatus
    dock: DockStatus
    telemetry: TelemetrySample
    mission: MissionStatus
    alerts: tuple[AlertEvent, ...] = field(default_factory=tuple)

