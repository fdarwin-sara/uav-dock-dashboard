from __future__ import annotations

from datetime import datetime, timezone

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QListWidget, QProgressBar, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
import pyqtgraph as pg

from app.components.dock_visualization import DockVisualization
from app.components.metric_card import MetricCard
from app.core.enums import Severity
from app.models.history import MissionRecord
from app.viewmodels.dashboard_viewmodel import DashboardViewModel


def panel(title: str) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("panel")
    layout = QVBoxLayout(frame)
    heading = QLabel(title)
    heading.setStyleSheet("font-size: 16px; font-weight: 700;")
    layout.addWidget(heading)
    return frame, layout


class DashboardPage(QWidget):
    def __init__(self, vm: DashboardViewModel) -> None:
        super().__init__()
        self.vm = vm
        root = QVBoxLayout(self)
        title = QLabel("Overview")
        title.setObjectName("title")
        root.addWidget(title)
        subtitle = QLabel("Live operational picture • SIMULATION MODE")
        subtitle.setObjectName("muted")
        root.addWidget(subtitle)
        self.cards = [MetricCard(x) for x in ("UAV Status", "Battery Level", "Mission Progress", "Active Alerts")]
        cards = QHBoxLayout()
        for card in self.cards:
            cards.addWidget(card)
        root.addLayout(cards)
        monitor, monitor_layout = panel("UAV & Dock Monitoring")
        self.visual = DockVisualization()
        monitor_layout.addWidget(self.visual)
        mission, mission_layout = panel("Current Mission")
        self.mission_text = QLabel()
        self.progress = QProgressBar()
        mission_layout.addWidget(self.mission_text)
        mission_layout.addWidget(self.progress)
        center = QHBoxLayout()
        center.addWidget(monitor, 2)
        center.addWidget(mission, 1)
        root.addLayout(center)
        telemetry, telemetry_layout = panel("Telemetry Monitoring")
        self.telemetry_text = QLabel()
        self.chart = pg.PlotWidget()
        self.chart.setBackground("#132530")
        self.chart.showGrid(x=True, y=True, alpha=0.2)
        self.chart.setLabel("left", "Altitude", units="m")
        self.chart.setLabel("bottom", "Samples")
        self.altitude_curve = self.chart.plot(pen=pg.mkPen("#62e6c6", width=2))
        self.altitudes: list[float] = []
        telemetry_layout.addWidget(self.telemetry_text)
        telemetry_layout.addWidget(self.chart)
        alerts, alerts_layout = panel("Recent Alerts")
        self.alerts = QLabel()
        self.alerts.setWordWrap(True)
        alerts_layout.addWidget(self.alerts)
        bottom = QHBoxLayout()
        bottom.addWidget(telemetry, 2)
        bottom.addWidget(alerts, 1)
        root.addLayout(bottom)
        vm.snapshot_changed.connect(self.update_snapshot)
        self.update_snapshot(vm.snapshot)

    def update_snapshot(self, snapshot) -> None:
        self.cards[0].update_value("CONNECTED", snapshot.uav.operational_state)
        self.cards[1].update_value(f"{snapshot.uav.battery_percent:.1f}%", "UAV battery")
        self.cards[2].update_value(f"{snapshot.mission.progress_percent:.0f}%", snapshot.mission.phase.value)
        self.cards[3].update_value(str(len(snapshot.alerts)), "active events")
        self.visual.update_state(snapshot.uav.altitude_m, snapshot.dock.uav_present)
        self.mission_text.setText(f"{snapshot.mission.mission_id}\n{snapshot.mission.state}  •  {snapshot.mission.phase.value}\n"
                                  f"Communication: {snapshot.mission.communication}")
        self.progress.setValue(round(snapshot.mission.progress_percent))
        self.telemetry_text.setText(f"Altitude: {snapshot.telemetry.altitude_m:.1f} m    "
                                    f"Battery voltage: {snapshot.telemetry.battery_voltage_v:.2f} V")
        self.altitudes.append(snapshot.telemetry.altitude_m)
        self.altitudes = self.altitudes[-60:]
        self.altitude_curve.setData(self.altitudes)
        self.alerts.setText("\n".join(f"[{a.severity.value}] {a.source}: {a.message}" for a in snapshot.alerts))


class TelemetryPage(QWidget):
    def __init__(self, vm: DashboardViewModel) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("UAV Telemetry"); title.setObjectName("title"); layout.addWidget(title)
        self.details = QLabel(); self.details.setWordWrap(True); layout.addWidget(self.details)
        self.chart = pg.PlotWidget(); self.chart.setBackground("#132530")
        self.chart.showGrid(x=True, y=True, alpha=0.2)
        self.chart.setLabel("left", "Altitude", units="m")
        self.curve = self.chart.plot(pen=pg.mkPen("#62e6c6", width=2))
        self.altitudes: list[float] = []
        layout.addWidget(self.chart)
        vm.snapshot_changed.connect(self.update_snapshot)
        self.update_snapshot(vm.snapshot)

    def update_snapshot(self, s) -> None:
        self.details.setText(f"Battery {s.uav.battery_percent:.1f}%  •  Voltage {s.telemetry.battery_voltage_v:.2f} V  •  "
                            f"Altitude {s.uav.altitude_m:.1f} m  •  Speed {s.uav.speed_mps:.1f} m/s  •  "
                            f"GPS {s.uav.latitude:.4f}, {s.uav.longitude:.4f}  •  Heading {s.uav.heading_deg:.0f}°")
        self.altitudes.append(s.telemetry.altitude_m)
        self.altitudes = self.altitudes[-60:]
        self.curve.setData(self.altitudes)


class MissionsPage(QWidget):
    def __init__(self, vm: DashboardViewModel) -> None:
        super().__init__(); layout = QVBoxLayout(self)
        title = QLabel("Missions"); title.setObjectName("title"); layout.addWidget(title)
        self.text = QLabel(); layout.addWidget(self.text)
        vm.snapshot_changed.connect(lambda s: self.text.setText(f"Current mission: {s.mission.mission_id}\n"
                                                                  f"State: {s.mission.state}\nPhase: {s.mission.phase.value}\n"
                                                                  f"Progress: {s.mission.progress_percent:.0f}%"))
        self.text.setText("Waiting for telemetry...")


class DockPage(QWidget):
    def __init__(self, vm: DashboardViewModel) -> None:
        super().__init__(); layout = QVBoxLayout(self)
        title = QLabel("Dock Station"); title.setObjectName("title"); layout.addWidget(title)
        self.text = QLabel(); layout.addWidget(self.text)
        vm.snapshot_changed.connect(lambda s: self.text.setText(f"Connection: {'Connected' if s.dock.connected else 'Disconnected'}\n"
                                                                  f"UAV present: {'Yes' if s.dock.uav_present else 'No'}\n"
                                                                  f"Battery present: {'Yes' if s.dock.battery_present else 'No'}\n"
                                                                  f"Mechanism: {s.dock.mechanism.value}\nVerification: {s.dock.verification}"))
        self.text.setText("Waiting for telemetry...")


class AlertsPage(QWidget):
    def __init__(self, vm: DashboardViewModel) -> None:
        super().__init__(); layout = QVBoxLayout(self)
        title = QLabel("Alerts"); title.setObjectName("title"); layout.addWidget(title)
        self.filter = QComboBox(); self.filter.addItems(["All severities", *[s.value for s in Severity]]); layout.addWidget(self.filter)
        self.table = QTableWidget(0, 4); self.table.setHorizontalHeaderLabels(["Severity", "Source", "Message", "Time"]); layout.addWidget(self.table)
        self._alerts = ()
        self.filter.currentTextChanged.connect(self.render)
        vm.snapshot_changed.connect(lambda s: (setattr(self, "_alerts", s.alerts), self.render()))

    def render(self) -> None:
        selected = self.filter.currentText()
        alerts = [a for a in self._alerts if selected == "All severities" or a.severity.value == selected]
        self.table.setRowCount(len(alerts))
        for row, alert in enumerate(alerts):
            values = (alert.severity.value, alert.source, alert.message, alert.timestamp.astimezone().strftime("%H:%M:%S"))
            for col, value in enumerate(values): self.table.setItem(row, col, QTableWidgetItem(value))


class HistoryPage(QWidget):
    def __init__(self) -> None:
        super().__init__(); layout = QVBoxLayout(self)
        title = QLabel("History"); title.setObjectName("title"); layout.addWidget(title)
        table = QTableWidget(3, 5); table.setHorizontalHeaderLabels(["Mission", "Started", "Status", "Duration", "Result"]); layout.addWidget(table)
        now = datetime.now(timezone.utc)
        rows = [MissionRecord(f"M-2026-00{i}", now, "Completed", 300 + i * 42, "Demo record") for i in range(1, 4)]
        for row, record in enumerate(rows):
            values = (record.mission_id, record.started_at.astimezone().strftime("%Y-%m-%d %H:%M"), record.status,
                      f"{record.duration_seconds}s", record.result)
            for col, value in enumerate(values): table.setItem(row, col, QTableWidgetItem(value))

