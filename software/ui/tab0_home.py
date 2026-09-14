from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QPushButton
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QPolygon
from ui.base_tab import SensorTabBase
from core.gauges import GXArcGauge


# --- 1. CUSTOM CHAMFERED FRAME FOR THE RED SENSOR BLOCK ---
class ChamferedStatusFrame(QFrame):
    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        c = 25  # Size of the bottom-right cut

        # Polygon with a flat top, left, bottom, but a cut bottom-right
        poly = QPolygon([
            QPoint(0, 50),  # Top Left
            QPoint(w, 50),  # Top Right
            QPoint(w,  h - c),  # Right edge, stop before bottom
            QPoint(w - c,  h),  # Bottom edge, stop before right
            QPoint(0, h)  # Bottom Left
        ])

        # Draw the neon red border and dark background
        painter.setBrush(QColor("#0f0f13"))
        painter.setPen(QPen(QColor("#fa1e4e"), 2))
        painter.drawPolygon(poly)


# --- 2. CUSTOM WIDGET FOR THE STATUS BLOCKS (Your Tweaked Class!) ---
class SensorStatusBlock(QFrame):
    def __init__(self, name, accent_color):
        super().__init__()
        self.accent_color = accent_color

        # Base style: dark background, transparent border so it doesn't clash with the main red frame
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a24;
                border: 1px solid #2a2a35;
                border-radius: 5px;
            }
        """)
        self.setFixedHeight(50)  # Tighter 50px height

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Left Accent Strip
        self.accent_strip = QFrame()
        self.accent_strip.setFixedWidth(4)
        self.accent_strip.setStyleSheet("background-color: #555555; border: none;")  # Dim default

        # Name
        self.lbl_name = QLabel(name)
        self.lbl_name.setStyleSheet("color: #ffffff; font-weight: bold; border: none;")

        # Status Badge (The small block on the right)
        self.badge = QLabel("OFF")
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setFixedSize(40, 24)
        self.badge.setStyleSheet(
            "background-color: #555555; color: #8a8a93; font-weight: bold; border: none; border-radius: 3px;")

        layout.addWidget(self.accent_strip)
        layout.addWidget(self.lbl_name)
        layout.addStretch()
        layout.addWidget(self.badge)

    def set_active(self, is_active):
        if is_active:
            # Wake up the colors!
            self.setStyleSheet(
                f"background-color: rgba(255, 255, 255, 0.05); border: 1px solid {self.accent_color}; border-radius: 5px;")
            self.accent_strip.setStyleSheet(f"background-color: {self.accent_color}; border: none;")
            self.badge.setText("ON")
            self.badge.setStyleSheet(
                f"background-color: {self.accent_color}; color: #0f0f13; font-weight: bold; border: none; border-radius: 3px;")
        else:
            # Go back to sleep
            self.setStyleSheet("background-color: #1a1a24; border: 1px solid #2a2a35; border-radius: 5px;")
            self.accent_strip.setStyleSheet("background-color: #555555; border: none;")
            self.badge.setText("OFF")
            self.badge.setStyleSheet(
                "background-color: #555555; color: #8a8a93; font-weight: bold; border: none; border-radius: 3px;")


# --- 3. THE HOME TAB MASTER CLASS ---
class Tab0_HOME(SensorTabBase):
    def __init__(self):
        super().__init__()

        # --- CUSTOM CENTERED HEADER ---
        header_layout = QHBoxLayout()
        title = QLabel("SYSTEM OVERVIEW & TELEMETRY")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #fa1e4e;")
        header_layout.addWidget(title)

        header_layout.addStretch()  # Push Master to center

        self.btn_master = QPushButton("MASTER ON")
        self.btn_master.setCheckable(True)
        self.btn_master.setMinimumWidth(100)  # Prevents jitter when text changes
        header_layout.addWidget(self.btn_master)
        self.content_layout.addLayout(header_layout)

        # --- MAIN CONTENT ---
        main_layout = QHBoxLayout()

        # --- LEFT: System Gauges ---
        gauges_layout = QVBoxLayout()

        self.gauge_loop = GXArcGauge(color="#ff7f26", title="LATENCY (ms)", max_val=1000)
        self.gauge_loop.update_value(13)

        self.gauge_mem = GXArcGauge(color="#ff7f26", title="CPU CYCLE (%)", max_val=100)
        self.gauge_mem.update_value(42)

        gauges_layout.addWidget(self.gauge_loop)
        gauges_layout.addWidget(self.gauge_mem)
        main_layout.addLayout(gauges_layout, 1)

        # --- RIGHT: Sensor Status Grid (Using the Custom Chamfer Frame) ---
        self.status_frame = ChamferedStatusFrame()
        status_layout = QVBoxLayout(self.status_frame)
        status_layout.setContentsMargins(15, 65, 15, 15)  # Add padding inside the drawn box

        grid = QGridLayout()
        grid.setSpacing(5)

        # Your specific names mapped to the exact colors you chose
        self.sensor_config = [
            ("MPU6050 1", "#ffaa00"),
            ("MPU6050 2", "#ffaa00"),
            ("HEATER", "#ffaa00"),
            ("VL53L0X", "#ffaa00"),
            ("OPTICAL ENC", "#ffaa00"),
            ("MAG ENC", "#ffaa00"),
            ("LOAD CELL", "#ffaa00"),
            ("BMP280", "#ffaa00"),
            ("POT 1", "#ffaa00"),
            ("POT 2", "#ffaa00"),
            ("POT 3", "#ffaa00"),
            ("MAGNETOMETER", "#ffaa00"),
            ("MOTOR", "#ffaa00"),
        ]

        self.status_blocks = {}
        row, col = 0, 0
        for name, color in self.sensor_config:
            block = SensorStatusBlock(name, color)
            self.status_blocks[name] = block
            grid.addWidget(block, row, col)

            col += 1
            if col > 1:  # Two Columns
                col = 0
                row += 1

        status_layout.addLayout(grid)

        # Qt.AlignTop forces the red box to hug the grid tightly!
        main_layout.addWidget(self.status_frame, 1, Qt.AlignTop)

        self.content_layout.addLayout(main_layout)

    def trigger_sensor(self, name, is_active):
        """Called by the main app when a toggle is flipped"""
        if name in self.status_blocks:
            self.status_blocks[name].set_active(is_active)
