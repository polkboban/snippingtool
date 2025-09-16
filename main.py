# main.py (modern Snipping Tool look)
import sys
import platform
import winreg
import pyautogui
from io import BytesIO

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QMessageBox, QDialog,
    QDialogButtonBox, QFileDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

from snip_modes.rectangle_snip import RectangleSnipOverlay
from snip_modes.freeform_snip import FreeformSnipOverlay


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


class ImagePreviewDialog(QDialog):
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Snip Preview")
        self.resize(600, 420)
        self.image = image

        layout = QVBoxLayout()

        label = QLabel()
        buffer = BytesIO()
        self.image.save(buffer, format="PNG")
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        label.setPixmap(pixmap.scaled(580, 360, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Close)
        copy_btn = QPushButton("Copy")
        buttons.addButton(copy_btn, QDialogButtonBox.ActionRole)

        buttons.accepted.connect(self.save_image)
        buttons.rejected.connect(self.reject)
        copy_btn.clicked.connect(self.copy_to_clipboard)

        layout.addWidget(buttons)
        self.setLayout(layout)

    def save_image(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Screenshot", "", "PNG Files (*.png)"
        )
        if path:
            self.image.save(path)
        self.accept()

    def copy_to_clipboard(self):
        buffer = BytesIO()
        self.image.save(buffer, format="PNG")
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        QApplication.clipboard().setPixmap(pixmap)


class SnippingToolGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snipping Tool")
        self.resize(600, 300)
        self.setMinimumSize(500, 200)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # --- Top toolbar ---
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        toolbar.setStyleSheet("background-color: #2b2b2b;")

        # New button
        self.new_btn = QPushButton(" +  New ")
        self.new_btn.clicked.connect(self.start_snip)
        self.new_btn.setObjectName("newButton")

        # Mode dropdown
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(["Rectangle mode", "Free-form mode", "Fullscreen"])
        self.mode_dropdown.setObjectName("toolbarDropdown")

        # Delay dropdown
        self.delay_dropdown = QComboBox()
        self.delay_dropdown.addItems(["No delay", "3 sec", "5 sec"])
        self.delay_dropdown.setObjectName("toolbarDropdown")

        # Ellipsis placeholder
        self.more_btn = QPushButton("⋯")
        self.more_btn.setFixedWidth(40)
        self.more_btn.setObjectName("iconButton")

        toolbar_layout.addWidget(self.new_btn)
        toolbar_layout.addSpacing(15)
        toolbar_layout.addWidget(self.mode_dropdown)
        toolbar_layout.addSpacing(15)
        toolbar_layout.addWidget(self.delay_dropdown)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.more_btn)

        # --- Center message ---
        self.center_label = QLabel(
            'Press <span style="color:#ffffff;font-weight:bold;">Windows logo key + Shift + S</span> to start a snip.'
        )
        self.center_label.setAlignment(Qt.AlignCenter)

        # Layout assembly
        main_layout.addWidget(toolbar)
        main_layout.addStretch()
        main_layout.addWidget(self.center_label)
        main_layout.addStretch()

        self.setCentralWidget(main_widget)

    def start_snip(self):
        mode = self.mode_dropdown.currentText()
        delay = self.delay_dropdown.currentIndex() * 3  # 0, 3, 5
        self.hide()

        if "Rectangle" in mode:
            self.rect_snip = RectangleSnipOverlay(delay)
            self.rect_snip.snip_completed.connect(self.show_preview)
        elif "Free-form" in mode:
            self.freeform_snip = FreeformSnipOverlay(delay)
            self.freeform_snip.snip_completed.connect(self.show_preview)
        elif "Fullscreen" in mode:
            QTimer.singleShot(delay * 1000, self.capture_fullscreen)
        else:
            QMessageBox.information(self, "Coming Soon", f"{mode} not implemented.")
            self.show()

    def capture_fullscreen(self):
        screenshot = pyautogui.screenshot()
        self.show_preview(screenshot)

    def show_preview(self, image):
        preview = ImagePreviewDialog(image, self)
        preview.exec_()
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #202020;
        }
        #newButton {
            background-color: #3a3a3a;
            border: 1px solid #444;
            border-radius: 4px;
            padding: 6px 14px;
            font-size: 13px;
            color: #ffffff;
        }
        #newButton:hover {
            background-color: #505050;
        }
        #toolbarDropdown {
            background-color: #2b2b2b;
            border: 1px solid #444;
            border-radius: 4px;
            padding: 4px 10px;
            min-width: 140px;
            color: #ffffff;
            font-size: 13px;
        }
        #toolbarDropdown::drop-down {
            border: none;
            width: 18px;
        }
        #iconButton {
            background-color: transparent;
            border: none;
            font-size: 18px;
            color: #ffffff;
            padding: 4px 8px;
        }
        #iconButton:hover {
            background-color: #404040;
        }
        QLabel {
            font-size: 14px;
            color: #bbbbbb;
        }
    """)


    win = SnippingToolGUI()
    win.show()
    sys.exit(app.exec_())
