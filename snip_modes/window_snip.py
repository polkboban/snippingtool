import win32gui
from io import BytesIO
from PIL import Image
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QBuffer
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor

def get_top_level_hwnd(hwnd):
    parent_hwnd = win32gui.GetParent(hwnd)
    while parent_hwnd:
        hwnd = parent_hwnd
        parent_hwnd = win32gui.GetParent(hwnd)
    return hwnd

class WindowSnipOverlay(QWidget):
    snip_completed = pyqtSignal(object)

    def __init__(self, delay=0):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        screen_geometry = QApplication.instance().desktop().geometry()
        self.setGeometry(screen_geometry)
        
        self.highlight_rect = None
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)
        self.show()

    def mouseMoveEvent(self, event):
        try:
            pos = QCursor.pos()
            hwnd = win32gui.WindowFromPoint((pos.x(), pos.y()))
            
            top_level_hwnd = get_top_level_hwnd(hwnd)

            if top_level_hwnd != self.winId() and top_level_hwnd != 0:
                rect = win32gui.GetWindowRect(top_level_hwnd)
                self.highlight_rect = QRect(rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
            else:
                self.highlight_rect = None
        except Exception:
            self.highlight_rect = None
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        
        painter.fillRect(self.rect(), QColor(0, 0, 0, 70))
        
        if self.highlight_rect:
            pen = QPen(QColor(255, 0, 0), 3, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(self.highlight_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.highlight_rect:
            self.capture_snip()

    def capture_snip(self):
        self.hide()
        
        screen = QApplication.primaryScreen()
        if screen:
            pixmap = screen.grabWindow(0, self.highlight_rect.x(), self.highlight_rect.y(), self.highlight_rect.width(), self.highlight_rect.height())
            
            # Manual conversion from QPixmap to PIL Image
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            pixmap.save(buffer, "PNG")
            pil_image = Image.open(BytesIO(buffer.data()))
            
            self.snip_completed.emit(pil_image)
        
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.snip_completed.emit(None)
            self.close()