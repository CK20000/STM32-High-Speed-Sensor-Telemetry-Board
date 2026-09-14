import os
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QFrame, QSlider, QWidget)
from PySide6.QtCore import Qt
import pyqtgraph as pg
from ui.base_tab import SensorTabBase


class Tab6_MAG(SensorTabBase):
    def __init__(self):
        super().__init__()

        self.setup_standard_header("3-AXIS MAGNETOMETER & ESC SAFETY INTERLOCK", "ENABLE MAG STREAM")
        self.btn_pdf.clicked.connect(self.open_pdf)

        # MAIN SPLIT LAYOUT
        main_split = QVBoxLayout()
        main_split.setSpacing(20)

        # --- TOP SECTION: 3D PLOT (Takes majority of space) ---
        self.mag_plot = pg.PlotWidget(title="Magnetic Flux Density (μT)")
        self.mag_plot.setBackground('#0f0f13')
        self.mag_plot.showGrid(x=True, y=True, alpha=0.3)

        self.line_x = self.mag_plot.plot(pen=pg.mkPen(color='#fa1e4e', width=2), name="X")
        self.line_y = self.mag_plot.plot(pen=pg.mkPen(color='#00ffcc', width=2), name="Y")
        self.line_z = self.mag_plot.plot(pen=pg.mkPen(color='#b967ff', width=2), name="Z")

        main_split.addWidget(self.mag_plot, 4)  # Weight 4 (Stretches)

        # --- BOTTOM SECTION: ESC SAFETY BLOCK (THE UPGRADE) ---
        esc_frame = QFrame()
        esc_frame.setObjectName("escContainer")
        # The glowing neon box around the entire bottom row
        esc_frame.setStyleSheet("""
            QFrame#escContainer {
                background-color: #0f0f13;
                border: 2px solid #ff7f26; /* Your signature GX Orange */
                border-radius: 8px;
            }
        """)

        esc_layout = QHBoxLayout(esc_frame)
        esc_layout.setContentsMargins(20, 20, 20, 20)
        esc_layout.setSpacing(20)

        # 1. Left: Instructions
        lbl_instruct = QLabel("⚠ SAFETY INTERLOCK:\nMANUALLY TAKE POT 1 TO ZERO\nTO ENABLE MOTOR ARM SWITCH.")
        lbl_instruct.setStyleSheet("color: #8a8a93; font-weight: bold; border: none; font-size: 13px;")
        esc_layout.addWidget(lbl_instruct, 1, Qt.AlignLeft | Qt.AlignVCenter)

        # 2. Center: Arm Button
        self.btn_arm = QPushButton("LOCKED (BRING POT 1 TO 0)")
        self.btn_arm.setCheckable(True)
        self.btn_arm.setEnabled(False)
        self.btn_arm.setMinimumHeight(50)
        self.btn_arm.setMinimumWidth(300)
        self.btn_arm.setStyleSheet("""
            QPushButton {
                color: #ffaa00;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #ffaa00;
                border-radius: 5px;
                background-color: #1a1a24;
            }
        """)
        esc_layout.addWidget(self.btn_arm, 1, Qt.AlignCenter)

        # 3. Right: Duty Slider Indicator (With Custom GX Styling)
        slider_layout = QVBoxLayout()
        slider_layout.setSpacing(10)
        self.lbl_duty = QLabel("MOTOR COMMAND: 0% [SAFE]")
        self.lbl_duty.setStyleSheet("color: #00ffcc; font-weight: bold; border: none; font-size: 14px;")

        self.slider_duty = QSlider(Qt.Horizontal)
        self.slider_duty.setRange(0, 30)
        self.slider_duty.setEnabled(False)  # Indicator only
        # Strip away the ugly Windows default slider look
        self.slider_duty.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #2a2a35;
                height: 8px;
                background: #1a1a24;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00ffcc;
                border: 1px solid #00ffcc;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: rgba(0, 255, 204, 0.4);
                border-radius: 4px;
            }
        """)

        slider_layout.addWidget(self.lbl_duty, 0, Qt.AlignCenter)
        slider_layout.addWidget(self.slider_duty)

        # Wrap layout in a blank widget so Qt.AlignRight works perfectly
        slider_widget = QWidget()
        slider_widget.setLayout(slider_layout)
        slider_widget.setStyleSheet("border: none;")
        esc_layout.addWidget(slider_widget, 1, Qt.AlignRight | Qt.AlignVCenter)

        main_split.addWidget(esc_frame, 1)  # Weight 1 (Narrow)
        self.content_layout.addLayout(main_split)

    def update_esc_safety(self, pot1_val):
        """Evaluates safety logic and dynamically shifts CSS Colors"""
        duty = int((pot1_val / 4095.0) * 30.0)

        if not self.btn_arm.isChecked():
            # STATE: UNARMED
            self.slider_duty.setValue(0)
            self.lbl_duty.setText("MOTOR COMMAND: 0% [SAFE]")
            self.lbl_duty.setStyleSheet("color: #00ffcc; font-weight: bold; border: none; font-size: 14px;")

            if pot1_val <= 15:  # Tolerance for ADC noise near zero
                self.btn_arm.setEnabled(True)
                self.btn_arm.setText("ARM ESC MOTOR")
                self.btn_arm.setStyleSheet("""
                    QPushButton {
                        color: #00ffcc;
                        font-weight: bold;
                        font-size: 14px;
                        border: 2px solid #00ffcc;
                        border-radius: 5px;
                        background-color: #1a1a24;
                    }
                    QPushButton:hover { background-color: rgba(0, 255, 204, 0.15); }
                """)
            else:
                self.btn_arm.setEnabled(False)
                self.btn_arm.setText("LOCKED (BRING POT 1 TO 0)")
                self.btn_arm.setStyleSheet("""
                    QPushButton {
                        color: #ffaa00;
                        font-weight: bold;
                        font-size: 14px;
                        border: 2px solid #ffaa00;
                        border-radius: 5px;
                        background-color: #1a1a24;
                    }
                """)
        else:
            # STATE: ARMED & LIVE
            self.btn_arm.setText("ESC ARMED [LIVE]")
            self.btn_arm.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 255, 204, 0.25); 
                    color: #ffffff; 
                    font-weight: bold; 
                    font-size: 14px;
                    border: 2px solid #00ffcc; 
                    border-radius: 5px;
                }
            """)
            self.slider_duty.setValue(duty)
            self.lbl_duty.setText(f"MOTOR COMMAND: {duty}% [HOT]")
            # Switch text to Neon Red when the prop is spinning!
            self.lbl_duty.setStyleSheet("color: #fa1e4e; font-weight: bold; border: none; font-size: 14px;")

    def open_pdf(self):
        pdf_path = os.path.join(os.getcwd(), "datasheets", "hmc5883l.pdf")
        if os.path.exists(pdf_path): os.startfile(pdf_path)