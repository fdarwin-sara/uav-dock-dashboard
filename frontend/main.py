from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from app.core.config import APP_NAME
from app.core.theme import DARK_THEME
from app.services.mock_data_provider import MockDataProvider
from app.viewmodels.dashboard_viewmodel import DashboardViewModel
from app.views.main_window import MainWindow


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    application = QApplication(sys.argv)
    application.setApplicationName(APP_NAME)
    application.setStyleSheet(DARK_THEME)
    provider = MockDataProvider()
    view_model = DashboardViewModel(provider)
    window = MainWindow(view_model)
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())

