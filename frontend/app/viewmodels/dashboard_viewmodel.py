from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Signal

from app.contracts.data_provider import IDataProvider
from app.models.state import DashboardSnapshot


class DashboardViewModel(QObject):
    snapshot_changed = Signal(object)

    def __init__(self, provider: IDataProvider, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.provider = provider
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.provider.subscribe(self._on_snapshot)

    @property
    def snapshot(self) -> DashboardSnapshot:
        return self.provider.snapshot()

    def start(self, interval_ms: int = 1000) -> None:
        self.provider.start()
        self.timer.start(interval_ms)

    def stop(self) -> None:
        self.timer.stop()
        self.provider.stop()

    def refresh(self) -> None:
        tick = getattr(self.provider, "tick", None)
        if tick is None:
            return
        tick()

    def _on_snapshot(self, snapshot: DashboardSnapshot) -> None:
        self.snapshot_changed.emit(snapshot)

