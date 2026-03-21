import ctypes
import win32gui
import pyautogui
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QPen, QColor

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]

def get_precise_rect(hwnd):
    """Try to get the tight visual bounds (no invisible drop shadows), fallback to standard bounds."""
    try:
        rect = RECT()
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        ctypes.windll.dwmapi.DwmGetWindowAttribute(
            hwnd, DWMWA_EXTENDED_FRAME_BOUNDS, ctypes.byref(rect), ctypes.sizeof(rect)
        )
        return rect.left, rect.top, rect.right, rect.bottom
    except Exception:
        return win32gui.GetWindowRect(hwnd)

def get_window_under_cursor(x, y, ignore_hwnd):
    """Finds the topmost window underneath the cursor, ignoring the snipping tool overlay."""
    found_hwnd = None
    
    def callback(hwnd, extra):
        nonlocal found_hwnd
        
        if hwnd == ignore_hwnd or not win32gui.IsWindowVisible(hwnd) or win32gui.IsIconic(hwnd):
            return True
            
        class_name = win32gui.GetClassName(hwnd)
        if class_name in ("Progman", "WorkerW", "Shell_TrayWnd"):
            return True
            
        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        except Exception:
            return True
            
        if left <= x <= right and top <= y <= bottom:
            found_hwnd = hwnd
            return False 
            
        return True
        
    win32gui.EnumWindows(callback, None)
    return found_hwnd

class WindowSnipOverlay(QWidget):
    snip_completed = pyqtSignal(object)

    def __init__(self, screen_pixmap=None, delay=0):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.screen_pixmap = screen_pixmap
        
        screen_geometry = QApplication.primaryScreen().virtualGeometry()
        self.setGeometry(screen_geometry)
        
        self.physical_rect = None
        self.logical_rect = None
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.show()

    def mouseMoveEvent(self, event):
        try:
            physical_x, physical_y = pyautogui.position()
            
            hwnd = get_window_under_cursor(physical_x, physical_y, int(self.winId()))
            
            if hwnd:
                left, top, right, bottom = get_precise_rect(hwnd)
                width = right - left
                height = bottom - top
                
                self.physical_rect = (left, top, width, height)
                
                scale = self.devicePixelRatioF()
                self.logical_rect = QRect(
                    int(left / scale), 
                    int(top / scale), 
                    int(width / scale), 
                    int(height / scale)
                )
            else:
                self.physical_rect = None
                self.logical_rect = None
                
        except Exception as e:
            print(f"Tracking error: {e}")
            self.physical_rect = None
            self.logical_rect = None
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 70))
        
        if self.logical_rect:
            pen = QPen(QColor(255, 0, 0), 3, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawRect(self.logical_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.physical_rect:
            self.capture_snip()

    def capture_snip(self):
        self.hide()
        try:
            # Huge fix here! Use the pre-grabbed pixmap so the toolbar isn't captured!
            if self.screen_pixmap:
                screenshot = self.screen_pixmap.copy(self.logical_rect)
            else:
                screen = QApplication.primaryScreen()
                screenshot = screen.grabWindow(0, self.logical_rect.x(), self.logical_rect.y(), self.logical_rect.width(), self.logical_rect.height())
                
            self.snip_completed.emit(screenshot)
        except Exception as e:
            print(f"Capture error: {e}")
            self.snip_completed.emit(None)
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.snip_completed.emit(None)
            self.close()