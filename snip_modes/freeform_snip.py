from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget

class FreeformSnipOverlay(QWidget):
    snip_completed = pyqtSignal(object)  

    def __init__(self, screen_pixmap=None, delay=0):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.path = QPainterPath()
        
        self.screen_pixmap = screen_pixmap

        if delay > 0:
            QTimer.singleShot(delay * 1000, self.start_snipping)
        else:
            self.start_snipping()

    def start_snipping(self):
        if not self.screen_pixmap:
            screen = QApplication.primaryScreen()
            self.screen_pixmap = screen.grabWindow(0)
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        from PyQt6.QtCore import QRectF
        from PyQt6.QtGui import QPainterPath

        overlay_path = QPainterPath()
        overlay_path.addRect(QRectF(self.rect()))

        if not self.path.isEmpty():
            selection_path = QPainterPath(self.path)
            selection_path.closeSubpath()
            overlay_path = overlay_path.subtracted(selection_path)

        painter.fillPath(overlay_path, QColor(0, 0, 0, 100))

        pen = QPen(QColor(255, 255, 255), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
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
        if self.screen_pixmap is None or self.path.isEmpty():
            self.snip_completed.emit(None)
            return

        cropped_pixmap = QPixmap(self.screen_pixmap.size())
        cropped_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(cropped_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setClipPath(self.path)
        painter.drawPixmap(0, 0, self.screen_pixmap)
        painter.end()

        bounding_rect = self.path.boundingRect().toRect()
        final_image = cropped_pixmap.copy(bounding_rect)

        self.snip_completed.emit(final_image)