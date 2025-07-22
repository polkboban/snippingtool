import sys
import pyautogui
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

class SnippingWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.X11BypassWindowManagerHint  
        )
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        self.begin = QPoint()
        self.end = QPoint()
        self.setCursor(Qt.CrossCursor)
        self.showFullScreen()

        print("snipping tool active: click and drag to select area.")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

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
        width = x2 - x1
        height = y2 - y1

        print(f"Captured region: ({x1}, {y1}, {width}x{height})")

        if width > 0 and height > 0:
            screenshot = pyautogui.screenshot(region=(x1, y1, width, height))
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", "", "PNG Files (*.png);;All Files (*)")
            if file_path:
                screenshot.save(file_path)

        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    snip = SnippingWidget()
    sys.exit(app.exec_())
