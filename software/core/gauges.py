# Create new file: core/gauges.py
import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QPolygonF, QRadialGradient


class GX360Dial(QWidget):
    def __init__(self, dual_mode=False, color1="#00ffcc", color2="#fa1e4e"):
        super().__init__()
        self.setMinimumSize(250, 250)
        self.dual_mode = dual_mode
        self.val1 = 0  # Cyan hand (Optical)
        self.val2 = 0  # Neon Red hand (Magnetic)
        self.color1_hex = color1
        self.color2_hex = color2
        self.val_label_text = "DEG"

    def update_values(self, v1, v2=0):
        self.val1 = v1 % 360
        self.val2 = v2 % 360
        self.update()  # Triggers a GPU repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Center coordinates and radius
        cx = self.width() / 2
        cy = self.height() / 2
        radius = min(cx, cy) - 20

        # 1. Draw the Background and Main Ring
        # Use a radial gradient for depth
        gradient = QRadialGradient(cx, cy, radius)
        gradient.setColorAt(0, QColor("#1a1a24"))
        gradient.setColorAt(0.9, QColor("#121217"))
        painter.setBrush(gradient)
        painter.setPen(QPen(QColor("#2a2a35"), 4))
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

        # 2. Draw Ticks
        painter.setPen(QPen(QColor("#555566"), 1.5))
        for deg in range(0, 360, 10):
            rad = math.radians(deg - 90)
            inner_r = radius - 15
            outer_r = radius
            if deg % 90 == 0:
                inner_r = radius - 25
                painter.setPen(QPen(QColor("#ffffff"), 2))
            else:
                painter.setPen(QPen(QColor("#555566"), 1.5))

            x1 = cx + inner_r * math.cos(rad)
            y1 = cy + inner_r * math.sin(rad)
            x2 = cx + outer_r * math.cos(rad)
            y2 = cy + outer_r * math.sin(rad)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # 3. Draw Hands (Needles)
        # Helper function to create the hand polygon using trig
        def create_hand_poly(val, length_factor, width_factor):
            rad = math.radians(val - 90)
            length = radius * length_factor
            width = 12 * width_factor

            p_tip = QPointF(cx + length * math.cos(rad), cy + length * math.sin(rad))
            p_left = QPointF(cx + width * math.cos(rad - math.pi / 2), cy + width * math.sin(rad - math.pi / 2))
            p_right = QPointF(cx + width * math.cos(rad + math.pi / 2), cy + width * math.sin(rad + math.pi / 2))

            #poly = QPolygonF([cx, cy, p_left, p_tip, p_right])
            poly = QPolygonF([QPointF(cx, cy), p_left, p_tip, p_right])
            return poly

        # Draw Hand 1 (Cyan)
        hand1_poly = create_hand_poly(self.val1, 0.95, 1.0)
        painter.setBrush(QColor(self.color1_hex))
        painter.setPen(Qt.NoPen)
        painter.drawPolygon(hand1_poly)

        # Draw Hand 2 (Red) if in Dual Mode
        if self.dual_mode:
            hand2_poly = create_hand_poly(self.val2, 0.8, 1.2)
            painter.setBrush(QColor(self.color2_hex))
            painter.drawPolygon(hand2_poly)

        # 4. Draw center pivot
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(QPointF(cx, cy), 12, 12)

        # 5. Draw Digital Display text
        painter.setPen(QColor("#ffffff"))
        painter.setFont(self.parent().font())  # Use application font
        display_text = f"{int(self.val1)}°"
        if self.dual_mode:
            display_text += f" // {int(self.val2)}°"
        painter.drawText(self.rect(), Qt.AlignBottom | Qt.AlignHCenter, display_text)


# --- THE NEW ARC GAUGE (For Tab 5 Potentiometers) ---
class GXArcGauge(QWidget):
    def __init__(self, color="#00ffcc", title="DATA", max_val=360):
        super().__init__()
        self.setMinimumSize(220, 220)
        self.val = 0
        self.max_val = max_val
        self.color_hex = color
        self.title = title

    def update_value(self, v):
        self.val = v
        self.update()  # Trigger GPU repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Make it a perfect square in the center of the widget
        side = min(self.width(), self.height())
        rect = QRectF((self.width() - side) / 2 + 20, (self.height() - side) / 2 + 20, side - 40, side - 40)

        # 1. Background Dark Track
        pen_bg = QPen(QColor("#2a2a35"), 18, Qt.SolidLine, Qt.FlatCap)
        painter.setPen(pen_bg)
        # PySide Angles: 16th of a degree. Start bottom-left (225°), Span 270° clockwise (negative span)
        painter.drawArc(rect, 225 * 16, -270 * 16)

        # 2. Glowing Value Arc
        pen_val = QPen(QColor(self.color_hex), 18, Qt.SolidLine, Qt.FlatCap)
        painter.setPen(pen_val)

        # Calculate how much of the arc to fill based on the current value
        # Prevent division by zero or over-drawing
        safe_val = min(max(self.val, 0), self.max_val)
        span = int((-270 * (safe_val / self.max_val)) * 16)
        painter.drawArc(rect, 225 * 16, span)

        # 3. Main Number Display (Shifted slightly up)
        painter.setPen(QColor("#ffffff"))
        font = painter.font()
        font.setPointSize(36)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect().adjusted(0, -20, 0, 0), Qt.AlignCenter, f"{int(self.val)}")

        # 4. Title / Subtext (Shifted up to sit under the number)
        font.setPointSize(12)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QColor("#8a8a93"))
        painter.drawText(self.rect().adjusted(0, 50, 0, 0), Qt.AlignCenter, self.title)