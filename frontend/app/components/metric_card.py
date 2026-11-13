from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class MetricCard(QFrame):
    def __init__(self, title: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.value = QLabel("--")
        self.value.setObjectName("metric")
        self.detail = QLabel("")
        self.detail.setObjectName("muted")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(title.upper()))
        layout.addWidget(self.value)
        layout.addWidget(self.detail)

    def update_value(self, value: str, detail: str = "") -> None:
        self.value.setText(value)
        self.detail.setText(detail)

