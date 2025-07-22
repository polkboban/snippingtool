# main.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt

from io import BytesIO

from PIL import ImageQt
from PyQt5.QtWidgets import QLabel, QDialog, QDialogButtonBox, QFileDialog, QPushButton
from PyQt5.QtGui import QPixmap, QClipboard
from PyQt5.QtWidgets import QVBoxLayout


from snip_modes.rectangle_snip import RectangleSnipOverlay

class ImagePreviewDialog(QDialog):
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preview Snip")
        self.setFixedSize(500, 400)
        self.image = image  # PIL Image

        layout = QVBoxLayout()

        # Convert PIL image to QPixmap using BytesIO
        label = QLabel()
        buffer = BytesIO()
        self.image.save(buffer, format='PNG')
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())

        label.setPixmap(pixmap.scaled(480, 320, Qt.KeepAspectRatio))
        layout.addWidget(label)

        # Buttons: Save | Cancel | Copy
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        copy_btn = QPushButton("📋 Copy")
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
        # Copy to clipboard using QPixmap
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
        self.setFixedSize(400, 200)

        # Layouts
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        toolbar_layout = QHBoxLayout()

        # --- Toolbar buttons ---
        # New Snip
        self.new_btn = QPushButton("🆕  New")
        self.new_btn.clicked.connect(self.start_snip)
        self.new_btn.setFixedHeight(40)

        # Mode
        self.mode_label = QLabel("Mode:")
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(["Rectangle", "Free-form (coming soon)", "Fullscreen (coming soon)"])

        # Delay
        self.delay_label = QLabel("Delay:")
        self.delay_dropdown = QComboBox()
        self.delay_dropdown.addItems(["0", "3", "5"])

        # Add to toolbar layout
        toolbar_layout.addWidget(self.new_btn)
        toolbar_layout.addSpacing(20)
        toolbar_layout.addWidget(self.mode_label)
        toolbar_layout.addWidget(self.mode_dropdown)
        toolbar_layout.addSpacing(20)
        toolbar_layout.addWidget(self.delay_label)
        toolbar_layout.addWidget(self.delay_dropdown)

        # Assemble UI
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
        else:
            QMessageBox.information(self, "Coming Soon", f"{mode} is not implemented yet.")
            self.show()

    def show_preview(self, image):
        preview = ImagePreviewDialog(image, self)
        preview.exec_()
        self.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = SnippingToolGUI()
    win.show()
    sys.exit(app.exec_())



