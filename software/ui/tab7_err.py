# ui/tabs.py update
import os
import math
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QStackedWidget, QSlider, QCheckBox,
                               QFrame, QComboBox, QTextEdit)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QPolygon
from core.gauges import GX360Dial
import pyqtgraph as pg
from ui.base_tab import SensorTabBase

class Tab6_ERR(SensorTabBase):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        # --- LEFT PANEL: System Info ---
        info_panel = QVBoxLayout()
        info_panel.setSpacing(10)

        # Software & Hardware Versions (Usually indicated there ne)
        info_panel.addWidget(QLabel("SYSTEM INFORMATION"))
        info_panel.addWidget(QLabel("SOFTWARE VERSION: v1.0.3 (GX Edition)"))
        info_panel.addWidget(QLabel("HARDWARE VERSION: v1.0.0 (Rev B)"))
        info_panel.addWidget(QLabel("STM32 FW: v0.9.8"))
        info_panel.addStretch()

        # Quick commands for debugging tool
        info_panel.addWidget(QLabel("QUICK DEBUG COMMANDS"))
        self.btn_ping_acc = QPushButton("PING ACC SENSORS")
        self.btn_ping_pot = QPushButton("PING POTS")
        for btn in [self.btn_ping_acc, self.btn_ping_pot]:
            btn.setObjectName("tinyActionBtn")  # Corner styles ne
            info_panel.addWidget(btn)

        layout.addLayout(info_panel, 1)  # Width factor 1

        # --- RIGHT PANEL: The Console Window ---
        console_panel = QVBoxLayout()

        header = QHBoxLayout()
        header.addWidget(QLabel("I2C ERROR & COMM CONSOLE"))
        self.btn_clear = QPushButton("CLEAR")
        header.addWidget(self.btn_clear)
        console_panel.addLayout(header)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setObjectName("gxConsole")  # Hacker styles ne Consolas
        console_panel.addWidget(self.console)

        layout.addLayout(console_panel, 3)  # Width factor 3 (wider)

        self.content_layout.addLayout(layout)
        self.btn_clear.clicked.connect(self.console.clear)