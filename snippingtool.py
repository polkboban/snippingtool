import sys
import pyautogui
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog

class SnippingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowState(Qt.WindowFullScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.begin = self.end = None
        self.show()

    def paintEvent(self, event):
        if self.begin and self.end:
            qp = QPainter(self)
            qp.setPen(QPen(QColor("red"), 2))
            qp.setBrush(QColor(0, 0, 0, 100))  # Dark transparent background
            qp.drawRect(0, 0, self.width(), self.height())
            rect = QRect(self.begin, self.end)
            qp.setBrush(Qt.NoBrush)
            qp.drawRect(rect)

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())
        self.hide()

        # Take screenshot of selected region
        img = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))

        # Save dialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", "", "PNG Files (*.png);;All Files (*)")
        if file_path:
            img.save(file_path)

        QApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SnippingWidget()
    sys.exit(app.exec_())
