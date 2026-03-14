from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget

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
        self.fullscreen_pixmap = None

        if delay > 0:
            QTimer.singleShot(delay * 1000, self.start_snipping)
        else:
            self.start_snipping()

    def start_snipping(self):
        screen = QApplication.primaryScreen()
        self.fullscreen_pixmap = screen.grabWindow(0)
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
        self.path.moveTo(event.position())
        self.drawing = True

    def mouseMoveEvent(self, event):
        if hasattr(self, 'drawing') and self.drawing:
            self.path.lineTo(event.position())
            self.update()

    def mouseReleaseEvent(self, event):
        self.drawing = False
        self.hide()
        self.capture_freeform_area()
        self.close()

    def capture_freeform_area(self):
        if self.fullscreen_pixmap is None or self.path.isEmpty():
            self.snip_completed.emit(None)
            return

        cropped_pixmap = QPixmap(self.fullscreen_pixmap.size())
        cropped_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(cropped_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setClipPath(self.path)
        painter.drawPixmap(0, 0, self.fullscreen_pixmap)
        painter.end()

        bounding_rect = self.path.boundingRect().toRect()
        final_image = cropped_pixmap.copy(bounding_rect)

        self.snip_completed.emit(final_image)