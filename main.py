# main.py

import sys
import platform
import winreg
import pyautogui
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt, QTimer

from io import BytesIO

from PIL import ImageQt
from PyQt5.QtWidgets import QLabel, QDialog, QDialogButtonBox, QFileDialog, QPushButton
from PyQt5.QtGui import QPixmap, QClipboard
from PyQt5.QtWidgets import QVBoxLayout


from snip_modes.rectangle_snip import RectangleSnipOverlay
from snip_modes.freeform_snip import FreeformSnipOverlay

def is_dark_mode():
    if platform.system() == "Windows":
        try:
            reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(reg, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except Exception as e:
            print(f"Error checking dark mode: {e}")
            return False
    return False

class ImagePreviewDialog(QDialog):
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preview Snip")
        self.resize(500,480)
        self.setMinimumSize(400,320)
        self.image = image  

        layout = QVBoxLayout()

        label = QLabel()
        buffer = BytesIO()
        self.image.save(buffer, format='PNG')
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())

        label.setPixmap(pixmap.scaled(480, 320, Qt.KeepAspectRatio))
        layout.addWidget(label)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        copy_btn = QPushButton("Copy")
        buttons.addButton(copy_btn, QDialogButtonBox.ActionRole)

        buttons.accepted.connect(self.save_image)
        buttons.rejected.connect(self.reject)
        copy_btn.clicked.connect(self.copy_to_clipboard)

        layout.addWidget(buttons)
        self.setLayout(layout)

    def save_image(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Screenshot", "", "PNG Files (*.png)")
        if path:
            self.image.save(path)
        self.accept()

    def copy_to_clipboard(self):
        buffer = BytesIO()
        self.image.save(buffer, format='PNG')
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())

        clipboard = QApplication.clipboard()
        clipboard.setPixmap(pixmap)

class SnippingToolGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snipping Tool Clone")
        self.resize(500,180)
        self.setMinimumSize(400,120)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        toolbar_layout = QHBoxLayout()

        #buttons
        self.new_btn = QPushButton("New")
        self.new_btn.clicked.connect(self.start_snip)
        self.new_btn.setFixedHeight(40)

        self.mode_label = QLabel("Mode:")
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(["Rectangle", "Free-form", "Fullscreen"])

        self.delay_label = QLabel("Delay:")
        self.delay_dropdown = QComboBox()
        self.delay_dropdown.addItems(["0", "3", "5"])

        toolbar_layout.addWidget(self.new_btn)
        toolbar_layout.addSpacing(20)
        toolbar_layout.addWidget(self.mode_label)
        toolbar_layout.addWidget(self.mode_dropdown)
        toolbar_layout.addSpacing(20)
        toolbar_layout.addWidget(self.delay_label)
        toolbar_layout.addWidget(self.delay_dropdown)

        main_layout.addLayout(toolbar_layout)
        main_layout.addStretch()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def start_snip(self):
        mode = self.mode_dropdown.currentText()
        delay = int(self.delay_dropdown.currentText())
        self.hide()

        if mode == "Rectangle":
            self.rect_snip = RectangleSnipOverlay(delay)
            self.rect_snip.snip_completed.connect(self.show_preview)
        elif mode.startswith("Free-form"):
            self.freeform_snip = FreeformSnipOverlay(delay)
            self.freeform_snip.snip_completed.connect(self.show_preview)
        elif mode == "Fullscreen":
            QTimer.singleShot(delay * 1000, self.capture_fullscreen)
        else:
            QMessageBox.information(self, "Coming Soon", f"{mode} is not implemented yet.")
            self.show()

    def capture_fullscreen(self):
        screenshot = pyautogui.screenshot()
        self.show_preview(screenshot)

    def show_preview(self, image):
        preview = ImagePreviewDialog(image, self)
        preview.exec_()
        self.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)

    if is_dark_mode():
        app.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-size: 13px;
            }
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #444;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QComboBox {
                background-color: #2d2d2d;
                border: 1px solid #555;
                padding: 4px;
                color: #e0e0e0;
            }
            QComboBox::drop-down {
                border: none;
            }
            QLabel {
                font-weight: 500;
            }
        """)
    win = SnippingToolGUI()
    win.show()
    sys.exit(app.exec_())



