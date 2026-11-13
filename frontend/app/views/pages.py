from __future__ import annotations

from datetime import datetime, timezone

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.components.dock_visualization import DockVisualization
from app.components.metric_card import MetricCard
from app.core.enums import Severity
from app.models.history import MissionRecord
from app.viewmodels.dashboard_viewmodel import DashboardViewModel


def panel(title: str) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("panel")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(18, 16, 18, 18)
    heading = QLabel(title)
    heading.setStyleSheet("font-size: 16px; font-weight: 700;")
    layout.addWidget(heading)
    return frame, layout


def styled_label(text: str, object_name: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName(object_name)
    return label


def set_table_policy(table: QTableWidget, stretch_columns: tuple[int, ...]) -> None:
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setWordWrap(True)
    table.verticalHeader().setVisible(False)
    header = table.horizontalHeader()
    header.setMinimumSectionSize(80)
    for column in range(table.columnCount()):
        header.setSectionResizeMode(
            column,
            QHeaderView.Stretch if column in stretch_columns else QHeaderView.ResizeToContents,
        )


class DashboardPage(QWidget):
    def __init__(self, vm: DashboardViewModel) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 22)
        root.setSpacing(12)
        root.addWidget(styled_label("Overview", "title"))
        root.addWidget(styled_label("Live operational picture • SIMULATION MODE", "muted"))

        self.cards = [MetricCard(x) for x in ("UAV Status", "Battery Level", "Mission Progress", "Active Alerts")]
        cards = QHBoxLayout()
        cards.setSpacing(12)
        for card in self.cards:
            card.setMinimumHeight(110)
            cards.addWidget(card, 1)
        root.addLayout(cards)

        monitor, monitor_layout = panel("UAV & Dock Monitoring")
        self.visual = DockVisualization()
        monitor_layout.addWidget(self.visual)
        mission, mission_layout = panel("Current Mission")
        self.mission_text = QLabel()
        self.mission_text.setWordWrap(True)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        mission_layout.addWidget(self.mission_text)
        mission_layout.addStretch()
        mission_layout.addWidget(self.progress)
        center = QHBoxLayout()
        center.setSpacing(12)
        center.addWidget(monitor, 2)
        center.addWidget(mission, 1)
        root.addLayout(center, 3)

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
        bottom.setSpacing(12)
        bottom.addWidget(telemetry, 2)
        bottom.addWidget(alerts, 1)
        root.addLayout(bottom, 2)
        vm.snapshot_changed.connect(self.update_snapshot)
        self.update_snapshot(vm.snapshot)

    def update_snapshot(self, snapshot) -> None:
        self.cards[0].update_value("CONNECTED", snapshot.uav.operational_state)
        self.cards[1].update_value(f"{snapshot.uav.battery_percent:.1f}%", "UAV battery")
        self.cards[2].update_value(f"{snapshot.mission.progress_percent:.0f}%", snapshot.mission.phase.value)
        self.cards[3].update_value(str(len(snapshot.alerts)), "active events")
        self.visual.update_state(snapshot.uav.altitude_m, snapshot.dock.uav_present)
        self.mission_text.setText(
            f"<b>{snapshot.mission.mission_id}</b><br>{snapshot.mission.state}  •  "
            f"{snapshot.mission.phase.value}<br>Communication: {snapshot.mission.communication}"
        )
        self.progress.setValue(round(snapshot.mission.progress_percent))
        self.telemetry_text.setText(
            f"Altitude: {snapshot.telemetry.altitude_m:.1f} m    "
            f"Battery voltage: {snapshot.telemetry.battery_voltage_v:.2f} V"
        )
        self.altitudes = (self.altitudes + [snapshot.telemetry.altitude_m])[-60:]
        self.altitude_curve.setData(self.altitudes)
        self.alerts.setText("\n".join(
            f"[{a.severity.value}] {a.source}: {a.message}" for a in snapshot.alerts
        ))


class TelemetryPage(QWidget):
    def __init__(self, vm: DashboardViewModel) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.addWidget(styled_label("UAV Telemetry", "title"))
        layout.addWidget(styled_label("Live flight data • SIMULATION MODE", "muted"))
        cards = QHBoxLayout()
        self.telemetry_cards = [MetricCard(label) for label in ("Battery", "Voltage", "Altitude", "Speed")]
        for card in self.telemetry_cards:
            cards.addWidget(card, 1)
        layout.addLayout(cards)

        charts = QHBoxLayout()
        self.altitude_plot = self._plot("Altitude", "m", "#62e6c6")
        self.voltage_plot = self._plot("Voltage", "V", "#f0b35b")
        charts.addWidget(self.altitude_plot["widget"])
        charts.addWidget(self.voltage_plot["widget"])
        layout.addLayout(charts, 3)

        info, info_layout = panel("Position & Orientation")
        self.details = QLabel()
        self.details.setWordWrap(True)
        info_layout.addWidget(self.details)
        layout.addWidget(info)
        self.altitudes: list[float] = []
        self.voltages: list[float] = []
        vm.snapshot_changed.connect(self.update_snapshot)
        self.update_snapshot(vm.snapshot)

    @staticmethod
    def _plot(label: str, unit: str, color: str) -> dict:
        frame, layout = panel(f"{label} trend")
        plot = pg.PlotWidget()
        plot.setBackground("#132530")
        plot.showGrid(x=True, y=True, alpha=0.2)
        plot.setLabel("left", label, units=unit)
        plot.setLabel("bottom", "Samples")
        curve = plot.plot(pen=pg.mkPen(color, width=2))
        layout.addWidget(plot)
        return {"widget": frame, "curve": curve}

    def update_snapshot(self, snapshot) -> None:
        self.telemetry_cards[0].update_value(f"{snapshot.uav.battery_percent:.1f}%", "remaining")
        self.telemetry_cards[1].update_value(f"{snapshot.telemetry.battery_voltage_v:.2f} V", "battery voltage")
        self.telemetry_cards[2].update_value(f"{snapshot.uav.altitude_m:.1f} m", "above reference")
        self.telemetry_cards[3].update_value(f"{snapshot.uav.speed_mps:.1f} m/s", "ground speed")
        self.altitudes = (self.altitudes + [snapshot.uav.altitude_m])[-60:]
        self.voltages = (self.voltages + [snapshot.telemetry.battery_voltage_v])[-60:]
        self.altitude_plot["curve"].setData(self.altitudes)
        self.voltage_plot["curve"].setData(self.voltages)
        self.details.setText(
            f"<b>GPS</b>  {snapshot.uav.latitude:.4f}, {snapshot.uav.longitude:.4f}"
            f"    <b>Heading</b>  {snapshot.uav.heading_deg:.0f}°"
            f"    <b>Last update</b>  {snapshot.telemetry.timestamp.astimezone().strftime('%H:%M:%S')}"
        )


class MissionsPage(QWidget):
    _phases = ("Mission", "Return", "Landing", "Exchange", "Verification", "Ready")

    def __init__(self, vm: DashboardViewModel) -> None:
        super().__init__()
        self.vm = vm
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)
        layout.addWidget(styled_label("Missions", "title"))
        layout.addWidget(styled_label("Current mission supervision • no flight commands", "muted"))
        current, current_layout = panel("Current mission")
        self.mission_text = QLabel()
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        current_layout.addWidget(self.mission_text)
        current_layout.addWidget(self.progress)
        timeline = QHBoxLayout()
        timeline.setSpacing(4)
        self.timeline_labels: list[QLabel] = []
        for phase in self._phases:
            label = QLabel(phase)
            label.setAlignment(Qt.AlignCenter)
            label.setMinimumHeight(42)
            label.setStyleSheet("background: #20343d; border-radius: 5px; padding: 8px;")
            self.timeline_labels.append(label)
            timeline.addWidget(label, 1)
        current_layout.addLayout(timeline)
        layout.addWidget(current)

        details, details_layout = panel("Mission information")
        self.details = QLabel()
        self.details.setWordWrap(True)
        details_layout.addWidget(self.details)
        layout.addWidget(details)
        layout.addStretch()
        vm.snapshot_changed.connect(self.update_snapshot)
        self.update_snapshot(vm.snapshot)

    def update_snapshot(self, snapshot) -> None:
        mission = snapshot.mission
        self.mission_text.setText(
            f"<b>{mission.mission_id}</b>  •  {mission.state}<br>"
            f"Current stage: {mission.phase.value}"
        )
        self.progress.setValue(round(mission.progress_percent))
        active_index = min(len(self._phases) - 1, round(mission.progress_percent / 20))
        for index, label in enumerate(self.timeline_labels):
            color = "#245b58" if index <= active_index else "#20343d"
            label.setStyleSheet(f"background: {color}; border-radius: 5px; padding: 8px;")
        self.details.setText(
            f"Elapsed time: {mission.elapsed_seconds} s (simulated)\n"
            f"Communication: {mission.communication}\n"
            f"Last update: {mission.updated_at.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}"
        )


class DockPage(QWidget):
    def __init__(self, vm: DashboardViewModel) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.addWidget(styled_label("Dock Station", "title"))
        layout.addWidget(styled_label("Station status • SIMULATION MODE", "muted"))
        self.status_cards = [MetricCard(label) for label in ("Dock status", "UAV present", "Battery", "Mechanism")]
        cards = QHBoxLayout()
        for card in self.status_cards:
            cards.addWidget(card, 1)
        layout.addLayout(cards)
        visual_panel, visual_layout = panel("Dock schematic")
        self.visual = DockVisualization()
        visual_layout.addWidget(self.visual)
        info_panel, info_layout = panel("Verification & recent events")
        self.info = QLabel()
        self.info.setWordWrap(True)
        self.events = QListWidget()
        info_layout.addWidget(self.info)
        info_layout.addWidget(self.events)
        body = QHBoxLayout()
        body.addWidget(visual_panel, 2)
        body.addWidget(info_panel, 1)
        layout.addLayout(body, 1)
        vm.snapshot_changed.connect(self.update_snapshot)
        self.update_snapshot(vm.snapshot)

    def update_snapshot(self, snapshot) -> None:
        dock = snapshot.dock
        self.status_cards[0].update_value("CONNECTED" if dock.connected else "OFFLINE", "general state")
        self.status_cards[1].update_value("YES" if dock.uav_present else "NO", "detected")
        self.status_cards[2].update_value("PRESENT" if dock.battery_present else "ABSENT", "battery bay")
        self.status_cards[3].update_value(dock.mechanism.value, "mechanism state")
        self.visual.update_state(snapshot.uav.altitude_m, dock.uav_present)
        self.info.setText(f"<b>Verification</b><br>{dock.verification}<br><br>"
                          f"<b>Last update</b><br>{snapshot.mission.updated_at.astimezone().strftime('%H:%M:%S')}")
        if self.events.count() == 0 or self.events.item(0).text() != "Dock telemetry synchronized":
            self.events.insertItem(0, QListWidgetItem("Dock telemetry synchronized"))
        if dock.uav_present:
            self.events.insertItem(0, QListWidgetItem("UAV presence detected"))
        while self.events.count() > 5:
            self.events.takeItem(self.events.count() - 1)


class AlertsPage(QWidget):
    def __init__(self, vm: DashboardViewModel) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.addWidget(styled_label("Alerts", "title"))
        layout.addWidget(styled_label("Operator notifications • SIMULATION MODE", "muted"))
        self.filter = QComboBox()
        self.filter.addItems(["All severities", *[s.value for s in Severity]])
        layout.addWidget(self.filter)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Severity", "Source", "Message", "Timestamp"])
        set_table_policy(self.table, (2,))
        layout.addWidget(self.table, 1)
        self._alerts = ()
        self.filter.currentTextChanged.connect(self.render)
        vm.snapshot_changed.connect(self._set_alerts)

    def _set_alerts(self, snapshot) -> None:
        self._alerts = snapshot.alerts
        self.render()

    def render(self) -> None:
        selected = self.filter.currentText()
        alerts = [a for a in self._alerts if selected == "All severities" or a.severity.value == selected]
        self.table.setRowCount(len(alerts))
        colors = {Severity.INFO: "#62e6c6", Severity.WARNING: "#f0b35b", Severity.CRITICAL: "#ed6a70"}
        for row, alert in enumerate(alerts):
            values = (alert.severity.value, alert.source, alert.message,
                      alert.timestamp.astimezone().strftime("%Y-%m-%d %H:%M:%S"))
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col == 0:
                    item.setForeground(QColor(colors[alert.severity]))
                self.table.setItem(row, col, item)
        self.table.resizeRowsToContents()


class HistoryPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.addWidget(styled_label("History", "title"))
        layout.addWidget(styled_label("Read-only demonstration records", "muted"))
        table = QTableWidget(3, 5)
        table.setHorizontalHeaderLabels(["Mission", "Started", "Status", "Duration", "Result"])
        set_table_policy(table, (4,))
        layout.addWidget(table, 1)
        now = datetime.now(timezone.utc)
        rows = [MissionRecord(f"M-2026-00{i}", now, "Completed", 300 + i * 42, "Demo record") for i in range(1, 4)]
        for row, record in enumerate(rows):
            values = (record.mission_id, record.started_at.astimezone().strftime("%Y-%m-%d %H:%M"),
                      record.status, f"{record.duration_seconds}s", record.result)
            for col, value in enumerate(values):
                table.setItem(row, col, QTableWidgetItem(value))
        table.resizeRowsToContents()
