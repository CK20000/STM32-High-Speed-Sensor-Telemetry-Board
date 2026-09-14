import os
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QSlider, QCheckBox, QFrame)
from PySide6.QtCore import Qt
import pyqtgraph as pg
from ui.base_tab import SensorTabBase


class Tab1_ACC(SensorTabBase):
    def __init__(self):
        super().__init__()

        self.setup_standard_header("ACCELEROMETER & THERMAL DRIFT ANALYSIS", "ENABLE DUAL MPU6050 I2C STREAM")
        self.btn_pdf.clicked.connect(self.open_pdf)

        plot_layout = QHBoxLayout()

        # --- ACC 1 (0x68) ---
        self.plot1_frame = QVBoxLayout()
        self.plot1 = pg.PlotWidget(title="ACC 1 (0x68)")
        self.plot1.setBackground('#0f0f13')
        # Capture lines into line1 variables!
        self.line1_x, self.line1_y, self.line1_z = self.setup_plot_lines(self.plot1)
        self.plot1_frame.addWidget(self.plot1)
        self.plot1_frame.addLayout(self.create_xyz_toggles(1))

        # --- ACC 2 (0x69) ---
        self.plot2_frame = QVBoxLayout()
        self.plot2 = pg.PlotWidget(title="ACC 2 (0x69)")
        self.plot2.setBackground('#0f0f13')
        # Capture lines into line2 variables!
        self.line2_x, self.line2_y, self.line2_z = self.setup_plot_lines(self.plot2)
        self.plot2_frame.addWidget(self.plot2)
        self.plot2_frame.addLayout(self.create_xyz_toggles(2))

        plot_layout.addLayout(self.plot1_frame)
        plot_layout.addLayout(self.plot2_frame)
        self.content_layout.addLayout(plot_layout)

        # --- HEATING ELEMENT CONTROLS ---
        heater_frame = QFrame()
        heater_frame.setObjectName("heaterFrame")
        heater_frame.setStyleSheet("border: 1px solid #2a2a35; border-radius: 5px; padding: 10px;")
        heater_layout = QHBoxLayout(heater_frame)

        self.btn_heater_enable = QPushButton("ENABLE HEATER")
        self.btn_heater_enable.setCheckable(True)

        self.pwm_slider = QSlider(Qt.Horizontal)
        self.pwm_slider.setRange(0, 100)
        self.pwm_slider.setEnabled(False)

        self.lbl_temp = QLabel("TEMP: 24.0 °C")
        self.lbl_temp.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")

        heater_layout.addWidget(self.btn_heater_enable)
        heater_layout.addWidget(QLabel("PWM: "))
        heater_layout.addWidget(self.pwm_slider)
        heater_layout.addWidget(self.lbl_temp)

        self.content_layout.addWidget(heater_frame)
        self.btn_heater_enable.toggled.connect(self.pwm_slider.setEnabled)

    def setup_plot_lines(self, plot_widget):
        plot_widget.showGrid(x=True, y=True, alpha=0.3)
        # We don't save to 'self' here anymore, we just return them
        lx = plot_widget.plot(pen=pg.mkPen(color='#fa1e4e', width=2), name="X")
        ly = plot_widget.plot(pen=pg.mkPen(color='#00ffcc', width=2), name="Y")
        lz = plot_widget.plot(pen=pg.mkPen(color='#ffaa00', width=2), name="Z")
        return lx, ly, lz

    def create_xyz_toggles(self, acc_num):
        layout = QHBoxLayout()
        for axis in ['X', 'Y', 'Z']:
            cb = QCheckBox(f"Show {axis}")
            cb.setChecked(True)
            cb.setStyleSheet("color: #8a8a93;")
            layout.addWidget(cb)
        layout.addStretch()
        return layout

    def open_pdf(self):
        pdf_path = os.path.join(os.getcwd(), "datasheets", "mpu6050_heater.pdf")
        if os.path.exists(pdf_path): os.startfile(pdf_path)
