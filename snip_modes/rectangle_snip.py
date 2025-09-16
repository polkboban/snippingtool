#rectanglesnip

import pyautogui
from PyQt5.QtCore import Qt, QRect, QPoint, QTimer,pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog


class RectangleSnipOverlay(QWidget):
    snip_completed = pyqtSignal(object)

    def __init__(self, delay=0):
        super().__init__()
        self.delay = delay
        self.begin = QPoint()
        self.end = QPoint()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)

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
            painter.setBrush(Qt.NoBrush)
            rect = QRect(self.begin, self.end)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
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
        self.close()
