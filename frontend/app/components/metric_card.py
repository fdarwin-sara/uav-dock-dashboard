from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class MetricCard(QFrame):
    def __init__(self, title: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.setProperty("metric", True)
        self.value = QLabel("--")
        self.value.setObjectName("metric")
        self.detail = QLabel("")
        self.detail.setObjectName("muted")
        layout = QVBoxLayout(self)
        title_label = QLabel(title.upper())
        title_label.setObjectName("metricTitle")
        layout.addWidget(title_label)
        layout.addWidget(self.value)
        layout.addWidget(self.detail)

    def update_value(self, value: str, detail: str = "") -> None:
        self.value.setText(value)
        self.detail.setText(detail)

