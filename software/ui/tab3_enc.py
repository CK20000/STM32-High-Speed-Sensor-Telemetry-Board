from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget
from PySide6.QtCore import Qt
from core.gauges import GX360Dial # <--- USING THE HAND METERS
from ui.base_tab import SensorTabBase

class Tab3_ENC(SensorTabBase):
    def __init__(self):
        super().__init__()

        self.setup_standard_header("OPTICAL & MAGNETIC ENCODERS", "ENABLE ENCODER STREAM")

        toggle_layout = QHBoxLayout()
        toggle_layout.addStretch()
        self.btn_mode = QPushButton("MODE: SEPARATE")
        self.btn_mode.setObjectName("tinyActionBtn")
        self.btn_mode.setCheckable(True)
        toggle_layout.addWidget(self.btn_mode)
        self.content_layout.addLayout(toggle_layout)

        self.dial_stack = QStackedWidget()

        view_sep_widget = QWidget()
        sep_layout = QHBoxLayout(view_sep_widget)
        self.dial_optical = GX360Dial(dual_mode=False, color1="#00ffcc")
        self.dial_magnetic = GX360Dial(dual_mode=False, color1="#fa1e4e")
        sep_layout.addWidget(QLabel("OPTICAL"))
        sep_layout.addWidget(self.dial_optical)
        sep_layout.addStretch()
        sep_layout.addWidget(QLabel("MAGNETIC"))
        sep_layout.addWidget(self.dial_magnetic)
        self.dial_stack.addWidget(view_sep_widget)

        view_comb_widget = QWidget()
        comb_layout = QVBoxLayout(view_comb_widget)
        self.dial_combined = GX360Dial(dual_mode=True)
        comb_layout.addWidget(self.dial_combined, 0, Qt.AlignCenter)
        self.dial_stack.addWidget(view_comb_widget)

        self.content_layout.addWidget(self.dial_stack)
        self.btn_mode.toggled.connect(self.switch_view)

    def switch_view(self, is_checked):
        if is_checked:
            self.btn_mode.setText("MODE: COMBINED")
            self.dial_stack.setCurrentIndex(1)
        else:
            self.btn_mode.setText("MODE: SEPARATE")
            self.dial_stack.setCurrentIndex(0)
