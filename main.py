import sys
import platform
import winreg
import keyboard
import pywinstyles

from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMenu, QMessageBox, QFileDialog, QFrame,
    QGraphicsView, QGraphicsScene, QGraphicsDropShadowEffect, QStackedWidget, QGraphicsRectItem
)
from PyQt6.QtGui import (
    QPixmap, QColor, QFont, QIcon, QPainter, QAction,
    QPainterPath, QPen, QShortcut, QKeySequence, QLinearGradient
)
from PyQt6.QtCore import Qt, QTimer, QSize, QByteArray, pyqtSignal, QThread, QPropertyAnimation, QEasingCurve, QPoint, QVariantAnimation, QRectF
from snip_modes.rectangle_snip import RectangleSnipOverlay
from snip_modes.freeform_snip import FreeformSnipOverlay
from snip_modes.window_snip import WindowSnipOverlay
from snip_modes.video_snip import VideoSnipOverlay

SVG_ICONS = {
    "play": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>""",
    "pause": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>""",
    "close" : """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-x-icon lucide-x"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>""",
    "record": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="4" fill="{color}"></circle></svg>""",
    "blur": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path></svg>""",
    "text": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7V4h16v3M9 20h6M12 4v16"/></svg>""",
    "rect_tool": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect></svg>""",
    "plus": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="6" ry="6" fill="{color}"></rect><line x1="12" y1="8" x2="12" y2="16" stroke="#7c3aed" stroke-width="2.5" stroke-linecap="round"></line><line x1="8" y1="12" x2="16" y2="12" stroke="#7c3aed" stroke-width="2.5" stroke-linecap="round"></line></svg>""",
    "rectangle": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2" stroke-dasharray="4 4"></rect></svg>""",
    "free-form": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 2.5 2.5 0 0 1-.5-4.48 2.5 2.5 0 0 1 1.4-4.5 2.5 2.5 0 0 1 4.52-5.88z" stroke-dasharray="4 4"></path></svg>""",
    "window": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>""",
    "fullscreen": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path></svg>""",
    "delay": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>""",
    "pen": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19l7-7 3 3-7 7-3-3z"></path><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"></path><path d="M2 2l7.586 7.586"></path><circle cx="11" cy="11" r="2"></circle></svg>""",
    "highlighter": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-highlighter-icon lucide-highlighter"><path d="m9 11-6 6v3h9l3-3"/><path d="m22 12-4.6 4.6a2 2 0 0 1-2.8 0l-5.2-5.2a2 2 0 0 1 0-2.8L14 4"/></svg>""",
    "undo": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7v6h6"></path><path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"></path></svg>""",
    "redo": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 7v6h-6"></path><path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3l3 2.7"></path></svg>""",
    "save": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>""",
    "copy": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>""",
    "camera": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg>""",
    "video": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg>"""
}

def create_svg_icon(name, color):
    svg_data = SVG_ICONS[name].format(color=color)
    renderer = QSvgRenderer(QByteArray(svg_data.encode('utf-8')))
    pixmap = QPixmap(renderer.defaultSize())
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter()
    painter.begin(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

def is_dark_mode():
    if platform.system() == "Windows":
        try:
            reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except Exception:
            return False
    return False

class AnnotationScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_path_item = None
        self.current_shape_item = None
        self.current_path = None  
        self.items_drawn = [] 
        self.items_undone = []  
        self.base_pixmap = None
        
        self.pen_state = {"color": QColor(255, 0, 0), "width": 60}
        self.highlighter_state = {"color": QColor(255, 255, 0), "width": 140}
        
        self.current_tool = "pen" 
        self.update_pen()

    def update_pen(self):
        if self.current_tool == "pen":
            self.current_pen = QPen(self.pen_state["color"], self.pen_state["width"], Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        elif self.current_tool == "highlighter":
            c = QColor(self.highlighter_state["color"])
            c.setAlpha(100)
            self.current_pen = QPen(c, self.highlighter_state["width"], Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.MiterJoin)
        elif self.current_tool == "blur":
            self.current_pen = QPen(QColor(100, 100, 100, 150), 2, Qt.PenStyle.DashLine)

    def set_color(self, color):
        if self.current_tool == "pen": self.pen_state["color"] = color
        elif self.current_tool == "highlighter": self.highlighter_state["color"] = color
        self.update_pen()

    def set_size(self, size):
        if self.current_tool == "pen": self.pen_state["width"] = size
        elif self.current_tool == "highlighter": self.highlighter_state["width"] = size
        self.update_pen()

    def set_base_pixmap(self, pixmap):
        self.base_pixmap = pixmap

    def set_tool(self, tool_name):
        self.current_tool = tool_name
        self.update_pen()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            event.accept()
            return

        if self.current_tool == "text_select":
            super().mousePressEvent(event) 
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.items_undone.clear()  
            self.start_pos = event.scenePos()
            
            if self.current_tool in ["pen", "highlighter"]:
                self.current_path = QPainterPath(self.start_pos)
                self.current_path_item = self.addPath(self.current_path, self.current_pen)
                self.items_drawn.append(self.current_path_item)
            elif self.current_tool in ["rectangle", "blur"]:
                from PyQt6.QtCore import QRectF
                self.current_shape_item = self.addRect(QRectF(self.start_pos, self.start_pos), self.current_pen)
                if self.current_tool == "rectangle":
                    self.items_drawn.append(self.current_shape_item)
                    
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.current_tool == "text_select":
            super().mouseMoveEvent(event)
            return
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.current_tool in ["pen", "highlighter"] and self.current_path_item:
                self.current_path.lineTo(event.scenePos())
                self.current_path_item.setPath(self.current_path)
            elif self.current_tool in ["rectangle", "blur"] and self.current_shape_item:
                from PyQt6.QtCore import QRectF
                rect = QRectF(self.start_pos, event.scenePos()).normalized()
                self.current_shape_item.setRect(rect)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.current_tool == "text_select":
            super().mouseReleaseEvent(event)
            return
        if event.button() == Qt.MouseButton.LeftButton:
            if self.current_tool == "blur" and self.current_shape_item:
                rect = self.current_shape_item.rect().toRect()
                self.removeItem(self.current_shape_item)
                self.current_shape_item = None
                
                if rect.width() > 0 and rect.height() > 0 and self.base_pixmap:
                    captured_region = self.base_pixmap.copy(rect)
                    scaled_down = captured_region.scaled(max(1, rect.width() // 10), max(1, rect.height() // 10), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)
                    pixelated = scaled_down.scaled(rect.width(), rect.height(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)
                    
                    from PyQt6.QtWidgets import QGraphicsPixmapItem
                    blur_item = QGraphicsPixmapItem(pixelated)
                    blur_item.setPos(float(rect.x()), float(rect.y()))
                    self.addItem(blur_item)
                    self.items_drawn.append(blur_item)
            self.current_path_item = None
            self.current_path = None
            self.current_shape_item = None
        super().mouseReleaseEvent(event)

    def undo(self):
        if self.items_drawn:
            item = self.items_drawn.pop()
            self.removeItem(item)
            self.items_undone.append(item)  

    def redo(self):
        if self.items_undone:
            item = self.items_undone.pop()
            self.addItem(item)
            self.items_drawn.append(item)  

class ShimmerOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.is_animating = False
        self.hide()

    def start(self):
        self.show()
        self.angle = 0
        self.is_animating = True
        self.timer.start(16)

    def stop(self):
        self.hide()
        self.is_animating = False
        self.timer.stop()

    def animate(self):
        if self.parent() and self.size() != self.parent().size():
            self.resize(self.parent().size())
            
        self.angle = (self.angle + 5) % 360
        self.update()

    def paintEvent(self, event):
        if not self.is_animating: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        view = self.parent()
        if hasattr(view, 'scene') and view.scene() and not view.scene().sceneRect().isEmpty():
            mapped_poly = view.mapFromScene(view.scene().sceneRect())
            target_rect = mapped_poly.boundingRect()
        else:
            target_rect = self.rect()
        
        painter.fillRect(target_rect, QColor(0, 0, 0, 40)) 
        
        from PyQt6.QtGui import QConicalGradient
        rect = target_rect.adjusted(2, 2, -2, -2)
        
        accent = QColor(0, 120, 212)
        transparent = QColor(0, 120, 212, 0)
        
        center = target_rect.center().toPointF()
        gradient = QConicalGradient(center, float(self.angle))
        gradient.setColorAt(0.0, accent)
        gradient.setColorAt(0.15, transparent)
        gradient.setColorAt(0.85, transparent)
        gradient.setColorAt(1.0, accent)
        
        pen = QPen(gradient, 4)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        painter.drawRect(rect)

class OCRWorker(QThread):
    result_ready = pyqtSignal(list) # Changed from str to list
    error_occurred = pyqtSignal(str)

    def __init__(self, byte_array):
        super().__init__()
        self.byte_array = byte_array

    def run(self):
        try:
            import pytesseract
            from pytesseract import Output
            from PIL import Image
            import io
            import os
            
            tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            else:
                self.error_occurred.emit("Tesseract not found at C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
                return
            
            pil_img = Image.open(io.BytesIO(self.byte_array.data()))
            # Get data with bounding boxes
            data = pytesseract.image_to_data(pil_img, output_type=Output.DICT)
            
            results = []
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if text: # Ignore empty strings
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    results.append({"text": text, "rect": (x, y, w, h)})
                    
            self.result_ready.emit(results)
        except Exception as e:
            self.error_occurred.emit(str(e))

class GlobalHotkeyThread(QThread):
    trigger_snip = pyqtSignal()
    def run(self):
        keyboard.add_hotkey('ctrl+shift+s', self.emit_trigger)
        keyboard.wait()
    def emit_trigger(self):
        self.trigger_snip.emit()

class FloatingSnipToolbar(QWidget):
    mode_selected = pyqtSignal(str)
    cancelled = pyqtSignal()

    def __init__(self, dark_mode=False, initial_mode="Rectangle"):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.icon_color = "#ffffff" if dark_mode else "#000000"
        self.bg_color = "#2b2b2b" if dark_mode else "#ffffff"
        self.border_color = "#4a4a4a" if dark_mode else "#d0d0d0"
        self.hover_color = "#414141" if dark_mode else "#f0f0f0"
        self.active_color = "#0078d4" 

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {self.bg_color};
                border: 1px solid {self.border_color};
                border-radius: 8px;
            }}
        """)
        
        c_layout = QHBoxLayout(container)
        c_layout.setContentsMargins(8, 6, 8, 6)
        c_layout.setSpacing(6)

        self.rect_btn = self.create_btn("rectangle", "Rectangle Snip", "Rectangle")
        self.free_btn = self.create_btn("free-form", "Freeform Snip", "Free-form")
        self.win_btn = self.create_btn("window", "Window Snip", "Window")
        self.full_btn = self.create_btn("fullscreen", "Fullscreen Snip", "Fullscreen")
        
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"background-color: {self.border_color};")
        
        self.close_btn = QPushButton()
        self.close_btn.setIcon(create_svg_icon("close", self.icon_color))
        self.close_btn.setToolTip("Cancel")
        self.close_btn.setFixedSize(36, 36)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; border-radius: 4px; color: {self.icon_color}; font-weight: bold; font-size: 16px;}}
            QPushButton:hover {{ background: #E81123; color: white; }}
        """)
        self.close_btn.clicked.connect(self.cancelled.emit)

        self.buttons = [self.rect_btn, self.free_btn, self.win_btn, self.full_btn]
        
        c_layout.addWidget(self.rect_btn)
        c_layout.addWidget(self.free_btn)
        c_layout.addWidget(self.win_btn)
        c_layout.addWidget(self.full_btn)
        c_layout.addWidget(sep)
        c_layout.addWidget(self.close_btn)

        layout.addWidget(container)

        self.adjustSize()
        screen_geom = QApplication.primaryScreen().geometry()
        self.move(screen_geom.width() // 2 - self.width() // 2, 20)
        
        self.set_active_button(initial_mode)

    def create_btn(self, icon_name, tooltip, mode_name):
        btn = QPushButton()
        btn.setIcon(create_svg_icon(icon_name, self.icon_color))
        btn.setToolTip(tooltip)
        btn.setFixedSize(36, 36)
        btn.setProperty("mode", mode_name)
        btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; border: none; border-radius: 4px; border-bottom: 3px solid transparent;}}
            QPushButton:hover {{ background: {self.hover_color}; }}
        """)
        btn.clicked.connect(lambda: self.handle_mode_click(btn))
        return btn

    def handle_mode_click(self, btn):
        mode = btn.property("mode")
        self.set_active_button(mode)
        self.mode_selected.emit(mode)
        
    def set_active_button(self, mode):
        for btn in self.buttons:
            if btn.property("mode") == mode:
                btn.setStyleSheet(f"""
                    QPushButton {{ background: {self.hover_color}; border: none; border-radius: 4px; border-bottom: 3px solid {self.active_color};}}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{ background: transparent; border: none; border-radius: 4px; border-bottom: 3px solid transparent;}}
                    QPushButton:hover {{ background: {self.hover_color}; }}
                """)

import cv2
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QSlider, QGraphicsDropShadowEffect,
                             QFileDialog, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class VideoPreviewDialog(QMainWindow):
    def __init__(self, video_path, dark_mode=False, parent=None):
        super().__init__(parent=parent)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle("Snipping Tool - Video Preview")
        self.resize(1000, 600)
        
        self.video_path = video_path
        self.dark_mode = dark_mode
        self.icon_color = "#ffffff" if dark_mode else "#000000"
        self.is_playing = True
        self.was_playing_before_scrub = False

        import pywinstyles
        pywinstyles.apply_style(self, "mica")
        header_color = "#1f1f1f" if dark_mode else "#f3f3f3"
        pywinstyles.change_header_color(self, header_color)
        if dark_mode:
            pywinstyles.apply_style(self, "dark")
        
        self.central_widget = QWidget()
        self.central_widget.setObjectName("dialogContainer")
        self.setCentralWidget(self.central_widget)
        
        self.cap = cv2.VideoCapture(self.video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 20.0
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        self.setup_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(int(1000 / self.fps))

    def setup_ui(self):
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.player_container = QWidget()
        self.player_container.setStyleSheet("background-color: transparent;")
        p_layout = QVBoxLayout(self.player_container)
        p_layout.setContentsMargins(40, 40, 40, 20)

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        from PyQt6.QtWidgets import QSizePolicy
        self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_label.setMinimumSize(100, 100)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 4)
        self.video_label.setGraphicsEffect(shadow)
        
        p_layout.addWidget(self.video_label)
        main_layout.addWidget(self.player_container, 1)

        control_bar = QWidget()
        control_bar.setFixedHeight(65)
        c_layout = QHBoxLayout(control_bar)
        c_layout.setContentsMargins(20, 0, 20, 15)
        c_layout.setSpacing(15)

        btn_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {"#383838" if self.dark_mode else "#e0e0e0"};
            }}
        """

        self.play_btn = QPushButton()
        self.play_btn.setIcon(create_svg_icon("pause", self.icon_color))
        self.play_btn.setFixedSize(40, 40)
        self.play_btn.setStyleSheet(btn_style)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.clicked.connect(self.toggle_playback)
        self.play_btn.setToolTip("Play/Pause")

        time_color = "#ffffff" if self.dark_mode else "#000000"
        
        self.current_time_lbl = QLabel("00:00")
        self.current_time_lbl.setStyleSheet(f"color: {time_color};")
        self.current_time_lbl.setMinimumWidth(45)
        self.current_time_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.total_time_lbl = QLabel(self.format_time(self.total_frames / self.fps if self.fps else 0))
        self.total_time_lbl.setStyleSheet(f"color: {time_color};")
        self.total_time_lbl.setMinimumWidth(45)
        self.total_time_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, max(0, self.total_frames - 1))
        self.slider.setCursor(Qt.CursorShape.PointingHandCursor)
        
        slider_track = "#444444" if self.dark_mode else "#cccccc"
        self.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border-radius: 2px;
                height: 4px;
                background: {slider_track};
            }}
            QSlider::handle:horizontal {{
                background: #7800d4;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }}
            QSlider::sub-page:horizontal {{
                background: #7800d4;
                border-radius: 2px;
            }}
        """)
        
        self.slider.sliderPressed.connect(self.on_slider_pressed)
        self.slider.sliderMoved.connect(self.on_slider_moved)
        self.slider.sliderReleased.connect(self.on_slider_released)

        self.save_btn = QPushButton()
        self.save_btn.setIcon(create_svg_icon("save", self.icon_color))
        self.save_btn.setFixedSize(40, 40)
        self.save_btn.setStyleSheet(btn_style)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_video)
        self.save_btn.setToolTip("Save Video")

        c_layout.addWidget(self.play_btn)
        c_layout.addWidget(self.current_time_lbl)
        c_layout.addWidget(self.slider, 1)
        c_layout.addWidget(self.total_time_lbl)
        c_layout.addWidget(self.save_btn)

        main_layout.addWidget(control_bar)

    def format_time(self, seconds):
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02d}:{s:02d}"

    def update_frame(self):
        if not self.is_playing:
            return
            
        current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        
        if current_frame >= self.total_frames - 1:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            current_frame = 0
            
        self.read_and_display()
        
        self.slider.blockSignals(True)
        self.slider.setValue(current_frame)
        self.slider.blockSignals(False)
        self.current_time_lbl.setText(self.format_time(current_frame / self.fps if self.fps else 0))

    def read_and_display(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            
            self.video_label.setPixmap(pixmap.scaled(
                self.video_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))

    def toggle_playback(self):
        self.is_playing = not self.is_playing
        icon_name = "pause" if self.is_playing else "play"
        self.play_btn.setIcon(create_svg_icon(icon_name, self.icon_color))

    def on_slider_pressed(self):
        self.was_playing_before_scrub = self.is_playing
        if self.is_playing:
            self.toggle_playback()

    def on_slider_moved(self, position):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
        self.read_and_display()
        self.current_time_lbl.setText(self.format_time(position / self.fps if self.fps else 0))

    def on_slider_released(self):
        if self.was_playing_before_scrub:
            self.toggle_playback()

    def save_video(self):
        import shutil
        path, _ = QFileDialog.getSaveFileName(self, "Save Video", "", "MP4 Files (*.mp4)")
        if path:
            self.is_playing = False
            self.timer.stop()
            self.cap.release()
            shutil.copy(self.video_path, path)
            self.close()

    def closeEvent(self, event):
        self.timer.stop()
        self.cap.release()
        super().closeEvent(event)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.is_playing:
            current = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, current - 1))
            self.read_and_display()

class CaptureToggle(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, dark_mode=False, parent=None):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.is_video = False
        self.icon_color = "#ffffff" if dark_mode else "#000000"
        
        self.bg_color = "#323232" if dark_mode else "#e6e6e6"
        self.thumb_color = "#4a4a4a" if dark_mode else "#ffffff"
        thumb_border = "none" if dark_mode else "1px solid #d0d0d0"

        self.setFixedSize(96, 36)
        self.setStyleSheet(f"background-color: {self.bg_color}; border-radius: 18px;")

        self.thumb = QWidget(self)
        self.thumb.setFixedSize(44, 32)
        self.thumb.setStyleSheet(f"background-color: {self.thumb_color}; border-radius: 16px; border: {thumb_border};")
        self.thumb.move(2, 2)

        self.photo_btn = QPushButton(self)
        self.photo_btn.setIcon(create_svg_icon("camera", self.icon_color))
        self.photo_btn.setFixedSize(44, 32)
        self.photo_btn.move(2, 2)
        self.photo_btn.setStyleSheet("background: transparent; border: none;")
        self.photo_btn.setToolTip("Snip (Photo)")
        self.photo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.photo_btn.clicked.connect(lambda: self.set_state(False))

        self.video_btn = QPushButton(self)
        self.video_btn.setIcon(create_svg_icon("video", self.icon_color))
        self.video_btn.setFixedSize(44, 32)
        self.video_btn.move(50, 2)
        self.video_btn.setStyleSheet("background: transparent; border: none;")
        self.video_btn.setToolTip("Record (Video)")
        self.video_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.video_btn.clicked.connect(lambda: self.set_state(True))

        self.animation = QPropertyAnimation(self.thumb, b"pos")
        self.animation.setEasingCurve(QEasingCurve.Type.OutBack) 
        self.animation.setDuration(250)

    def set_state(self, is_video):
        if self.is_video == is_video:
            return
        self.is_video = is_video
        
        end_pos = QPoint(50, 2) if is_video else QPoint(2, 2)
        
        self.animation.stop()
        self.animation.setEndValue(end_pos)
        self.animation.start()
        
        self.toggled.emit(self.is_video)

class AnimatedNewButton(QPushButton):
    def __init__(self, icon, text, text_color, parent=None):
        super().__init__(parent)
        self.custom_icon = icon
        self.custom_text = text
        self.text_color = text_color
        self.setFixedHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("newButton") 
        
        self.anim_value = 0.0
        self.animation = QVariantAnimation(self)
        self.animation.setDuration(450)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuart) 
        self.animation.valueChanged.connect(self.set_anim_value)

    def set_anim_value(self, val):
        self.anim_value = val
        self.update()

    def enterEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.anim_value)
        self.animation.setEndValue(1.0)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.stop()
        self.animation.setStartValue(self.anim_value)
        self.animation.setEndValue(0.0)
        self.animation.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event) 
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setClipRect(self.rect()) 
        
        font = self.font()
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(self.text_color)) 
        fm = painter.fontMetrics()
        
        icon_size = 18
        spacing = 8
        
        total_width = icon_size + spacing + fm.horizontalAdvance(self.custom_text)
        start_x = (self.width() - total_width) // 2
        
        icon_y = (self.height() - icon_size) // 2
        pixmap = self.custom_icon.pixmap(icon_size, icon_size)
        painter.drawPixmap(int(start_x), int(icon_y), pixmap)
        
        current_x = start_x + icon_size + spacing
        text_y = (self.height() + fm.ascent() - fm.descent()) // 2
        
        elements = list(self.custom_text)
        num_elements = len(elements)
        stagger_range = 0.5 
        stagger_step = stagger_range / max(1, (num_elements - 1)) if num_elements > 1 else 0
        
        for i, char in enumerate(elements):
            start_t = i * stagger_step
            end_t = start_t + (1.0 - stagger_range)
            
            if self.anim_value < start_t: local_val = 0.0
            elif self.anim_value > end_t: local_val = 1.0
            else: local_val = (self.anim_value - start_t) / (end_t - start_t)
            
            offset_y = -local_val * self.height()
            
            char_w = fm.horizontalAdvance(char)
            painter.drawText(int(current_x), int(text_y + offset_y), char)
            painter.drawText(int(current_x), int(text_y + offset_y + self.height()), char)
            current_x += char_w

class SelectableTextItem(QGraphicsRectItem):
    def __init__(self, text, rect):
        super().__init__(QRectF(*rect))
        self.text_content = text
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        
        self.setPen(QPen(Qt.PenStyle.NoPen))
        
    def paint(self, painter, option, widget=None):
        if self.isSelected():
            painter.fillRect(self.rect(), QColor(0, 120, 212, 120)) 
        elif self.isUnderMouse():
            painter.fillRect(self.rect(), QColor(255, 255, 255, 120)) 
        else:
            painter.fillRect(self.rect(), QColor(255, 255, 255, 40))

from PyQt6.QtGui import QNativeGestureEvent

class ZoomableView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            zoom_in_factor = 1.15
            zoom_out_factor = 1.0 / zoom_in_factor
            zoom_factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor
            
            self.scale(zoom_factor, zoom_factor)
            event.accept()
            
            if hasattr(self.window(), 'update_canvas_cursor'):
                self.window().update_canvas_cursor()
        else:
            super().wheelEvent(event)

    def viewportEvent(self, event):
        if isinstance(event, QNativeGestureEvent):
            if event.gestureType() == Qt.NativeGestureType.ZoomNativeGesture:
                multiplier = event.value() + 1.0
                if multiplier > 0:
                    self.scale(multiplier, multiplier)
                    if hasattr(self.window(), 'update_canvas_cursor'):
                        self.window().update_canvas_cursor()
                return True
        return super().viewportEvent(event)

from PyQt6.QtWidgets import QSlider, QGridLayout

class BrushFlyout(QWidget):
    def __init__(self, tool_name, current_color, current_size, dark_mode, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.tool_name = tool_name
        self.dark_mode = dark_mode
        self.parent_gui = parent
        
        self.container = QFrame(self)
        self.container.setObjectName("flyoutContainer")
        
        bg_color = "rgba(40, 40, 40, 200)" if dark_mode else "rgba(240, 240, 240, 200)"
        border_color = "#555555" if dark_mode else "#cccccc"
        text_color = "#ffffff" if dark_mode else "#000000"
        
        self.container.setStyleSheet(f"""
            #flyoutContainer {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 10px;
            }}
            QLabel {{ color: {text_color}; font-weight: 600; }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.container)
        
        c_layout = QVBoxLayout(self.container)
        c_layout.setContentsMargins(15, 15, 15, 15)
        c_layout.setSpacing(15)
        
        c_layout.addWidget(QLabel("Size"))
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(1, 200) if tool_name == "pen" else self.slider.setRange(10, 400)
        self.slider.setValue(current_size)
        self.slider.setCursor(Qt.CursorShape.PointingHandCursor)
        
        slider_track = "#444444" if dark_mode else "#cccccc"
        self.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{ border-radius: 2px; height: 4px; background: {slider_track}; }}
            QSlider::handle:horizontal {{ background: #0078d4; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; }}
            QSlider::sub-page:horizontal {{ background: #0078d4; border-radius: 2px; }}
        """)
        self.slider.valueChanged.connect(self.on_size_changed)
        c_layout.addWidget(self.slider)
        
        c_layout.addWidget(QLabel("Colors"))
        grid = QGridLayout()
        grid.setSpacing(10)
        
        colors = [
            "#000000", "#ffffff", "#ff4343", "#ff9800", "#ffeb3b", "#4caf50", 
            "#2196f3", "#9c27b0", "#00bcd4", "#e91e63", "#795548", "#9e9e9e"
        ]
        
        row, col = 0, 0
        for hex_color in colors:
            btn = QPushButton()
            btn.setFixedSize(26, 26)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            border = "2px solid #0078d4" if QColor(hex_color).name() == current_color.name() else "1px solid rgba(150, 150, 150, 0.5)"
            btn.setStyleSheet(f"""
                QPushButton {{ background-color: {hex_color}; border-radius: 13px; border: {border}; }}
                QPushButton:hover {{ border: 2px solid #888888; }}
            """)
            btn.clicked.connect(lambda checked, c=hex_color: self.on_color_clicked(c))
            
            grid.addWidget(btn, row, col)
            col += 1
            if col > 5:
                col = 0
                row += 1
                
        c_layout.addLayout(grid)
        
        import pywinstyles
        try:
            pywinstyles.apply_style(self, "mica")
            if dark_mode: pywinstyles.apply_style(self, "dark")
        except: pass

    def on_size_changed(self, val):
        if self.parent_gui: 
            self.parent_gui.scene.set_size(val)
            self.parent_gui.update_canvas_cursor()
            
    def on_color_clicked(self, hex_color):
        if self.parent_gui:
            self.parent_gui.scene.set_color(QColor(hex_color))
            self.parent_gui.update_tool_button_styles()
            self.parent_gui.update_canvas_cursor()
        self.close() 

class SnippingToolGUI(QMainWindow):
    def __init__(self, dark_mode=False):
        super().__init__()
        self.dark_mode = dark_mode
        self.icon_color = "#ffffff" if dark_mode else "#000000"

        self.setWindowTitle("Snipping Tool")
        self.resize(590, 300)
        self.setMinimumSize(520, 300)

        pywinstyles.apply_style(self, "mica")
        header_color = "#1f1f1f" if dark_mode else "#f3f3f3"
        pywinstyles.change_header_color(self, header_color)
        if dark_mode: pywinstyles.apply_style(self, "dark")

        self.snip_modes = ["Rectangle", "Free-form", "Window", "Fullscreen"]
        self.delays = ["No delay", "3 seconds", "5 seconds", "10 seconds"]
        self.current_mode = self.snip_modes[0]
        self.current_delay_sec = 0
        
        self.current_overlay = None
        self.snip_toolbar = None
        
        self.central_widget = QWidget()
        self.central_widget.setObjectName("mainContainer")
        self.setCentralWidget(self.central_widget)
        
        self.setup_ui()

        self.copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.copy_shortcut.activated.connect(self.copy_to_clipboard)
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_image)

        self.hotkey_thread = GlobalHotkeyThread()
        self.hotkey_thread.trigger_snip.connect(self.start_snip)
        self.hotkey_thread.start()

    def set_editing_tools_enabled(self, enabled):
        if enabled:
            self.bottom_toolbar.show()
            self.h_div_bottom.show()
            self.ocr_btn.show()
            self.copy_btn.show()
            self.save_btn.show()
        else:
            self.bottom_toolbar.hide()
            self.h_div_bottom.hide()
            self.ocr_btn.hide()
            self.copy_btn.hide()
            self.save_btn.hide()

    def update_canvas_cursor(self):
        tool = getattr(self.scene, 'current_tool', 'pen')
        
        if tool in ["pen", "highlighter"]:
            if tool == "pen":
                size = self.scene.pen_state["width"]
                color = self.scene.pen_state["color"]
                alpha = 255
                is_rect = False
            else:
                size = self.scene.highlighter_state["width"]
                color = self.scene.highlighter_state["color"]
                alpha = 100
                is_rect = True

            zoom_factor = self.view.transform().m11() if hasattr(self, 'view') else 1.0
            display_size = max(4, int(size * zoom_factor)) 
            
            from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QCursor
            from PyQt6.QtCore import Qt, QPointF, QRectF
            
            pixmap_size = display_size + 4
            pixmap = QPixmap(pixmap_size, pixmap_size)
            pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            c = QColor(color)
            c.setAlpha(alpha)
            painter.setBrush(c)

            border_color = QColor(0, 0, 0, 150) if c.lightness() > 128 else QColor(255, 255, 255, 150)
            painter.setPen(QPen(border_color, 1))

            center = pixmap_size / 2.0
            
            if is_rect:
                rect_x = center - (display_size / 2.0)
                rect_y = center - (display_size / 2.0)
                painter.drawRect(QRectF(rect_x, rect_y, display_size, display_size))
            else:
                painter.drawEllipse(QPointF(center, center), display_size / 2.0, display_size / 2.0)
                
            painter.end()

            self.view.viewport().setCursor(QCursor(pixmap, int(center), int(center)))
        elif tool == "text_select":
            self.view.viewport().setCursor(Qt.CursorShape.IBeamCursor)
        else:
            self.view.viewport().setCursor(Qt.CursorShape.CrossCursor)
    
    def update_tool_button_styles(self):
        pen_color = self.scene.pen_state["color"].name()
        hl_color = self.scene.highlighter_state["color"].name()
        
        def get_style(active_color):
            return f"""
                QPushButton {{ background: transparent; border: none; border-radius: 6px; padding: 10px; }}
                QPushButton:hover {{ background-color: {"#383838" if self.dark_mode else "#e0e0e0"}; }}
                QPushButton:checked {{ background-color: {"#4a4a4a" if self.dark_mode else "#d0d0d0"}; border-bottom: 3px solid {active_color}; }}
                QPushButton:disabled {{ opacity: 0.5; }}
            """
        
        self.pen_btn.setStyleSheet(get_style(pen_color))
        self.highlight_btn.setStyleSheet(get_style(hl_color))
        self.rect_btn.setStyleSheet(get_style("transparent"))
        self.blur_btn.setStyleSheet(get_style("transparent"))

    def setup_ui(self):
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        action_btn_style = f"""
            QPushButton {{ background: transparent; border: none; border-radius: 6px; padding: 10px; }}
            QPushButton:hover {{ background-color: {"#383838" if self.dark_mode else "#e0e0e0"}; }}
            QPushButton:disabled {{ opacity: 0.5; }}
        """
        
        self.top_toolbar = QWidget()
        self.top_toolbar.setFixedHeight(55)
        t_layout = QHBoxLayout(self.top_toolbar)
        t_layout.setContentsMargins(15, 0, 15, 0)
        t_layout.setSpacing(5)

        icon = create_svg_icon("plus", self.icon_color)
        self.new_btn = AnimatedNewButton(icon, "New", self.icon_color)
        self.new_btn.setMinimumWidth(90)
        self.new_btn.setToolTip("Start new capture")
        self.new_btn.clicked.connect(self.start_snip)
        
        self.is_video_mode = False
        self.capture_toggle = CaptureToggle(self.dark_mode)
        self.capture_toggle.toggled.connect(self.set_capture_mode)

        self.mode_btn = QPushButton()
        self.mode_btn.setObjectName("toolbarButton")
        self.mode_btn.setFixedHeight(36)
        self.mode_btn.clicked.connect(self.show_mode_menu)
        self.mode_btn.setToolTip("Snipping Mode")
        self.update_mode_button()
        
        self.delay_btn = QPushButton()
        self.delay_btn.setObjectName("toolbarButton")
        self.delay_btn.setFixedHeight(36)
        self.delay_btn.clicked.connect(self.show_delay_menu)
        self.delay_btn.setToolTip("Capture Delay")
        self.update_delay_button()

        self.top_sep = QFrame()
        self.top_sep.setFixedWidth(1)
        sep_color = "rgba(255, 255, 255, 0.1)" if self.dark_mode else "rgba(0, 0, 0, 0.1)"
        self.top_sep.setStyleSheet(f"background-color: {sep_color}; margin: 12px 4px;")

        t_layout.addWidget(self.new_btn)
        t_layout.addSpacing(10)
        t_layout.addWidget(self.capture_toggle)
        t_layout.addWidget(self.top_sep)
        t_layout.addWidget(self.mode_btn)
        t_layout.addSpacing(-13)
        t_layout.addWidget(self.delay_btn)
        t_layout.addStretch(0)

        self.ocr_btn = QPushButton()
        self.ocr_btn.setIcon(create_svg_icon("text", self.icon_color))
        self.ocr_btn.setStyleSheet(action_btn_style)
        self.ocr_btn.clicked.connect(self.extract_text)
        self.ocr_btn.setCheckable(True)
        self.ocr_btn.setToolTip("Text Actions (OCR)")
        self.ocr_btn.hide()

        self.copy_btn = QPushButton()
        self.copy_btn.setIcon(create_svg_icon("copy", self.icon_color))
        self.copy_btn.setStyleSheet(action_btn_style)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setToolTip("Copy to Clipboard")
        self.copy_btn.hide()

        self.save_btn = QPushButton()
        self.save_btn.setIcon(create_svg_icon("save", self.icon_color))
        self.save_btn.setStyleSheet(action_btn_style)
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setToolTip("Save Image")
        self.save_btn.hide()

        t_layout.addWidget(self.ocr_btn)
        t_layout.addWidget(self.copy_btn)
        t_layout.addWidget(self.save_btn)
        
        main_layout.addWidget(self.top_toolbar)
        
        h_div_top = QFrame()
        h_div_top.setFixedHeight(1)
        h_div_top.setStyleSheet(f"background-color: {'#3a3a3a' if self.dark_mode else '#e0e0e0'}; border: none;")
        main_layout.addWidget(h_div_top)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)

        self.placeholder_page = QWidget()
        p_layout = QVBoxLayout(self.placeholder_page)
        p_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.placeholder_frame = QFrame()
        self.placeholder_frame.setObjectName("placeholderFrame")
        self.placeholder_frame.setFixedSize(500, 150)
        pf_layout = QVBoxLayout(self.placeholder_frame)
        pf_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        placeholder_label = QLabel("Snip and share")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setObjectName("placeholderLabel")
        placeholder_label.setFont(QFont("Segoe UI Variable", 16))
        pf_layout.addWidget(placeholder_label)
        
        instruction_label = QLabel("Press + New to start snipping")
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label.setStyleSheet("color: #a0a0a0; margin-top: 10px;")
        pf_layout.addWidget(instruction_label)

        p_layout.addWidget(self.placeholder_frame)
        self.stacked_widget.addWidget(self.placeholder_page)

        self.canvas_page = QWidget()
        self.canvas_page.setObjectName("canvasPage")
        canvas_bg = "#191919" if self.dark_mode else "#e6e6e6"
        self.canvas_page.setStyleSheet(f"#canvasPage {{ background-color: {canvas_bg}; }}")
        
        c_layout = QVBoxLayout(self.canvas_page)
        c_layout.setContentsMargins(40, 40, 40, 40)
        
        self.scene = AnnotationScene(self)
        self.view = ZoomableView(self.scene) 
        self.view.setStyleSheet("background: transparent; border: none;")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.show_view_context_menu)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 4)
        self.view.setGraphicsEffect(shadow)
        c_layout.addWidget(self.view)
        
        self.stacked_widget.addWidget(self.canvas_page)

        self.h_div_bottom = QFrame()
        self.h_div_bottom.setFixedHeight(1)
        self.h_div_bottom.setStyleSheet(f"background-color: {'#3a3a3a' if self.dark_mode else '#e0e0e0'}; border: none;")
        main_layout.addWidget(self.h_div_bottom)

        self.bottom_toolbar = QWidget()
        self.bottom_toolbar.setFixedHeight(55)
        b_layout = QHBoxLayout(self.bottom_toolbar)
        b_layout.setContentsMargins(15, 0, 15, 0)
        b_layout.setSpacing(5)

        self.pen_btn = QPushButton()
        self.pen_btn.setIcon(create_svg_icon("pen", self.icon_color))
        self.pen_btn.setCheckable(True)
        self.pen_btn.setChecked(True)
        self.pen_btn.setStyleSheet(action_btn_style)
        self.pen_btn.clicked.connect(lambda: self.switch_tool("pen"))
        self.pen_btn.setToolTip("Pen")

        self.highlight_btn = QPushButton()
        self.highlight_btn.setIcon(create_svg_icon("highlighter", self.icon_color))
        self.highlight_btn.setCheckable(True)
        self.highlight_btn.setStyleSheet(action_btn_style)
        self.highlight_btn.clicked.connect(lambda: self.switch_tool("highlighter"))
        self.highlight_btn.setToolTip("Highlighter")

        self.rect_btn = QPushButton()
        self.rect_btn.setIcon(create_svg_icon("rect_tool", self.icon_color))
        self.rect_btn.setCheckable(True)
        self.rect_btn.setStyleSheet(action_btn_style)
        self.rect_btn.clicked.connect(lambda: self.switch_tool("rectangle"))
        self.rect_btn.setToolTip("Rectangle Shape")

        self.blur_btn = QPushButton()
        self.blur_btn.setIcon(create_svg_icon("blur", self.icon_color))
        self.blur_btn.setCheckable(True)
        self.blur_btn.setStyleSheet(action_btn_style)
        self.blur_btn.clicked.connect(lambda: self.switch_tool("blur"))
        self.blur_btn.setToolTip("Blur/Pixelate Area")
        self.blur_btn.clicked.connect(lambda: self.switch_tool("blur"))
        self.blur_btn.setToolTip("Blur/Pixelate Area")
        
        self.update_tool_button_styles()

        self.b_sep_sep = QFrame()
        self.b_sep_sep.setFixedWidth(1)
        sep_color = "rgba(255, 255, 255, 0.1)" if self.dark_mode else "rgba(0, 0, 0, 0.1)"
        self.b_sep_sep.setStyleSheet(f"background-color: {sep_color}; margin: 12px 4px;")

        self.undo_btn = QPushButton()
        self.undo_btn.setIcon(create_svg_icon("undo", self.icon_color))
        self.undo_btn.setStyleSheet(action_btn_style)
        self.undo_btn.clicked.connect(self.undo_stroke)
        self.undo_btn.setToolTip("Undo Last Action")

        self.redo_btn = QPushButton()
        self.redo_btn.setIcon(create_svg_icon("redo", self.icon_color))
        self.redo_btn.setStyleSheet(action_btn_style)
        self.redo_btn.clicked.connect(self.redo_stroke)
        self.redo_btn.setToolTip("Redo Last Action")

        b_layout.addStretch(1)
        b_layout.addWidget(self.pen_btn)
        b_layout.addWidget(self.highlight_btn)
        b_layout.addWidget(self.rect_btn)
        b_layout.addWidget(self.blur_btn)
        b_layout.addSpacing(10)
        b_layout.addWidget(self.b_sep_sep)
        b_layout.addSpacing(10)
        b_layout.addWidget(self.undo_btn)
        b_layout.addWidget(self.redo_btn)
        b_layout.addStretch(1)

        main_layout.addWidget(self.bottom_toolbar)

        self.toast_label = QLabel(self)
        self.toast_label.setStyleSheet("""
            background-color: #303030; color: white; border-radius: 6px; 
            padding: 8px 16px; font-weight: 600; font-size: 14px;
        """)
        self.toast_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.toast_label.hide()
        
        self.shimmer = ShimmerOverlay(self.view)
        
        self.bottom_toolbar.hide()
        self.h_div_bottom.hide()

    def show_view_context_menu(self, pos):
        if getattr(self.scene, 'current_tool', None) == "text_select":
            selected_items = [item for item in self.scene.selectedItems() if isinstance(item, SelectableTextItem)]
            if selected_items:
                from PyQt6.QtWidgets import QMenu
                menu = QMenu(self)
                menu.setObjectName("contextMenu")
                
                copy_action = menu.addAction("Copy Selected Text")
                action = menu.exec(self.view.mapToGlobal(pos))
                
                if action == copy_action:
                    self.copy_to_clipboard()

    def set_capture_mode(self, is_video):
        self.is_video_mode = is_video
        
        if is_video:
            self.mode_btn.setEnabled(False)
            self.mode_btn.setText(" Record")
            self.mode_btn.setIcon(create_svg_icon("record", self.icon_color))
        else:
            self.mode_btn.setEnabled(True)
            self.update_mode_button()

    def update_mode_button(self):
        icon_name = self.current_mode.split(' ')[0].lower()
        self.mode_btn.setText(f" {self.current_mode}")
        self.mode_btn.setIcon(create_svg_icon(icon_name, self.icon_color))
        
    def update_delay_button(self):
        self.delay_btn.setText(f" {self.delays[self.get_delay_index()]}")
        self.delay_btn.setIcon(create_svg_icon("delay", self.icon_color))

    def show_mode_menu(self):
        menu = QMenu(self)
        menu.setObjectName("contextMenu")
        actions = { "Rectangle": "rectangle", "Free-form": "free-form", "Window": "window", "Fullscreen": "fullscreen" }
        for text, icon_name in actions.items():
            action = QAction(create_svg_icon(icon_name, self.icon_color), text, self)
            action.triggered.connect(lambda checked, t=text: self.set_mode(t))
            menu.addAction(action)
        menu.exec(self.mode_btn.mapToGlobal(self.mode_btn.rect().bottomLeft()))

    def show_delay_menu(self):
        menu = QMenu(self)
        menu.setObjectName("contextMenu")
        for i, text in enumerate(self.delays):
            action = QAction(text, self)
            action.triggered.connect(lambda checked, idx=i: self.set_delay(idx))
            menu.addAction(action)
        menu.exec(self.delay_btn.mapToGlobal(self.delay_btn.rect().bottomLeft()))

    def set_mode(self, mode):
        self.current_mode = mode
        self.update_mode_button()

    def set_delay(self, index):
        self.current_delay_sec = [0, 3, 5, 10][index]
        self.update_delay_button()

    def get_delay_index(self):
        return {0: 0, 3: 1, 5: 2, 10: 3}.get(self.current_delay_sec, 0)

    def switch_tool(self, tool_name):
        if tool_name != "text_select" and self.ocr_btn.isChecked():
            self.ocr_btn.setChecked(False)
            from PyQt6.QtWidgets import QGraphicsView
            self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
            if hasattr(self, 'text_items'):
                for item in self.text_items:
                    item.hide()
                    item.setSelected(False)
                    
        if self.scene.current_tool == tool_name and tool_name in ["pen", "highlighter"]:
            if tool_name == "pen":
                self.pen_btn.setChecked(True)
            elif tool_name == "highlighter":
                self.highlight_btn.setChecked(True)
                
            self.show_brush_flyout(tool_name)
            return

        self.pen_btn.setChecked(tool_name == "pen")
        self.highlight_btn.setChecked(tool_name == "highlighter")
        self.rect_btn.setChecked(tool_name == "rectangle")
        self.blur_btn.setChecked(tool_name == "blur")
        self.scene.set_tool(tool_name)
        self.update_tool_button_styles()
        self.update_canvas_cursor()

    def show_brush_flyout(self, tool_name):
        if tool_name == "pen":
            color = self.scene.pen_state["color"]
            size = self.scene.pen_state["width"]
            btn = self.pen_btn
        else:
            color = self.scene.highlighter_state["color"]
            size = self.scene.highlighter_state["width"]
            btn = self.highlight_btn
            
        self.flyout = BrushFlyout(tool_name, color, size, self.dark_mode, self)
        
        btn_pos = btn.mapToGlobal(QPoint(0, 0))
        self.flyout.adjustSize()
        x = btn_pos.x() - (self.flyout.width() // 2) + (btn.width() // 2)
        y = btn_pos.y() - self.flyout.height() - 10
        
        self.flyout.move(x, y)
        self.flyout.show()

    

    def choose_color(self):
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(self.scene.pen_color, self, "Choose Pen Color")
        if color.isValid():
            self.scene.set_color(color)
            self.update_tool_button_styles() 

    def undo_stroke(self): 
        self.scene.undo()

    def redo_stroke(self): 
        self.scene.redo()

    def extract_text(self):
        if self.ocr_btn.isChecked():
            if hasattr(self, 'text_items') and self.text_items:
                self.set_text_mode(True)
                return
                
            self.ocr_btn.setEnabled(False)
            self.shimmer.start()
            
            final_image = self.get_rendered_image()
            byte_array = QByteArray()
            from PyQt6.QtCore import QBuffer, QIODevice
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            final_image.save(buffer, "PNG")
            
            self.ocr_thread = OCRWorker(byte_array)
            self.ocr_thread.result_ready.connect(self.on_ocr_complete)
            self.ocr_thread.error_occurred.connect(self.on_ocr_error)
            self.ocr_thread.start()
        else:
            self.set_text_mode(False)

    def set_text_mode(self, enabled):
        from PyQt6.QtWidgets import QGraphicsView
        if enabled:
            self.scene.set_tool("text_select")
            self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.show_toast("Drag to select text")
            
            self.pen_btn.setChecked(False)
            self.highlight_btn.setChecked(False)
            self.rect_btn.setChecked(False)
            self.blur_btn.setChecked(False)
            
            if hasattr(self, 'text_items'):
                for item in self.text_items:
                    item.show()
        else:
            self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
            if hasattr(self, 'text_items'):
                for item in self.text_items:
                    item.hide()
                    item.setSelected(False)
            
            if self.scene.current_tool == "text_select":
                self.switch_tool("pen")

    def on_ocr_complete(self, text_data):
        self.shimmer.stop()
        self.ocr_btn.setEnabled(True)
        
        if not text_data:
            self.ocr_btn.setChecked(False)
            QMessageBox.information(self, "No Text Found", "Could not detect any text in the image.")
            return
            
        if hasattr(self, 'text_items'):
            for item in self.text_items:
                self.scene.removeItem(item)
                
        self.text_items = []
        for item in text_data:
            rect_item = SelectableTextItem(item['text'], item['rect'])
            self.scene.addItem(rect_item)
            self.text_items.append(rect_item)
            
        self.set_text_mode(True)

    def on_ocr_error(self, error_msg):
        self.shimmer.stop()
        self.ocr_btn.setEnabled(True)
        QMessageBox.warning(self, "OCR Error", error_msg)

    def get_rendered_image(self):
        pixmap = QPixmap(self.scene.sceneRect().size().toSize())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.scene.render(painter)
        painter.end()
        return pixmap

    def save_image(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", "", "PNG Files (*.png)")
        if path:
            self.get_rendered_image().save(path)

    def copy_to_clipboard(self):
        from PyQt6.QtWidgets import QGraphicsView
        if hasattr(self, 'text_items') and self.view.dragMode() == QGraphicsView.DragMode.RubberBandDrag:
            selected_items = [item for item in self.scene.selectedItems() if isinstance(item, SelectableTextItem)]
            
            if selected_items:
                selected_items.sort(key=lambda i: (round(i.rect().y() / 15), i.rect().x()))
                text = " ".join([i.text_content for i in selected_items])
                
                QApplication.clipboard().setText(text)
                self.show_toast("Selected text copied")
                return
                
        QApplication.clipboard().setPixmap(self.get_rendered_image())
        self.show_toast("Image copied to clipboard")

    def show_toast(self, message):
        self.toast_label.setText(message)
        self.toast_label.adjustSize()
        from PyQt6.QtCore import QPoint
        btn_pos = self.ocr_btn.mapTo(self, QPoint(0, 0))
        self.toast_label.move(btn_pos.x() - self.toast_label.width() - 15, btn_pos.y())
        self.toast_label.show()
        self.toast_label.raise_()
        QTimer.singleShot(2000, self.toast_label.hide)

    def start_snip(self):
        self.hide()
        QTimer.singleShot(200, self.launch_snip_environment)

    def launch_snip_environment(self):
        if self.is_video_mode:
            self.current_overlay = VideoSnipOverlay()
            self.current_overlay.recording_completed.connect(self.on_video_completed)
            return

        self.screen_pixmap = QApplication.primaryScreen().grabWindow(0)

        self.snip_toolbar = FloatingSnipToolbar(self.dark_mode, self.current_mode)
        self.snip_toolbar.mode_selected.connect(self.switch_snip_mode)
        self.snip_toolbar.cancelled.connect(self.cancel_snip)
        self.snip_toolbar.show()

        self.switch_snip_mode(self.current_mode)

    def switch_snip_mode(self, mode):
        self.current_mode = mode
        self.update_mode_button()

        if self.current_overlay:
            try:
                self.current_overlay.close()
                self.current_overlay.deleteLater()
            except RuntimeError:
                pass
            self.current_overlay = None

        if "Rectangle" in mode:
            self.current_overlay = RectangleSnipOverlay(self.screen_pixmap, self.current_delay_sec)
        elif "Free-form" in mode:
            self.current_overlay = FreeformSnipOverlay(self.screen_pixmap, self.current_delay_sec)
        elif "Window" in mode:
            self.current_overlay = WindowSnipOverlay(self.screen_pixmap, self.current_delay_sec)
        elif "Fullscreen" in mode:
            self.on_snip_completed(self.screen_pixmap)
            return
            
        if self.current_overlay:
            self.current_overlay.snip_completed.connect(self.on_snip_completed)
            
        if self.snip_toolbar:
            self.snip_toolbar.show()
            self.snip_toolbar.raise_()
            self.snip_toolbar.activateWindow()

    def on_snip_completed(self, image):
        if self.snip_toolbar:
            self.snip_toolbar.close()
            
        if image:
            scale_factor = 10 
            new_width = image.width() * scale_factor
            new_height = image.height() * scale_factor
            
            high_res_image = image.scaled(
                new_width, 
                new_height, 
                Qt.AspectRatioMode.IgnoreAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )

            self.scene.clear()
            self.scene.setSceneRect(0, 0, high_res_image.width(), high_res_image.height())
            self.scene.addPixmap(high_res_image)
            self.scene.set_base_pixmap(high_res_image)
            
            self.stacked_widget.setCurrentIndex(1)
            self.set_editing_tools_enabled(True)

            self.resize(1000, 600)
            
            screen_geom = QApplication.primaryScreen().availableGeometry()
            window_geom = self.frameGeometry()
            window_geom.moveCenter(screen_geom.center())
            self.move(window_geom.topLeft())
            
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(10, lambda: self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio))
            
        self.showNormal()
        self.activateWindow()

    def on_video_completed(self, filepath):
        if filepath:
            self.preview_window = VideoPreviewDialog(filepath, dark_mode=self.dark_mode, parent=self)
            self.preview_window.show()
        self.showNormal()

    def cancel_snip(self):
        if self.snip_toolbar: self.snip_toolbar.close()
        if self.current_overlay: self.current_overlay.close()
        self.showNormal()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'view') and self.scene.items():
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.update_canvas_cursor()
        if hasattr(self, 'shimmer'):
            self.shimmer.resize(self.view.size())

DARK_THEME_STYLESHEET = """
QWidget { color: #ffffff; font-family: "Segoe UI Variable", "Segoe UI", sans-serif; font-size: 14px; }
#mainContainer, #dialogContainer { background-color: transparent; border: none; }

#newButton { 
    background-color: #2b2b2b; 
    border: 1px solid #444444;
    border-radius: 18px; 
    padding: 0px 18px; 
    font-weight: 600; 
}
#newButton:hover { background-color: #383838; border: 1px solid #555555; }
#newButton:pressed { background-color: #222222; }

#toolbarButton { background-color: transparent; border: 1px solid transparent; border-radius: 6px; padding: 0 12px; text-align: left; }
#toolbarButton:hover { background-color: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.1); }
#toolbarButton:pressed { background-color: rgba(255, 255, 255, 0.04); color: #cccccc; }
#placeholderFrame { background-color: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; }
QMenu { background-color: #2c2c2c; border: 1px solid #444444; border-radius: 8px; padding: 4px; }
QMenu::item { padding: 6px 24px 6px 12px; border-radius: 4px; margin: 2px; }
QMenu::item:selected { background-color: #404040; }
"""

LIGHT_THEME_STYLESHEET = """
QWidget { color: #202020; font-family: "Segoe UI Variable", "Segoe UI", sans-serif; font-size: 14px; }
#mainContainer, #dialogContainer { background-color: #f3f3f3; border: 1px solid #e0e0e0; border-radius: 8px; }

#newButton { 
    background-color: #ffffff; 
    border: 1px solid #cccccc;
    border-radius: 18px; 
    padding: 0px 18px; 
    font-weight: 600; 
}
#newButton:hover { background-color: #f5f5f5; border: 1px solid #bbbbbb; }
#newButton:pressed { background-color: #e5e5e5; }

#toolbarButton { background-color: transparent; border: 1px solid transparent; border-radius: 6px; padding: 0 12px; text-align: left; }
#toolbarButton:hover { background-color: rgba(0, 0, 0, 0.05); border: 1px solid rgba(0, 0, 0, 0.1); }
#toolbarButton:pressed { background-color: rgba(0, 0, 0, 0.02); color: #555555; }
#placeholderFrame { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; }
QMenu { background-color: #ffffff; border: 1px solid #d0d0d0; border-radius: 8px; padding: 4px; }
QMenu::item { padding: 6px 24px 6px 12px; border-radius: 4px; margin: 2px; }
QMenu::item:selected { background-color: #f0f0f0; }
"""

if __name__ == "__main__":
    import ctypes
    myappid = 'polkboban.snippingtool.v1'
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except AttributeError:
        pass

    app = QApplication(sys.argv)
    
    from PyQt6.QtGui import QIcon
    app.setWindowIcon(QIcon("assets/app_icon.png"))
    
    dark_mode = is_dark_mode()
    app.setStyleSheet(DARK_THEME_STYLESHEET if dark_mode else LIGHT_THEME_STYLESHEET)
    win = SnippingToolGUI(dark_mode=dark_mode)
    win.show()
    sys.exit(app.exec())