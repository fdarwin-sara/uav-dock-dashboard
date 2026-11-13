from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QButtonGroup, QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from app.core.config import APP_NAME, APP_SUBTITLE, APP_VERSION
from app.viewmodels.dashboard_viewmodel import DashboardViewModel
from app.views.pages import AlertsPage, DashboardPage, DockPage, HistoryPage, MissionsPage, TelemetryPage


class MainWindow(QMainWindow):
    def __init__(self, view_model: DashboardViewModel) -> None:
        super().__init__()
        self.view_model = view_model
        self.setWindowTitle(APP_NAME)
        self.resize(1440, 900)
        self.stack = QStackedWidget()
        pages = [DashboardPage(view_model), TelemetryPage(view_model), MissionsPage(view_model),
                 DockPage(view_model), AlertsPage(view_model), HistoryPage()]
        for page in pages:
            self.stack.addWidget(page)
        sidebar = self._sidebar()
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(sidebar)
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(container)
        self.stack.setCurrentIndex(0)
        view_model.start()

    def _sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(245)
        layout = QVBoxLayout(sidebar)
        brand = QLabel("INTINAUTA")
        brand.setObjectName("brand")
        layout.addWidget(brand)
        subtitle = QLabel("UAV-DOCK OPERATIONS\n" + APP_SUBTITLE)
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        self.nav_group = QButtonGroup(sidebar)
        self.nav_group.setExclusive(True)
        for index, name in enumerate(("Overview", "UAV Telemetry", "Missions", "Dock Station", "Alerts", "History")):
            button = QPushButton(name)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.clicked.connect(lambda checked=False, i=index: self._select_page(i))
            self.nav_group.addButton(button, index)
            layout.addWidget(button)
            if index == 0:
                button.setChecked(True)
        layout.addStretch()
        layout.addWidget(QLabel("●  CONNECTED  •  SIMULATION"))
        layout.addWidget(QLabel(f"Version {APP_VERSION}\nINTINAUTA / PachaLab"))
        return sidebar

    def _select_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        button = self.nav_group.button(index)
        if button is not None:
            button.setChecked(True)

    def closeEvent(self, event) -> None:
        self.view_model.stop()
        super().closeEvent(event)

