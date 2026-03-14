#freeformsnip

import pyautogui
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath
from PyQt6.QtWidgets import QApplication, QWidget
from PIL import Image, ImageDraw

class FreeformSnipOverlay(QWidget):
    snip_completed = pyqtSignal(object)  

    def __init__(self, delay=0):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        pen = QPen(QColor(0, 255, 0), 2)
        painter.setPen(pen)
        painter.drawPath(self.path)

    def mousePressEvent(self, event):
        self.path = QPainterPath()
        self.path.moveTo(event.position().toPointF())
        self.drawing = True

    def mouseMoveEvent(self, event):
        if hasattr(self, 'drawing') and self.drawing:
            self.path.lineTo(event.position().toPointF())
            self.update()

    def mouseReleaseEvent(self, event):
        self.drawing = False
        self.hide()
        self.capture_freeform_area()
        self.close()

    def capture_freeform_area(self):
        if self.fullscreen_image is None:
            return

        screen = self.fullscreen_image
        width, height = screen.size

        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)

        points = []
        scale = self.devicePixelRatioF()
        for i in range(self.path.elementCount()):
            el = self.path.elementAt(i)
            points.append((int(el.x * scale), int(el.y * scale)))

        if len(points) > 2:
            draw.polygon(points, fill=255)

            result = Image.new("RGBA", screen.size)
            result.paste(screen, (0, 0), mask)

            bbox = mask.getbbox()
            if bbox:
                result = result.crop(bbox)
                self.snip_completed.emit(result)
            else:
                self.snip_completed.emit(None)
        else:
            self.snip_completed.emit(None)