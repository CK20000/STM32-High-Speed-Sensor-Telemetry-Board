import os
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
import pyqtgraph as pg
from ui.base_tab import SensorTabBase


class Tab4_LDC(SensorTabBase):
    def __init__(self):
        super().__init__()

        self.setup_standard_header("LOAD CELL & BAROMETRIC PRESSURE", "ENABLE SENSOR STREAM")
        self.btn_pdf.clicked.connect(self.open_pdf)

        plot_layout = QHBoxLayout()

        self.load_plot = pg.PlotWidget(title="HX711 Load Cell (Grams)")
        self.load_plot.setBackground('#0f0f13')
        self.load_plot.showGrid(x=True, y=True, alpha=0.3)
        self.line_weight = self.load_plot.plot(pen=pg.mkPen(color='#fa1e4e', width=2))

        self.press_plot = pg.PlotWidget(title="BMP280 Pressure (hPa)")
        self.press_plot.setBackground('#0f0f13')
        self.press_plot.showGrid(x=True, y=True, alpha=0.3)
        self.line_press = self.press_plot.plot(pen=pg.mkPen(color='#ffaa00', width=2))

        plot_layout.addWidget(self.load_plot)
        plot_layout.addWidget(self.press_plot)
        self.content_layout.addLayout(plot_layout)

    def open_pdf(self):
        pdf_path = os.path.join(os.getcwd(), "datasheets", "hx711_bmp280.pdf")
        if os.path.exists(pdf_path): os.startfile(pdf_path)
