import sys
import os
import pyqtgraph as pg
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QFrame, QTabWidget, QTabBar)
from PySide6.QtCore import Qt, QPoint
# --- WE NEED THESE TO DRAW THE CHAMFER ON THE TITLE BAR ---
from PySide6.QtGui import QPainter, QColor, QPen

from ui.sidebar import GXSidebar
from ui.tab_manager import TabManager

#pg.setConfigOptions(useOpenGL=True, antialias=True)

class CustomTitleBar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("titleBar")
        self.setFixedHeight(40)  # Slightly taller to fit the bigger text

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title (Now targeting #mainTitle in CSS)
        title_label = QLabel("SENSOR DASHBOARD-GX")
        title_label.setObjectName("mainTitle")
        layout.addWidget(title_label)
        layout.addStretch()

        # Minimize Button
        min_btn = QPushButton("—")
        min_btn.setObjectName("titleBtn")
        min_btn.clicked.connect(self.parent.showMinimized)
        layout.addWidget(min_btn)

        # Close Button
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.clicked.connect(self.parent.close)
        layout.addWidget(close_btn)

        self.start_pos = None

    # --- THE TITLE BAR CHAMFER MAGIC ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Base Title Bar Background
        painter.fillRect(self.rect(), QColor("#1a1a24"))

        # Neon Red Pen
        pen = QPen(QColor("#fa1e4e"))
        pen.setWidth(2)
        painter.setPen(pen)

        w = self.width()
        h = self.height()
        c = 20  # The size of the top-left chamfer cut

        # 1. Draw Top-Left Angled Chamfer
        painter.drawLine(QPoint(0, c), QPoint(c, 0))
        # 2. Draw Top Border
        painter.drawLine(QPoint(c, 0), QPoint(w, 0))
        # 3. Draw Bottom Border (Separates title bar from the rest of the app)
        painter.drawLine(QPoint(0, h), QPoint(w, h))

    # --- Window Drag Logic ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.start_pos is not None:
            delta = event.globalPosition().toPoint() - self.start_pos
            self.parent.move(self.parent.pos() + delta)
            self.start_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.start_pos = None


class DashboardCore(QMainWindow):
    def __init__(self):
        super().__init__()

        # KILL THE WINDOWS FRAME
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Add Custom Title Bar
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # 4. THE MASTER HORIZONTAL TAB SYSTEM
        self.master_tabs = QTabWidget()
        self.master_tabs.setTabsClosable(True)
        self.master_tabs.tabCloseRequested.connect(self.close_document_tab)

        # 5. Build the Telemetry Dashboard (Sidebar + Graphs)
        dashboard_widget = QWidget()
        dash_layout = QHBoxLayout(dashboard_widget)
        dash_layout.setContentsMargins(0, 0, 0, 0)
        dash_layout.setSpacing(0)

        self.sidebar = GXSidebar()
        self.tabs = TabManager()
        dash_layout.addWidget(self.sidebar)
        dash_layout.addWidget(self.tabs)

        # Bridge Sidebar to Tab Manager
        self.sidebar.btn_group.idClicked.connect(self.tabs.setCurrentIndex)

        # --- ADD THIS LINE: Force the Sidebar to highlight 'HOME' on startup ---
        self.sidebar.btn_group.button(0).setChecked(True)

        # Lock the Dashboard as Tab Index 0 and remove its close button!
        self.master_tabs.addTab(dashboard_widget, "\\")
        self.master_tabs.tabBar().setTabButton(0, QTabBar.RightSide, None)

        # Add the Master Tabs to the Main Window
        main_layout.addWidget(self.master_tabs)

        # 6. HIJACK THE "!" BUTTONS (Without touching the tab files!)
        self.hijack_pdf_buttons()

    def hijack_pdf_buttons(self):
        """Intercepts clicks from SensorTabBase and routes them to new Tabs"""

        # Map your specific tabs to the exact PDF file you want to open
        pdf_map = [
            (self.tabs.tab1, "ACCELEROMETER", "datasheets/mpu6050.pdf"),
            (self.tabs.tab2, "TIME OF FLIGHT", "datasheets/vl53l0x.pdf"),
            (self.tabs.tab3, "ENCODER", "datasheets/encoder.pdf"),
            (self.tabs.tab4, "LOAD CELL AND PRESSURE", "datasheets/loadcell.pdf"),
            (self.tabs.tab5, "POTENTIOMETERS", "datasheets/pot.pdf"),
            (self.tabs.tab6, "MAGNETOMETER", "datasheets/hmc5883l.pdf")
        ]

        for tab_instance, doc_title, filepath in pdf_map:
            if hasattr(tab_instance, 'btn_pdf'):
                # 1. Sever the EXACT connection to silence the RuntimeWarning
                try:
                    tab_instance.btn_pdf.clicked.disconnect(tab_instance.open_pdf)
                except Exception:
                    pass

                    # 2. Wire it to our new Horizontal Tab Spawner
                tab_instance.btn_pdf.clicked.connect(
                    lambda checked=False, t=doc_title, p=filepath: self.spawn_pdf_tab(t, p)
                )

    def spawn_pdf_tab(self, title, path):
        """Creates a new Horizontal Tab containing the PDF Viewer"""
        # First, check if the document is already open. If so, just switch to it!
        for i in range(self.master_tabs.count()):
            if self.master_tabs.tabText(i) == title:
                self.master_tabs.setCurrentIndex(i)
                return

        # If not open, build the viewer and spawn the tab
        from ui.pdf_viewer import GXPDFViewer
        viewer = GXPDFViewer(path)
        idx = self.master_tabs.addTab(viewer, title)

        # Instantly switch focus to the new document
        self.master_tabs.setCurrentIndex(idx)

    def close_document_tab(self, index):
        """Closes the tab when the X is clicked"""
        if index > 0:  # Failsafe: Never allow closing the main Dashboard (Index 0)
            self.master_tabs.removeTab(index)

    def closeEvent(self, event):
        """Safely shuts down the serial thread before closing"""
        self.tabs.stop_bridge()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load our external Opera GX style sheet
    qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
    else:
        print("Warning: style.qss not found!")

    window = DashboardCore()
    window.show()
    sys.exit(app.exec())
