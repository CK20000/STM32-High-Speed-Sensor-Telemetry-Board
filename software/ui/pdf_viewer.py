# ui/pdf_viewer.py
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

# Try to load the native PDF engine
try:
    from PySide6.QtPdf import QPdfDocument
    from PySide6.QtPdfWidgets import QPdfView

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class GXPDFViewer(QWidget):
    def __init__(self, pdf_path):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: #0f0f13;")

        # Fallback if the pip install failed
        if not PDF_AVAILABLE:
            lbl = QLabel("NATIVE PDF ENGINE MISSING.\nRun: pip install PySide6-pdf")
            lbl.setStyleSheet("color: #fa1e4e; font-size: 18px; font-weight: bold;")
            layout.addWidget(lbl, alignment=Qt.AlignCenter)
            return

        # Fallback if the PDF file doesn't exist
        if not os.path.exists(pdf_path):
            lbl = QLabel(f"DOCUMENT NOT FOUND:\n{pdf_path}")
            lbl.setStyleSheet("color: #ffaa00; font-size: 18px; font-weight: bold;")
            layout.addWidget(lbl, alignment=Qt.AlignCenter)
            return

        # 1. Load the Document into RAM
        self.doc = QPdfDocument(self)
        self.doc.load(pdf_path)

        # 2. Render it to the Screen
        self.view = QPdfView(self)
        self.view.setDocument(self.doc)

        # --- THE FIX: Enable Continuous Multi-Page Scrolling! ---
        self.view.setPageMode(QPdfView.PageMode.MultiPage)

        # Fit to width so you don't have to scroll horizontally!
        self.view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        self.view.setStyleSheet("background-color: #2a2a35; border: none;")

        layout.addWidget(self.view)