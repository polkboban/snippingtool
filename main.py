# main.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QComboBox
)
from snip_modes.rectangle_snip import RectangleSnipOverlay


class SnippingToolLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snipping Tool Clone")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.mode_label = QLabel("Snip Mode:")
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(["Rectangle", "Free-form (coming soon)"])

        self.delay_label = QLabel("Delay (seconds):")
        self.delay_dropdown = QComboBox()
        self.delay_dropdown.addItems(["0", "3", "5"])

        self.start_btn = QPushButton("Start Snip")
        self.start_btn.clicked.connect(self.start_snip)

        layout.addWidget(self.mode_label)
        layout.addWidget(self.mode_dropdown)
        layout.addWidget(self.delay_label)
        layout.addWidget(self.delay_dropdown)
        layout.addWidget(self.start_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_snip(self):
        mode = self.mode_dropdown.currentText()
        delay = int(self.delay_dropdown.currentText())
        self.hide()

        if mode == "Rectangle":
            self.rect_snip = RectangleSnipOverlay(delay)
        elif mode == "Free-form (coming soon)":
            print("Free-form snip not implemented yet")
        else:
            print("Unknown mode")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SnippingToolLauncher()
    window.show()
    sys.exit(app.exec_())
