import sys
import platform
import winreg
import keyboard
import pywinstyles

from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMenu, QMessageBox, QFileDialog, QFrame,
    QGraphicsView, QGraphicsScene, QGraphicsDropShadowEffect, QStackedWidget
)
from PyQt6.QtGui import (
    QPixmap, QColor, QFont, QIcon, QPainter, QAction,
    QPainterPath, QPen, QShortcut, QKeySequence, QLinearGradient
)
from PyQt6.QtCore import Qt, QTimer, QSize, QByteArray, pyqtSignal, QThread

from snip_modes.rectangle_snip import RectangleSnipOverlay
from snip_modes.freeform_snip import FreeformSnipOverlay
from snip_modes.window_snip import WindowSnipOverlay
from snip_modes.video_snip import VideoSnipOverlay

SVG_ICONS = {
    "record": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="3" fill="{color}"></circle></svg>""",
    "blur": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M8 12h8"></path><path d="M12 8v8"></path></svg>""",
    "text": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 7 4 4 20 4 20 7"></polyline><line x1="9" y1="20" x2="15" y2="20"></line><line x1="12" y1="4" x2="12" y2="20"></line></svg>""",
    "rect_tool": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect></svg>""",
    "plus": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>""",
    "rectangle": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}" width="18px" height="18px"><path d="M2 4.5A2.5 2.5 0 0 1 4.5 2h15A2.5 2.5 0 0 1 22 4.5v15a2.5 2.5 0 0 1-2.5 2.5h-15A2.5 2.5 0 0 1 2 19.5v-15ZM4.5 3A1.5 1.5 0 0 0 3 4.5v15A1.5 1.5 0 0 0 4.5 21h15a1.5 1.5 0 0 0 1.5-1.5v-15A1.5 1.5 0 0 0 19.5 3h-15Z"/></svg>""",
    "free-form": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}" width="18px" height="18px"><path d="M19.64 3.36a1.5 1.5 0 0 1 .42 2.08l-2.73 6.83a.5.5 0 0 0 .94.38l2.73-6.83a2.5 2.5 0 0 0-3.46-3.46l-6.83 2.73a.5.5 0 0 0 .38.94l6.83-2.73a1.5 1.5 0 0 1 2.08.42ZM8.41 6.1a1.5 1.5 0 0 1 2.49-1.59l.34.21a.5.5 0 0 0 .6-.2l.21-.34a1.5 1.5 0 0 1 2.49 1.59l-4.5 7.19a1.5 1.5 0 0 1-2.48 0L3.6 8.39a1.5 1.5 0 0 1 2.1-2.12l2.7 2.83ZM3.9 7.7a.5.5 0 0 0-.7.71l3.96 4.57a.5.5 0 0 0 .83 0l4.5-7.19a.5.5 0 0 0-.83-.53l-4.14 6.62-3.62-4.18Z"/></svg>""",
    "window": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}" width="18px" height="18px"><path d="M2 5.5A2.5 2.5 0 0 1 4.5 3h15A2.5 2.5 0 0 1 22 5.5v13a2.5 2.5 0 0 1-2.5 2.5h-15A2.5 2.5 0 0 1 2 18.5v-13ZM4.5 4A1.5 1.5 0 0 0 3 5.5v2A.5.5 0 0 0 3.5 8h17a.5.5 0 0 0 .5-.5v-2A1.5 1.5 0 0 0 19.5 4h-15ZM21 9H3v9.5A1.5 1.5 0 0 0 4.5 20h15a1.5 1.5 0 0 0 1.5-1.5V9Z"/></svg>""",
    "fullscreen": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}" width="18px" height="18px"><path d="M2.5 3A.5.5 0 0 0 2 3.5v5a.5.5 0 0 0 1 0v-4h4a.5.5 0 0 0 0-1h-5ZM21.5 3a.5.5 0 0 0-.5.5v4a.5.5 0 0 0 1 0v-4h4a.5.5 0 0 0 0-1h-5ZM2.5 16a.5.5 0 0 0-.5.5v5a.5.5 0 0 0 .5.5h5a.5.5 0 0 0 0-1h-4v-4a.5.5 0 0 0-1 0ZM22 15.5a.5.5 0 0 0-1 0v4h-4a.5.5 0 0 0 0 1h5a.5.5 0 0 0 .5-.5v-5Z"/></svg>""",
    "delay": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}" width="18px" height="18px"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2Zm0 19a9 9 0 1 1 9-9 9 9 0 0 1-9 9Z"/><path d="M12 6a.5.5 0 0 0-.5.5v5.79l-3.65 2.1a.5.5 0 0 0 .5.86l4-2.31A.5.5 0 0 0 12.5 12V6.5A.5.5 0 0 0 12 6Z"/></svg>""",
    "pen": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19l7-7 3 3-7 7-3-3z"></path><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"></path><path d="M2 2l7.586 7.586"></path><circle cx="11" cy="11" r="2"></circle></svg>""",
    "highlighter": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l-6 6v3h9l3-3"></path><path d="M22 12l-4.6 4.6a2 2 0 0 1-2.8 0l-5.2-5.2a2 2 0 0 1 0-2.8L14 4"></path></svg>""",
    "undo": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7v6h6"></path><path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"></path></svg>""",
    "save": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>""",
    "copy": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>"""
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
        self.base_pixmap = None
        
        self.pen_color = QColor(255, 0, 0)
        self.pen_width = 4
        self.current_tool = "pen" 
        self.update_pen()

    def update_pen(self):
        self.current_pen = QPen(self.pen_color, self.pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        if self.current_tool == "highlighter":
            color = QColor(self.pen_color)
            color.setAlpha(100)
            self.current_pen.setColor(color)
            self.current_pen.setWidth(15)
        elif self.current_tool == "blur":
            self.current_pen = QPen(QColor(100, 100, 100, 150), 2, Qt.PenStyle.DashLine)

    def set_color(self, color):
        self.pen_color = color
        self.update_pen()

    def set_tool(self, tool_name):
        self.current_tool = tool_name
        self.update_pen()

    def set_base_pixmap(self, pixmap):
        self.base_pixmap = pixmap

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
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

class ShimmerOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.offset = -300
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.is_animating = False
        self.hide()

    def start(self):
        self.show()
        self.offset = -300
        self.is_animating = True
        self.timer.start(16)

    def stop(self):
        self.hide()
        self.is_animating = False
        self.timer.stop()

    def animate(self):
        self.offset += 15
        if self.offset > self.width() + 300:
            self.offset = -300
        self.update()

    def paintEvent(self, event):
        if not self.is_animating: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80)) 
        gradient = QLinearGradient(self.offset, 0, self.offset + 300, self.height())
        gradient.setColorAt(0.0, QColor(255, 255, 255, 0))
        gradient.setColorAt(0.4, QColor(0, 0, 0, 150))
        gradient.setColorAt(0.5, QColor(255, 255, 255, 0))
        gradient.setColorAt(0.6, QColor(0, 0, 0, 150))
        gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(self.rect(), gradient)

class OCRWorker(QThread):
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, byte_array):
        super().__init__()
        self.byte_array = byte_array

    def run(self):
        try:
            import pytesseract
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
            text = pytesseract.image_to_string(pil_img)
            self.result_ready.emit(text)
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

    def __init__(self, dark_mode=False, initial_mode="Rectangle mode"):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.icon_color = "#ffffff" if dark_mode else "#000000"
        self.bg_color = "#2b2b2b" if dark_mode else "#ffffff"
        self.border_color = "#4a4a4a" if dark_mode else "#d0d0d0"
        self.hover_color = "#414141" if dark_mode else "#f0f0f0"
        self.active_color = "#0078d4" # Native windows blue indicator

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

        # Mode Buttons
        self.rect_btn = self.create_btn("rectangle", "Rectangle Snip", "Rectangle mode")
        self.free_btn = self.create_btn("free-form", "Freeform Snip", "Free-form mode")
        self.win_btn = self.create_btn("window", "Window Snip", "Window mode")
        self.full_btn = self.create_btn("fullscreen", "Fullscreen Snip", "Fullscreen mode")
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"background-color: {self.border_color};")
        
        # Close Button
        self.close_btn = QPushButton("✕")
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

class VideoPreviewDialog(QMainWindow):
    def __init__(self, video_path, dark_mode=False, parent=None):
        super().__init__(parent=parent)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle("Snipping Tool - Video Preview")
        self.resize(1000, 700)
        
        self.video_path = video_path
        self.dark_mode = dark_mode
        self.is_playing = True

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
        
        self.setup_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(int(1000 / self.fps))

    def setup_ui(self):
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        toolbar = QWidget()
        toolbar.setFixedHeight(55)
        t_layout = QHBoxLayout(toolbar)
        t_layout.setContentsMargins(15, 0, 15, 0)

        btn_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 10px;
                color: {"#ffffff" if self.dark_mode else "#000000"};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {"#383838" if self.dark_mode else "#e0e0e0"};
            }}
        """

        self.play_btn = QPushButton("⏸ Pause")
        self.play_btn.setStyleSheet(btn_style)
        self.play_btn.clicked.connect(self.toggle_playback)

        self.save_btn = QPushButton("💾 Save Video As...")
        self.save_btn.setStyleSheet(btn_style)
        self.save_btn.clicked.connect(self.save_video)

        t_layout.addWidget(self.play_btn)
        t_layout.addStretch(1)
        t_layout.addWidget(self.save_btn)

        main_layout.addWidget(toolbar)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background-color: {'#3a3a3a' if self.dark_mode else '#e0e0e0'};")
        divider.setFixedHeight(1)
        main_layout.addWidget(divider)

        bg_color = 'transparent'
        self.player_container = QWidget()
        self.player_container.setStyleSheet(f"background-color: {bg_color};")
        
        p_layout = QVBoxLayout(self.player_container)
        p_layout.setContentsMargins(40, 40, 40, 40)

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 4)
        self.video_label.setGraphicsEffect(shadow)
        
        p_layout.addWidget(self.video_label)
        main_layout.addWidget(self.player_container, 1)

    def update_frame(self):
        if not self.is_playing:
            return
            
        ret, frame = self.cap.read()
        
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            
            from PyQt6.QtGui import QImage, QPixmap
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            
            self.video_label.setPixmap(pixmap.scaled(
                self.video_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))

    def toggle_playback(self):
        self.is_playing = not self.is_playing
        self.play_btn.setText("⏸ Pause" if self.is_playing else "▶ Play")

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

class SnippingToolGUI(QMainWindow):
    def __init__(self, dark_mode=False):
        super().__init__()
        self.dark_mode = dark_mode
        self.icon_color = "#ffffff" if dark_mode else "#000000"

        self.setWindowTitle("Snipping Tool")
        self.resize(1000, 700)
        self.setMinimumSize(520, 300)

        pywinstyles.apply_style(self, "mica")
        header_color = "#1f1f1f" if dark_mode else "#f3f3f3"
        pywinstyles.change_header_color(self, header_color)
        if dark_mode: pywinstyles.apply_style(self, "dark")

        self.snip_modes = ["Rectangle mode", "Free-form mode", "Window mode", "Fullscreen mode"]
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

    def setup_ui(self):
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.top_toolbar = QWidget()
        self.top_toolbar.setFixedHeight(55)
        t_layout = QHBoxLayout(self.top_toolbar)
        t_layout.setContentsMargins(15, 0, 15, 0)
        t_layout.setSpacing(5)

        self.new_btn = QPushButton(" New")
        self.new_btn.setObjectName("newButton")
        self.new_btn.clicked.connect(self.start_snip)
        self.new_btn.setFixedHeight(36)
        self.new_btn.setIcon(create_svg_icon("plus", "#ffffff" if not self.dark_mode else self.icon_color)) 
        
        self.mode_btn = QPushButton()
        self.mode_btn.setObjectName("toolbarButton")
        self.mode_btn.setFixedHeight(36)
        self.mode_btn.clicked.connect(self.show_mode_menu)
        self.update_mode_button()
        
        self.delay_btn = QPushButton()
        self.delay_btn.setObjectName("toolbarButton")
        self.delay_btn.setFixedHeight(36)
        self.delay_btn.clicked.connect(self.show_delay_menu)
        self.update_delay_button()

        t_layout.addWidget(self.new_btn)
        t_layout.addWidget(self.mode_btn)
        t_layout.addWidget(self.delay_btn)
        t_layout.addStretch(1)
        
        main_layout.addWidget(self.top_toolbar)
        
        h_div_top = QFrame()
        h_div_top.setFrameShape(QFrame.Shape.HLine)
        h_div_top.setStyleSheet(f"background-color: {'#3a3a3a' if self.dark_mode else '#e0e0e0'};")
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
        
        instruction_label = QLabel("Press Windows logo key + Shift + S to start a snip.")
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label.setStyleSheet("color: #a0a0a0; margin-top: 10px;")
        pf_layout.addWidget(instruction_label)

        p_layout.addWidget(self.placeholder_frame)
        self.stacked_widget.addWidget(self.placeholder_page)

        self.canvas_page = QWidget()
        c_layout = QVBoxLayout(self.canvas_page)
        c_layout.setContentsMargins(40, 40, 40, 40)
        
        self.scene = AnnotationScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setStyleSheet("background: transparent; border: none;")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 4)
        self.view.setGraphicsEffect(shadow)
        c_layout.addWidget(self.view)
        
        self.stacked_widget.addWidget(self.canvas_page)

        self.h_div_bottom = QFrame()
        self.h_div_bottom.setFrameShape(QFrame.Shape.HLine)
        self.h_div_bottom.setStyleSheet(f"background-color: {'#3a3a3a' if self.dark_mode else '#e0e0e0'};")
        main_layout.addWidget(self.h_div_bottom)

        self.bottom_toolbar = QWidget()
        self.bottom_toolbar.setFixedHeight(55)
        b_layout = QHBoxLayout(self.bottom_toolbar)
        b_layout.setContentsMargins(15, 0, 15, 0)
        b_layout.setSpacing(5)

        btn_style = f"""
            QPushButton {{ background: transparent; border: none; border-radius: 6px; padding: 10px; }}
            QPushButton:hover {{ background-color: {"#383838" if self.dark_mode else "#e0e0e0"}; }}
            QPushButton:checked {{ background-color: {"#4a4a4a" if self.dark_mode else "#d0d0d0"}; border-bottom: 3px solid {"#0078d4" if not self.dark_mode else "#4cc2ff"}; }}
            QPushButton:disabled {{ opacity: 0.5; }}
        """

        self.pen_btn = QPushButton()
        self.pen_btn.setIcon(create_svg_icon("pen", self.icon_color))
        self.pen_btn.setCheckable(True)
        self.pen_btn.setChecked(True)
        self.pen_btn.setStyleSheet(btn_style)
        self.pen_btn.clicked.connect(lambda: self.switch_tool("pen"))

        self.highlight_btn = QPushButton()
        self.highlight_btn.setIcon(create_svg_icon("highlighter", self.icon_color))
        self.highlight_btn.setCheckable(True)
        self.highlight_btn.setStyleSheet(btn_style)
        self.highlight_btn.clicked.connect(lambda: self.switch_tool("highlighter"))

        self.rect_btn = QPushButton()
        self.rect_btn.setIcon(create_svg_icon("rect_tool", self.icon_color))
        self.rect_btn.setCheckable(True)
        self.rect_btn.setStyleSheet(btn_style)
        self.rect_btn.clicked.connect(lambda: self.switch_tool("rectangle"))

        self.blur_btn = QPushButton()
        self.blur_btn.setIcon(create_svg_icon("blur", self.icon_color))
        self.blur_btn.setCheckable(True)
        self.blur_btn.setStyleSheet(btn_style)
        self.blur_btn.clicked.connect(lambda: self.switch_tool("blur"))

        self.color_btn = QPushButton()
        self.color_btn.setStyleSheet(f"background-color: #ff0000; border-radius: 10px; min-width: 20px; max-width: 20px; min-height: 20px; max-height: 20px; margin: 5px;")
        self.color_btn.clicked.connect(self.choose_color)

        self.undo_btn = QPushButton()
        self.undo_btn.setIcon(create_svg_icon("undo", self.icon_color))
        self.undo_btn.setStyleSheet(btn_style)
        self.undo_btn.clicked.connect(self.undo_stroke)

        self.ocr_btn = QPushButton()
        self.ocr_btn.setIcon(create_svg_icon("text", self.icon_color))
        self.ocr_btn.setStyleSheet(btn_style)
        self.ocr_btn.clicked.connect(self.extract_text)

        self.copy_btn = QPushButton()
        self.copy_btn.setIcon(create_svg_icon("copy", self.icon_color))
        self.copy_btn.setStyleSheet(btn_style)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)

        self.save_btn = QPushButton()
        self.save_btn.setIcon(create_svg_icon("save", self.icon_color))
        self.save_btn.setStyleSheet(btn_style)
        self.save_btn.clicked.connect(self.save_image)

        b_layout.addWidget(self.pen_btn)
        b_layout.addWidget(self.highlight_btn)
        b_layout.addWidget(self.rect_btn)
        b_layout.addWidget(self.blur_btn)
        b_layout.addWidget(self.color_btn)
        b_layout.addWidget(self.undo_btn)
        b_layout.addStretch(1)
        b_layout.addWidget(self.ocr_btn)
        b_layout.addWidget(self.copy_btn)
        b_layout.addWidget(self.save_btn)

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

    def set_editing_tools_enabled(self, enabled):
        if enabled:
            self.bottom_toolbar.show()
            self.h_div_bottom.show()
        else:
            self.bottom_toolbar.hide()
            self.h_div_bottom.hide()

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
        actions = { "Rectangle mode": "rectangle", "Free-form mode": "free-form", "Window mode": "window", "Fullscreen mode": "fullscreen", "Record mode": "record" }
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
        self.pen_btn.setChecked(tool_name == "pen")
        self.highlight_btn.setChecked(tool_name == "highlighter")
        self.rect_btn.setChecked(tool_name == "rectangle")
        self.blur_btn.setChecked(tool_name == "blur")
        self.scene.set_tool(tool_name)

    def choose_color(self):
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(self.scene.pen_color, self, "Choose Pen Color")
        if color.isValid():
            self.scene.set_color(color)
            self.color_btn.setStyleSheet(f"background-color: {color.name()}; border-radius: 10px; min-width: 20px; max-width: 20px; min-height: 20px; max-height: 20px; margin: 5px;")

    def undo_stroke(self): self.scene.undo()

    def extract_text(self):
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

    def on_ocr_complete(self, text):
        self.shimmer.stop()
        self.ocr_btn.setEnabled(True)
        if text.strip():
            QApplication.clipboard().setText(text)
            self.show_toast("Text copied to clipboard!")
        else:
            QMessageBox.information(self, "No Text Found", "Could not detect any text.")

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
        QApplication.clipboard().setPixmap(self.get_rendered_image())
        self.show_toast("Copied to clipboard!")

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
        if "Record" in self.current_mode:
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
            self.current_overlay.close()
            self.current_overlay.deleteLater()

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

    def on_snip_completed(self, image):
        if self.snip_toolbar:
            self.snip_toolbar.close()
            
        if image:
            self.scene.clear()
            self.scene.setSceneRect(0, 0, image.width(), image.height())
            self.scene.addPixmap(image)
            self.scene.set_base_pixmap(image)
            
            self.stacked_widget.setCurrentIndex(1)
            self.set_editing_tools_enabled(True)
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            
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
        if hasattr(self, 'shimmer'):
            self.shimmer.resize(self.view.size())

DARK_THEME_STYLESHEET = """
QWidget { color: #ffffff; font-family: "Segoe UI Variable", sans-serif; font-size: 14px; }
#mainContainer, #dialogContainer { background-color: transparent; border: none; }
#newButton { background-color: #D72828; border: 1px solid #6B6B6B; border-radius: 4px; padding: 0px 16px; font-weight: 600; }
#newButton:hover { background-color: #FF1414; }
#toolbarButton { background-color: #323232; border: 1px solid #4a4a4a; border-radius: 4px; padding: 0 10px; text-align: left; }
#toolbarButton:hover { background-color: #414141; }
#placeholderFrame { background-color: #2b2b2b; border: 1px solid #3a3a3a; border-radius: 6px; }
QMenu { background-color: #2b2b2b; border: 1px solid #4a4a4a; border-radius: 6px; padding: 4px; }
QMenu::item { padding: 6px 16px; border-radius: 4px; }
QMenu::item:selected { background-color: #414141; }
"""

LIGHT_THEME_STYLESHEET = """
QWidget { color: #000000; font-family: "Segoe UI Variable", sans-serif; font-size: 14px; }
#mainContainer, #dialogContainer { background-color: #f3f3f3; border: 1px solid #e0e0e0; border-radius: 8px; }
#newButton { background-color: #0078d4; border: 1px solid #0078d4; border-radius: 4px; padding: 0px 16px; font-weight: 600; color: white; }
#newButton:hover { background-color: #108ee9; }
#toolbarButton { background-color: #ffffff; border: 1px solid #d0d0d0; border-radius: 4px; padding: 0 10px; text-align: left; }
#toolbarButton:hover { background-color: #f0f0f0; }
#placeholderFrame { background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 6px; }
QMenu { background-color: #ffffff; border: 1px solid #d0d0d0; border-radius: 6px; padding: 4px; }
QMenu::item { padding: 6px 16px; border-radius: 4px; }
QMenu::item:selected { background-color: #f0f0f0; }
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dark_mode = is_dark_mode()
    app.setStyleSheet(DARK_THEME_STYLESHEET if dark_mode else LIGHT_THEME_STYLESHEET)
    win = SnippingToolGUI(dark_mode=dark_mode)
    win.show()
    sys.exit(app.exec())