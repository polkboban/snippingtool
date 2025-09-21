import sys
import ctypes
import win32gui
import pyautogui
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]

def get_window_rect_dwm(hwnd):
    rect = RECT()
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    ctypes.windll.dwmapi.DwmGetWindowAttribute(
        hwnd, DWMWA_EXTENDED_FRAME_BOUNDS, ctypes.byref(rect), ctypes.sizeof(rect)
    )
    return rect.left, rect.top, rect.right, rect.bottom

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

            if hwnd and hwnd != self.winId():
                rect = get_window_rect_dwm(hwnd)
                self.highlight_rect = QRect(rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
            else:
                self.highlight_rect = None
        except Exception as e:
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
        
        region_rect = (
            self.highlight_rect.x(),
            self.highlight_rect.y(),
            self.highlight_rect.width(),
            self.highlight_rect.height()
        )
        
        try:
            screenshot = pyautogui.screenshot(region=region_rect)
            self.snip_completed.emit(screenshot)
        except Exception as e:
            self.snip_completed.emit(None)
        
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.snip_completed.emit(None)
            self.close()