#rectanglesnip

import pyautogui
from PyQt6.QtCore import Qt, QRect, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QWidget

class RectangleSnipOverlay(QWidget):
    snip_completed = pyqtSignal(object)

    def __init__(self, delay=0):
        super().__init__()
        self.delay = delay
        self.begin = QPoint()
        self.end = QPoint()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

        if self.delay > 0:
            QTimer.singleShot(self.delay * 1000, self.showFullScreen)
        else:
            self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        if not self.begin.isNull() and not self.end.isNull():
            pen = QPen(QColor(255, 0, 0), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            rect = QRect(self.begin, self.end)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        self.begin = event.position().toPoint()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.position().toPoint()
        self.hide()

        scale = self.devicePixelRatioF()
        x1 = int(min(self.begin.x(), self.end.x()) * scale)
        y1 = int(min(self.begin.y(), self.end.y()) * scale)
        x2 = int(max(self.begin.x(), self.end.x()) * scale)
        y2 = int(max(self.begin.y(), self.end.y()) * scale)
        width, height = x2 - x1, y2 - y1

        if width > 0 and height > 0:
            screenshot = pyautogui.screenshot(region=(x1, y1, width, height))
            self.snip_completed.emit(screenshot)
        else:
            self.snip_completed.emit(None)
            
        self.close()