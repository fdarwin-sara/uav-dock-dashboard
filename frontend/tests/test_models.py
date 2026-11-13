from datetime import datetime, timezone

from app.core.enums import DockMechanismState, MissionPhase, Severity
from app.models.state import AlertEvent, DashboardSnapshot, DockStatus, MissionStatus, TelemetrySample, UAVStatus


def test_snapshot_has_explicit_units_and_timezone():
    now = datetime.now(timezone.utc)
    snapshot = DashboardSnapshot(
        UAVStatus(True, "In operation", 80, 0, 0, 10, 2, 180),
        DockStatus(True, False, True, DockMechanismState.READY, "Verified"),
        TelemetrySample(now, 10, 22.2),
        MissionStatus("M-1", "Active", MissionPhase.APPROACH, 10, 20, "Nominal", now),
        (AlertEvent(Severity.INFO, "ok", "UAV", now),),
    )
    assert snapshot.telemetry.timestamp.tzinfo is not None
    assert 0 <= snapshot.uav.battery_percent <= 100

