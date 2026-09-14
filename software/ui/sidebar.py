from PySide6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QButtonGroup
from PySide6.QtGui import QPainter, QColor, QPolygon, QPen
from PySide6.QtCore import Qt, QPoint

class GXSidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(60) # Slim, icon-only width like Opera GX
        self.setObjectName("gxSidebar")

        # Inside GXSidebar.__init__:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        layout.addStretch() # TOP STRETCH (Pushes buttons down)
        
        # Button Group to handle the "Active Tab" state logic
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        
        # Your 6 Sensor Sections mapped to buttons
        self.sections = [
            {"id": 0, "name": "HOME", "icon": "H"},
            {"id": 1, "name": "ACCELEROMETERS", "icon": "S1"}, # Accels & Heater
            {"id": 2, "name": "DISTANCE", "icon": "S2"}, # Time of Flight
            {"id": 3, "name": "ENCODERS", "icon": "S3"}, # Encoders
            {"id": 4, "name": "LOAD CELL & PRESSURE", "icon": "S4"}, # Load Cell / Pressure
            {"id": 5, "name": "POTENTIOMETER", "icon": "S5"}, # Pots & ESC
            {"id": 6, "name": "MAG", "icon": "M"},
            {"id": 7, "name": "DEBUG", "icon": "🧰"}  # I2C Error / Status
        ]
        
        self.buttons = {}
        for sec in self.sections:
            btn = QPushButton(sec["icon"])
            btn.setCheckable(True)
            btn.setObjectName("sidebarBtn")
            btn.setToolTip(sec["name"]) # Shows name on hover
            btn.setFixedSize(40, 40)
            
            self.btn_group.addButton(btn, sec["id"])
            layout.addWidget(btn, 0, Qt.AlignHCenter)
            self.buttons[sec["id"]] = btn
            
        layout.addStretch() # Pushes all buttons to the top

    # --- THE MAGIC: Drawing the custom GX Chamfered Edge ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Base background color
        painter.fillRect(self.rect(), QColor("#0f0f13"))
        
        # Draw the neon red angled cut at the top left
        pen = QPen(QColor("#fa1e4e"))
        pen.setWidth(2)
        painter.setPen(pen)
        
        # The coordinates for the polygon (The angled chamfer)
        points = QPolygon([
            QPoint(20, 0),         # Start slightly right on top edge
            QPoint(self.width(), 0), # Top right
            QPoint(self.width(), self.height()), # Bottom right
            QPoint(0, self.height()), # Bottom left
            QPoint(0, 20)          # Go up, but stop before the top to make the cut
        ])
        
        #painter.drawPolyline([QPoint(0, 20), QPoint(20, 0)]) # The actual red angle cut
