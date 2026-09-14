from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QSlider, QFrame, QComboBox, QGridLayout)
from PySide6.QtCore import Qt
from core.gauges import GXArcGauge
from ui.base_tab import SensorTabBase


class Tab5_POT(SensorTabBase):
    def __init__(self):
        super().__init__()

        self.setup_standard_header("POTENTIOMETERS & ESC SAFETY BRIDGE", "ENABLE POT STREAM")

        # --- THE 2x2 QUADRANT GRID ---
        grid = QGridLayout()
        grid.setSpacing(20)

        # Force exact 50/50 division horizontally and vertically
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)

        # 1. TOP-LEFT: Analog POT 1
        self.pot1_dial = GXArcGauge(color="#ffaa00", title="POT 1", max_val=4095)
        self.lbl_pot1_data = QLabel("ANALOG: 0 // VOLTS: 0.0V")
        grid.addWidget(self.create_pot_display(self.pot1_dial, self.lbl_pot1_data), 0, 0)

        # 2. BOTTOM-LEFT: Analog POT 2
        self.pot2_dial = GXArcGauge(color="#ffaa00", title="POT 2", max_val=4095)
        self.lbl_pot2_data = QLabel("ANALOG: 0 // VOLTS: 0.0V")
        grid.addWidget(self.create_pot_display(self.pot2_dial, self.lbl_pot2_data), 1, 0)

        # 3. TOP-RIGHT: Digital POT 3
        # Giving this a purple accent to visually separate it as the Digital Pot
        self.pot3_dial = GXArcGauge(color="#b967ff", title="DIGITAL POT 3", max_val=4095)
        self.lbl_pot3_data = QLabel("ANALOG: 0 // VOLTS: 0.0V")
        grid.addWidget(self.create_pot_display(self.pot3_dial, self.lbl_pot3_data), 0, 1)

        # 4. BOTTOM-RIGHT: Command Signal & ESC Logic
        cmd_frame = QFrame()
        cmd_frame.setStyleSheet("background-color: #1a1a24; border: 1px solid #2a2a35; border-radius: 8px;")
        cmd_layout = QVBoxLayout(cmd_frame)
        cmd_layout.setContentsMargins(20, 20, 20, 20)
        cmd_layout.setSpacing(20)

        lbl_cmd = QLabel("DIGITAL POTENTIOMETER COMMAND")
        lbl_cmd.setStyleSheet("color: #8a8a93; font-weight: bold; border: none;")
        cmd_layout.addWidget(lbl_cmd, 0, Qt.AlignCenter)

        self.digi_pot_bar = QSlider(Qt.Horizontal)
        self.digi_pot_bar.setRange(0, 100)
        self.digi_pot_bar.setEnabled(False)
        cmd_layout.addWidget(self.digi_pot_bar)

        # Add the command block to the bottom-right cell, wrapped to prevent stretching
        grid.addWidget(self.wrap_in_center_frame(cmd_frame), 1, 1)

        # Apply the final grid to the tab
        self.content_layout.addLayout(grid)

    def create_pot_display(self, dial, label):
        """Wraps the dial and label in a layout that strictly centers them."""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setAlignment(Qt.AlignCenter)  # This is the magic lock against stretching
        layout.addWidget(dial, 0, Qt.AlignCenter)

        label.setStyleSheet("color: #8a8a93; font-weight: bold; margin-top: 10px;")
        layout.addWidget(label, 0, Qt.AlignCenter)
        return frame

    def wrap_in_center_frame(self, widget):
        """Ensures the bottom-right control panel hugs its contents tightly."""
        wrapper = QFrame()
        layout = QVBoxLayout(wrapper)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(widget)
        return wrapper