# snip_modes/freeform_snip.py

import pyautogui
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath
from PyQt5.QtWidgets import QApplication, QWidget
from PIL import Image, ImageDraw


class FreeformSnipOverlay(QWidget):
    snip_completed = pyqtSignal(object)  

    def __init__(self, delay=0):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)
        self.path = QPainterPath()
        self.fullscreen_image = None

        if delay > 0:
            QTimer.singleShot(delay * 1000, self.start_snipping)
        else:
            self.start_snipping()

    def start_snipping(self):
        self.fullscreen_image = pyautogui.screenshot()
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        pen = QPen(QColor(0, 255, 0), 2)
        painter.setPen(pen)
        painter.drawPath(self.path)

    def mousePressEvent(self, event):
        self.path.moveTo(event.pos())

    def mouseMoveEvent(self, event):
        self.path.lineTo(event.pos())
        self.update()

    def mouseReleaseEvent(self, event):
        self.hide()
        self.capture_freeform_area()
        self.close()

    def capture_freeform_area(self):
        if self.fullscreen_image is None:
            return

        # Convert to mask
        screen = self.fullscreen_image
        width, height = screen.size

        # Draw the path onto a mask
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)

        points = []
        for i in range(self.path.elementCount()):
            el = self.path.elementAt(i)
            points.append((int(el.x), int(el.y)))

        if len(points) > 1:
            draw.polygon(points, fill=255)

            # Apply mask to the screenshot
            result = Image.new("RGBA", screen.size)
            result.paste(screen, (0, 0), mask)

            self.snip_completed.emit(result)
