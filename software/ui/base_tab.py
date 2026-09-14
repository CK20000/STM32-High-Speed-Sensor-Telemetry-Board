# ui/base_tab.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QPolygon


class SensorTabBase(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sensorTab")

        base_layout = QVBoxLayout(self)
        base_layout.setContentsMargins(20, 20, 20, 20)

        self.content_layout = QVBoxLayout()
        base_layout.addLayout(self.content_layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        c = 35  # Chamfer cut size

        poly = QPolygon([
            QPoint(c, 0), QPoint(w, 0), QPoint(w, h - c),
            QPoint(w - c, h), QPoint(0, h), QPoint(0, c)
        ])

        painter.setBrush(QColor("#0f0f13"))
        painter.setPen(QPen(QColor("#fa1e4e"), 2))
        painter.drawPolygon(poly)

    def setup_standard_header(self, title_text, enable_text):
        header_layout = QHBoxLayout()

        title = QLabel(title_text)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #fa1e4e;")
        header_layout.addWidget(title, alignment=Qt.AlignTop | Qt.AlignLeft)
        header_layout.addStretch()

        right_stack = QVBoxLayout()
        right_stack.setSpacing(5)

        self.btn_pdf = QPushButton("!")
        self.btn_pdf.setFixedSize(30, 30)
        self.btn_pdf.setObjectName("actionBtn")

        self.btn_enable = QPushButton(enable_text)
        self.btn_enable.setCheckable(True)
        self.btn_enable.setObjectName("streamToggle")

        right_stack.addWidget(self.btn_pdf, alignment=Qt.AlignRight)
        right_stack.addWidget(self.btn_enable, alignment=Qt.AlignRight)

        header_layout.addLayout(right_stack)
        self.content_layout.addLayout(header_layout)