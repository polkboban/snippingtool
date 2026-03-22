from PyQt6.QtCore import Qt, QRect, QRectF, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath
from PyQt6.QtWidgets import QWidget, QApplication

class RectangleSnipOverlay(QWidget):
    snip_completed = pyqtSignal(object)

    def __init__(self, screen_pixmap=None, delay=0):
        super().__init__()
        self.delay = delay
        self.begin = QPoint()
        self.end = QPoint()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

        if screen_pixmap:
            self.screen_pixmap = screen_pixmap
        else:
            self.screen_pixmap = QApplication.primaryScreen().grabWindow(0)

        if self.delay > 0:
            QTimer.singleShot(self.delay * 1000, self.showFullScreen)
        else:
            self.showFullScreen()
            

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.screen_pixmap)

        from PyQt6.QtCore import QRectF
        from PyQt6.QtGui import QPainterPath

        overlay_path = QPainterPath()
        overlay_path.addRect(QRectF(self.rect()))

        rect = None
        if not self.begin.isNull() and not self.end.isNull():
            rect = QRect(self.begin, self.end).normalized()
            selection_path = QPainterPath()
            selection_path.addRect(QRectF(rect))
            overlay_path = overlay_path.subtracted(selection_path)

        painter.fillPath(overlay_path, QColor(0, 0, 0, 100))

        if rect:
            pen = QPen(QColor(255, 0, 0), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)

            width = rect.width()
            height = rect.height()

            if width > 10 and height > 10:
                text = f"{width} × {height}"
                font = painter.font()
                font.setPointSize(10)
                font.setBold(True)
                painter.setFont(font)
                
                metrics = painter.fontMetrics()
                text_width = metrics.horizontalAdvance(text)
                text_height = metrics.height()
                
                text_x = self.end.x() + 15
                text_y = self.end.y() - text_height - 15
                
                if text_x + text_width + 10 > self.width():
                    text_x = self.end.x() - text_width - 15
                if text_y < 10:
                    text_y = self.end.y() + 20
                    text_x = self.end.x() - text_width - 15
                    
                bg_rect = QRect(text_x, text_y, text_width + 16, text_height + 8)
                
                painter.setBrush(QColor(20, 20, 20, 220))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(bg_rect, 6, 6)
                
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, text)

        mouse_pos = self.mapFromGlobal(self.cursor().pos())
        zoom_size = 40
        zoom_rect = QRect(mouse_pos.x() - zoom_size//2, mouse_pos.y() - zoom_size//2, zoom_size, zoom_size)
        zoomed_pixmap = self.screen_pixmap.copy(zoom_rect).scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio)
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        loupe_rect = QRect(mouse_pos.x() + 20, mouse_pos.y() + 20, 160, 160)
        
        if loupe_rect.right() > self.width():
            loupe_rect.moveLeft(mouse_pos.x() - 180)
        if loupe_rect.bottom() > self.height():
            loupe_rect.moveTop(mouse_pos.y() - 180)

        path = QPainterPath()
        path.addEllipse(QRectF(loupe_rect))
        painter.setClipPath(path)
        painter.drawPixmap(loupe_rect.topLeft(), zoomed_pixmap)
        
        painter.setClipping(False)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(loupe_rect)
        
        painter.setPen(QPen(QColor(0, 255, 0, 150), 1))
        painter.drawLine(loupe_rect.center().x(), loupe_rect.top(), loupe_rect.center().x(), loupe_rect.bottom())
        painter.drawLine(loupe_rect.left(), loupe_rect.center().y(), loupe_rect.right(), loupe_rect.center().y())

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

        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())
        width, height = x2 - x1, y2 - y1

        if width > 0 and height > 0:
            screenshot = self.screen_pixmap.copy(QRect(x1, y1, width, height))
            self.snip_completed.emit(screenshot)
        else:
            self.snip_completed.emit(None)
            
        self.close()