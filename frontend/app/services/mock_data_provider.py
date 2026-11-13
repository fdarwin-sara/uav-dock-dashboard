from __future__ import annotations

import math
import random
from datetime import datetime, timezone
from typing import Callable

from app.core.enums import DockMechanismState, MissionPhase, Severity
from app.models.state import (
    AlertEvent,
    DashboardSnapshot,
    DockStatus,
    MissionStatus,
    TelemetrySample,
    UAVStatus,
)


class MockDataProvider:
    """Deterministic presentation data; it does not command hardware."""

    def __init__(self, seed: int = 7) -> None:
        self._random = random.Random(seed)
        self._step = 0
        self._snapshot = self._build_snapshot()
        self._listeners: list[Callable[[DashboardSnapshot], None]] = []

    def _build_snapshot(self) -> DashboardSnapshot:
        self._step += 1
        progress = min(99.0, (self._step * 3.0) % 103)
        phase = (
            MissionPhase.APPROACH if progress < 25 else
            MissionPhase.ALIGNMENT if progress < 50 else
            MissionPhase.LANDING if progress < 70 else
            MissionPhase.BATTERY_CHECK if progress < 90 else MissionPhase.COMPLETE
        )
        now = datetime.now(timezone.utc)
        battery = max(20.0, 92.0 - self._step * 0.18)
        altitude = max(0.0, 18.0 + math.sin(self._step / 4) * 5)
        voltage = 22.2 + math.sin(self._step / 8) * 0.35
        return DashboardSnapshot(
            uav=UAVStatus(True, "In operation", battery, -0.183, -78.485, altitude, 3.2, 185.0),
            dock=DockStatus(True, phase in (MissionPhase.LANDING, MissionPhase.BATTERY_CHECK), True,
                            DockMechanismState.VERIFYING if phase == MissionPhase.BATTERY_CHECK
                            else DockMechanismState.UAV_DETECTED, "Telemetry verified"),
            telemetry=TelemetrySample(now, altitude, voltage),
            mission=MissionStatus("M-2026-001", "Active", phase, progress, self._step, "Nominal", now),
            alerts=(
                AlertEvent(Severity.WARNING, "Battery reserve below launch threshold", "UAV", now),
                AlertEvent(Severity.INFO, "Dock telemetry synchronized", "Dock", now),
            ) if self._step % 5 == 0 else (
                AlertEvent(Severity.INFO, "Dock telemetry synchronized", "Dock", now),
            ),
        )

    def snapshot(self) -> DashboardSnapshot:
        return self._snapshot

    def subscribe(self, callback: Callable[[DashboardSnapshot], None]) -> None:
        self._listeners.append(callback)

    def start(self) -> None:
        self.tick()

    def stop(self) -> None:
        self._listeners.clear()

    def tick(self) -> DashboardSnapshot:
        self._snapshot = self._build_snapshot()
        for listener in tuple(self._listeners):
            listener(self._snapshot)
        return self._snapshot

