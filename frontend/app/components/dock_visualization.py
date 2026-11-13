from PySide6.QtCore import QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class DockVisualization(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(220)
        self.altitude = 18.0
        self.uav_present = False

    def update_state(self, altitude: float, uav_present: bool) -> None:
        self.altitude, self.uav_present = altitude, uav_present
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        painter.setPen(QPen(QColor("#1E3A4C"), 2))
        painter.setBrush(QBrush(QColor("#102334")))
        dock = QRectF(w * .25, h * .66, w * .5, h * .18)
        painter.drawRoundedRect(dock, 8, 8)
        painter.setPen(QPen(QColor("#35D6C5"), 2))
        painter.drawLine(w * .35, h * .66, w * .65, h * .66)
        x, y = w * .5, h * (.25 - min(self.altitude, 25) / 100)
        painter.setBrush(QBrush(QColor("#35D6C5")))
        painter.drawEllipse(QRectF(x - 26, y - 10, 52, 20))
        painter.drawLine(x - 45, y, x + 45, y)
        painter.drawLine(x, y - 15, x, y + 15)
        painter.setPen(QPen(QColor("#9DB2C7"), 1))
        painter.drawText(12, 22, f"ESTIMATED ALTITUDE  {self.altitude:.1f} m")
        painter.drawText(12, h - 15, "DOCK LANDING ZONE  •  RELATIVE POSITION")

