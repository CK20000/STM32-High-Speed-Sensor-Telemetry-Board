import os
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
import pyqtgraph as pg
from ui.base_tab import SensorTabBase


class Tab2_VLX(SensorTabBase):
    def __init__(self):
        super().__init__()

        self.setup_standard_header("VL53L0X: TIME-OF-FLIGHT DISTANCE", "ENABLE VLX STREAM")
        self.btn_pdf.clicked.connect(self.open_pdf)

        self.vlx_plot = pg.PlotWidget(title="Distance (mm)")
        self.vlx_plot.setBackground('#0f0f13')
        self.vlx_plot.showGrid(x=True, y=True, alpha=0.3)
        self.line_dist = self.vlx_plot.plot(pen=pg.mkPen(color='#00ffcc', width=2), name="mm")

        self.content_layout.addWidget(self.vlx_plot)

    def open_pdf(self):
        pdf_path = os.path.join(os.getcwd(), "datasheets", "vl53l0x.pdf")
        if os.path.exists(pdf_path): os.startfile(pdf_path)
