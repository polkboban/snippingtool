# main.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

from snip_modes.rectangle_snip import RectangleSnipOverlay


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
        else:
            QMessageBox.information(self, "Coming Soon", f"{mode} is not implemented yet.")
            self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = SnippingToolGUI()
    win.show()
    sys.exit(app.exec_())
