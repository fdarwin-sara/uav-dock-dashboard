import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.services.mock_data_provider import MockDataProvider
from app.viewmodels.dashboard_viewmodel import DashboardViewModel
from app.views.main_window import MainWindow


def test_sidebar_navigation_is_exclusive():
    application = QApplication.instance() or QApplication([])
    window = MainWindow(DashboardViewModel(MockDataProvider()))
    buttons = [window.nav_group.button(index) for index in range(6)]

    assert buttons[0].isChecked()
    buttons[2].click()

    assert window.stack.currentIndex() == 2
    assert [button.isChecked() for button in buttons] == [False, False, True, False, False, False]
    window.close()
    application.processEvents()
