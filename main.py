import sys
import platform
import winreg
import pyautogui
from io import BytesIO

from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMenu, QAction, QMessageBox, QDialog,
    QDialogButtonBox, QFileDialog, QGraphicsDropShadowEffect, QFrame, QSizeGrip
)
from PyQt5.QtGui import QPixmap, QColor, QFont, QIcon, QPainter
from PyQt5.QtCore import Qt, QTimer, QSize, QByteArray, pyqtSignal

from snip_modes.rectangle_snip import RectangleSnipOverlay
from snip_modes.freeform_snip import FreeformSnipOverlay

class WindowSnipOverlay(QWidget):
    snip_completed = pyqtSignal(object)
    def __init__(self, delay=0):
        super().__init__()
        QTimer.singleShot(100, self.show_message)

    def show_message(self):
        QMessageBox.information(None, "Not Implemented", "Window mode is not yet implemented.")
        self.snip_completed.emit(None)
        self.close()

SVG_ICONS = {
    "plus": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>""",
    "rectangle": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}" width="18px" height="18px"><path d="M2 4.5A2.5 2.5 0 0 1 4.5 2h15A2.5 2.5 0 0 1 22 4.5v15a2.5 2.5 0 0 1-2.5 2.5h-15A2.5 2.5 0 0 1 2 19.5v-15ZM4.5 3A1.5 1.5 0 0 0 3 4.5v15A1.5 1.5 0 0 0 4.5 21h15a1.5 1.5 0 0 0 1.5-1.5v-15A1.5 1.5 0 0 0 19.5 3h-15Z"/></svg>""",
    "freeform": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}" width="18px" height="18px"><path d="M19.64 3.36a1.5 1.5 0 0 1 .42 2.08l-2.73 6.83a.5.5 0 0 0 .94.38l2.73-6.83a2.5 2.5 0 0 0-3.46-3.46l-6.83 2.73a.5.5 0 0 0 .38.94l6.83-2.73a1.5 1.5 0 0 1 2.08.42ZM8.41 6.1a1.5 1.5 0 0 1 2.49-1.59l.34.21a.5.5 0 0 0 .6-.2l.21-.34a1.5 1.5 0 0 1 2.49 1.59l-4.5 7.19a1.5 1.5 0 0 1-2.48 0L3.6 8.39a1.5 1.5 0 0 1 2.1-2.12l2.7 2.83ZM3.9 7.7a.5.5 0 0 0-.7.71l3.96 4.57a.5.5 0 0 0 .83 0l4.5-7.19a.5.5 0 0 0-.83-.53l-4.14 6.62-3.62-4.18Z"/></svg>""",
    "window": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}" width="18px" height="18px"><path d="M2 5.5A2.5 2.5 0 0 1 4.5 3h15A2.5 2.5 0 0 1 22 5.5v13a2.5 2.5 0 0 1-2.5 2.5h-15A2.5 2.5 0 0 1 2 18.5v-13ZM4.5 4A1.5 1.5 0 0 0 3 5.5v2A.5.5 0 0 0 3.5 8h17a.5.5 0 0 0 .5-.5v-2A1.5 1.5 0 0 0 19.5 4h-15ZM21 9H3v9.5A1.5 1.5 0 0 0 4.5 20h15a1.5 1.5 0 0 0 1.5-1.5V9Z"/></svg>""",
    "fullscreen": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}" width="18px" height="18px"><path d="M2.5 3A.5.5 0 0 0 2 3.5v5a.5.5 0 0 0 1 0v-4h4a.5.5 0 0 0 0-1h-5ZM21.5 3a.5.5 0 0 0-.5.5v4a.5.5 0 0 0 1 0v-4h4a.5.5 0 0 0 0-1h-5ZM2.5 16a.5.5 0 0 0-.5.5v5a.5.5 0 0 0 .5.5h5a.5.5 0 0 0 0-1h-4v-4a.5.5 0 0 0-1 0ZM22 15.5a.5.5 0 0 0-1 0v4h-4a.5.5 0 0 0 0 1h5a.5.5 0 0 0 .5-.5v-5Z"/></svg>""",
    "delay": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{color}" width="18px" height="18px"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2Zm0 19a9 9 0 1 1 9-9 9 9 0 0 1-9 9Z"/><path d="M12 6a.5.5 0 0 0-.5.5v5.79l-3.65 2.1a.5.5 0 0 0 .5.86l4-2.31A.5.5 0 0 0 12.5 12V6.5A.5.5 0 0 0 12 6Z"/></svg>""",
}

def create_svg_icon(name, color):
    svg_data = SVG_ICONS[name].format(color=color)
    renderer = QSvgRenderer(QByteArray(svg_data.encode('utf-8')))
    pixmap = QPixmap(renderer.defaultSize())
    pixmap.fill(Qt.transparent)
    painter = QPainter()
    painter.begin(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

def is_dark_mode():
    if platform.system() == "Windows":
        try:
            reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(
                reg, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except Exception:
            return False
    return False

class CustomTitleBarWindow(QMainWindow):
    def __init__(self, dark_mode=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.main_wrapper = QWidget()
        self.main_wrapper.setAttribute(Qt.WA_TranslucentBackground)
        main_layout = QVBoxLayout(self.main_wrapper)
        main_layout.setContentsMargins(35, 35, 35, 35)
        self.setCentralWidget(self.main_wrapper)

        self.container = QWidget(self)
        self.container.setObjectName("mainContainer")
        main_layout.addWidget(self.container)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(35)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 100 if dark_mode else 80))
        self.container.setGraphicsEffect(shadow)

        self.v_layout = QVBoxLayout(self.container)
        self.v_layout.setContentsMargins(1, 1, 1, 1)
        self.v_layout.setSpacing(0)

        self.title_bar = QWidget()
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(40)
        self.title_bar.mouseDoubleClickEvent = self.toggle_maximize
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(15, 0, 5, 0)

        self.title_label = QLabel(self.windowTitle())
        self.title_label.setObjectName("titleLabel")
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        self.min_btn = QPushButton("—")
        self.min_btn.setObjectName("titleButton")
        self.min_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.min_btn)
        
        self.max_btn = QPushButton("⬜")
        self.max_btn.setObjectName("titleButton")
        self.max_btn.clicked.connect(self.toggle_maximize)
        title_layout.addWidget(self.max_btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("titleButton")
        self.close_btn.setProperty("id", "closeButton")
        self.close_btn.clicked.connect(self.close)
        title_layout.addWidget(self.close_btn)

        self.v_layout.addWidget(self.title_bar)

        self.content = QWidget()
        self.v_layout.addWidget(self.content)
        
        self.grip = QSizeGrip(self.container)
        self.grip.setStyleSheet("background-color: transparent;")
        self.v_layout.addWidget(self.grip, 0, Qt.AlignBottom | Qt.AlignRight)

    def toggle_maximize(self, event=None):
        if self.isMaximized():
            self.showNormal()
            self.main_wrapper.layout().setContentsMargins(35, 35, 35, 35)
        else:
            self.showMaximized()
            self.main_wrapper.layout().setContentsMargins(0, 0, 0, 0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() < (self.title_bar.height() + 35):
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if hasattr(self, "_drag_pos") and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def setWindowTitle(self, title):
        super().setWindowTitle(title)
        if hasattr(self, 'title_label'):
            self.title_label.setText(title)

class ImagePreviewDialog(QDialog):
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(800, 600) 
        self.image = image

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)

        wrapper = QWidget()
        wrapper.setObjectName("dialogContainer")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 180))
        wrapper.setGraphicsEffect(shadow)

        v_layout = QVBoxLayout(wrapper)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        v_layout.addWidget(self.image_label, 1)

        buttons = QDialogButtonBox()
        self.save_btn = buttons.addButton("Save", QDialogButtonBox.AcceptRole)
        self.copy_btn = buttons.addButton("Copy", QDialogButtonBox.ActionRole)
        self.close_btn = buttons.addButton("Close", QDialogButtonBox.RejectRole)
        
        buttons.accepted.connect(self.save_image)
        buttons.rejected.connect(self.reject)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)

        v_layout.addWidget(buttons)
        layout.addWidget(wrapper)
        
        self.grip = QSizeGrip(wrapper)
        self.grip.setStyleSheet("margin: 5px;")
        v_layout.addWidget(self.grip, 0, Qt.AlignBottom | Qt.AlignRight)

        buffer = BytesIO()
        self.image.save(buffer, format="PNG")
        self.base_pixmap = QPixmap()
        self.base_pixmap.loadFromData(buffer.getvalue())
        self.update_image_display()

    def update_image_display(self):
        scaled_pixmap = self.base_pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image_display()

    def save_image(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", "", "PNG Files (*.png)")
        if path:
            self.image.save(path)
        self.accept()

    def copy_to_clipboard(self):
        buffer = BytesIO()
        self.image.save(buffer, format="PNG")
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        QApplication.clipboard().setPixmap(pixmap)
        self.accept()

class SnippingToolGUI(CustomTitleBarWindow):
    def __init__(self, dark_mode=False):
        super().__init__(dark_mode=dark_mode)
        self.dark_mode = dark_mode
        self.icon_color = "#ffffff" if dark_mode else "#000000"

        self.setWindowTitle("Snipping Tool")
        self.resize(620, 300)
        self.setMinimumSize(520, 300)

        self.snip_modes = ["Rectangle mode", "Free-form mode", "Window mode", "Fullscreen mode"]
        self.delays = ["No delay", "3 seconds", "5 seconds", "10 seconds"]
        self.current_mode = self.snip_modes[0]
        self.current_delay_sec = 0
        
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self.content)
        main_layout.setContentsMargins(12, 8, 12, 0)
        main_layout.setSpacing(10)
        
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(8)

        self.new_btn = QPushButton(" New")
        self.new_btn.setObjectName("newButton")
        self.new_btn.clicked.connect(self.start_snip)
        self.new_btn.setFixedHeight(36)
        
        self.new_btn.setIcon(create_svg_icon("plus", self.icon_color))
        self.new_btn.setIconSize(QSize(20, 20))
        
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
        
        self.more_btn = QPushButton("...")
        self.more_btn.setObjectName("toolbarButton")
        self.more_btn.setFixedSize(36, 36)

        toolbar_layout.addWidget(self.new_btn)
        toolbar_layout.addWidget(self.mode_btn)
        toolbar_layout.addWidget(self.delay_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.more_btn)
        
        placeholder = QFrame()
        placeholder.setObjectName("placeholderFrame")
        placeholder_layout = QVBoxLayout(placeholder)
        placeholder_layout.setAlignment(Qt.AlignCenter)
        
        placeholder_label = QLabel("Snip and share")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setObjectName("placeholderLabel")
        placeholder_layout.addWidget(placeholder_label)

        main_layout.addWidget(toolbar)
        main_layout.addWidget(placeholder, 1)

    def update_mode_button(self):
        icon_name = self.current_mode.split(' ')[0].lower()
        self.mode_btn.setText(f" {self.current_mode}")
        self.mode_btn.setIcon(create_svg_icon(icon_name, self.icon_color))
        self.mode_btn.setIconSize(QSize(18, 18))
        
    def update_delay_button(self):
        self.delay_btn.setText(f" {self.delays[self.get_delay_index()]}")
        self.delay_btn.setIcon(create_svg_icon("delay", self.icon_color))
        self.delay_btn.setIconSize(QSize(18, 18))

    def show_mode_menu(self):
        menu = QMenu(self)
        menu.setObjectName("contextMenu")
        
        actions = {
            "Rectangle mode": "rectangle",
            "Free-form mode": "freeform",
            "Window mode": "window",
            "Fullscreen mode": "fullscreen"
        }
        
        for text, icon_name in actions.items():
            action = QAction(create_svg_icon(icon_name, self.icon_color), text, self)
            action.triggered.connect(lambda checked, t=text: self.set_mode(t))
            menu.addAction(action)
            
        menu.exec_(self.mode_btn.mapToGlobal(self.mode_btn.rect().bottomLeft()))

    def show_delay_menu(self):
        menu = QMenu(self)
        menu.setObjectName("contextMenu")
        
        for i, text in enumerate(self.delays):
            action = QAction(text, self)
            action.triggered.connect(lambda checked, idx=i: self.set_delay(idx))
            menu.addAction(action)
            
        menu.exec_(self.delay_btn.mapToGlobal(self.delay_btn.rect().bottomLeft()))

    def set_mode(self, mode):
        self.current_mode = mode
        self.update_mode_button()

    def set_delay(self, index):
        self.current_delay_sec = [0, 3, 5, 10][index]
        self.update_delay_button()

    def get_delay_index(self):
        return {0: 0, 3: 1, 5: 2, 10: 3}.get(self.current_delay_sec, 0)

    def start_snip(self):
        self.hide()
        QTimer.singleShot(200, self.initiate_capture)

    def initiate_capture(self):
        if "Rectangle" in self.current_mode:
            self.snip_overlay = RectangleSnipOverlay(self.current_delay_sec)
            self.snip_overlay.snip_completed.connect(self.show_preview)
        elif "Free-form" in self.current_mode:
            self.snip_overlay = FreeformSnipOverlay(self.current_delay_sec) 
            self.snip_overlay.snip_completed.connect(self.show_preview)
        elif "Window" in self.current_mode:
            self.snip_overlay = WindowSnipOverlay(self.current_delay_sec)
            self.snip_overlay.snip_completed.connect(self.show_preview)
        elif "Fullscreen" in self.current_mode:
            QTimer.singleShot(self.current_delay_sec * 1000, self.capture_fullscreen)
        else:
            QMessageBox.information(self, "Coming Soon", f"{self.current_mode} not implemented.")
            self.show()

    def capture_fullscreen(self):
        screenshot = pyautogui.screenshot()
        self.show_preview(screenshot)

    def show_preview(self, image):
        if image:
            preview = ImagePreviewDialog(image, self)
            preview.exec_()
        self.show()

DARK_THEME_STYLESHEET = """
QWidget {
    color: #ffffff;
    font-family: "Segoe UI Variable", sans-serif;
    font-size: 14px;
}
#mainContainer, #dialogContainer {
    background-color: #1f1f1f;
    border: 1px solid #3a3a3a;
    border-radius: 8px;
}
#titleBar {
    background-color: #1f1f1f;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}
#titleLabel {
    color: #f0f0f0; 
    font-weight: 600;
}
#titleButton {
    background-color: transparent;
    border: none;
    min-width: 40px;
    height: 40px;
    font-size: 12px;
}
#titleButton:hover { background-color: #383838; }
#closeButton:hover { background-color: #E81123; }
#maxButton:hover { background-color: #383838; }

#newButton {
    background-color: #D72828;
    border: 1px solid #6B6B6B;
    border-radius: 4px;
    padding: 0px 16px;
    font-weight: 600;
}
#newButton:hover { background-color: #FF1414; }
#newButton:pressed { background-color: #FF0A0A; }

#toolbarButton {
    background-color: #323232;
    border: 1px solid #4a4a4a;
    border-radius: 4px;
    padding: 0 10px;
    text-align: left;
}
#toolbarButton:hover { background-color: #414141; }
#toolbarButton:pressed { background-color: #2a2a2a; }

#placeholderFrame {
    background-color: #2b2b2b;
    border: 1px solid #3a3a3a;
    border-radius: 6px;
}
#placeholderLabel { color: #a0a0a0; }

QDialogButtonBox QPushButton {
    background-color: #323232;
    border: 1px solid #4a4a4a;
    border-radius: 4px;
    padding: 8px 16px;
    min-width: 80px;
}
QDialogButtonBox QPushButton:hover { background-color: #414141; }

QMenu {
    background-color: #2b2b2b;
    border: 1px solid #4a4a4a;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 16px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #414141;
}
"""

LIGHT_THEME_STYLESHEET = """
QWidget {
    color: #000000;
    font-family: "Segoe UI Variable", sans-serif;
    font-size: 14px;
}
#mainContainer, #dialogContainer {
    background-color: #f3f3f3;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
}
#titleBar {
    background-color: #f3f3f3;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}
#titleLabel {
    color: #1c1c1c; 
    font-weight: 600;
}
#titleButton {
    background-color: transparent;
    border: none;
    min-width: 40px;
    height: 40px;
    font-size: 12px;
}
#titleButton:hover { background-color: #e0e0e0; }
#closeButton:hover { background-color: #E81123; color: white; }
#maxButton:hover { background-color: #e0e0e0; }

#newButton {
    background-color: #0078d4;
    border: 1px solid #0078d4;
    border-radius: 4px;
    padding: 0px 16px;
    font-weight: 600;
    color: white;
}
#newButton:hover { background-color: #108ee9; }
#newButton:pressed { background-color: #005a9e; }

#toolbarButton {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 0 10px;
    text-align: left;
}
#toolbarButton:hover { background-color: #f0f0f0; }
#toolbarButton:pressed { background-color: #e0e0e0; }

#placeholderFrame {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
}
#placeholderLabel { color: #606060; }

QDialogButtonBox QPushButton {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 8px 16px;
    min-width: 80px;
}
QDialogButtonBox QPushButton:hover { background-color: #f0f0f0; }

QMenu {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 16px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #f0f0f0;
}
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    dark_mode = is_dark_mode()
    
    app.setStyleSheet(DARK_THEME_STYLESHEET if dark_mode else LIGHT_THEME_STYLESHEET)
    
    win = SnippingToolGUI(dark_mode=dark_mode)
    win.show()
    sys.exit(app.exec_())