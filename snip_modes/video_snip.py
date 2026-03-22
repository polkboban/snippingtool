import cv2
import numpy as np
import mss
import time
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal, QThread, QTimer, QByteArray
from PyQt6.QtGui import QPainter, QColor, QPen, QIcon, QPixmap
from PyQt6.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtSvg import QSvgRenderer

class VideoRecorderThread(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, rect, filename="capture.mp4", fps=20):
        super().__init__()
        self.rect = rect
        self.filename = filename
        self.fps = fps
        self.running = True
        self.paused = False
        
    def run(self):
        with mss.mss() as sct:
            monitor = {"top": self.rect.y(), "left": self.rect.x(), "width": self.rect.width(), "height": self.rect.height()}
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(self.filename, fourcc, self.fps, (self.rect.width(), self.rect.height()))
            
            while self.running:
                start_time = time.time()
                
                if not self.paused:
                    img = np.array(sct.grab(monitor))
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    out.write(frame)
                
                elapsed = time.time() - start_time
                sleep_time = max(1./self.fps - elapsed, 0.001)
                time.sleep(sleep_time)
                
            out.release()
            self.finished.emit(self.filename)
            
    def stop(self):
        self.running = False
        
    def toggle_pause(self):
        self.paused = not self.paused
        return self.paused

class VideoSnipOverlay(QWidget):
    recording_completed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.begin = QPoint()
        self.end = QPoint()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        if not self.begin.isNull() and not self.end.isNull():
            pen = QPen(QColor(255, 0, 0), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QColor(0, 0, 0, 0)) 
            
            rect = QRect(self.begin, self.end).normalized()
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(rect, Qt.GlobalColor.transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        self.begin = event.position().toPoint()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.position().toPoint()
        self.hide()

        rect = QRect(self.begin, self.end).normalized()

        if rect.width() > 10 and rect.height() > 10:
            self.start_recording(rect)
        else:
            self.recording_completed.emit("")
            self.close()

    def create_svg_icon(self, path_data, color="#ffffff", view_box="0 0 24 24"):
        svg = f'<svg viewBox="{view_box}" xmlns="http://www.w3.org/2000/svg"><path fill="{color}" d="{path_data}"/></svg>'
        renderer = QSvgRenderer(QByteArray(svg.encode('utf-8')))
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)

    def start_recording(self, rect):
        import os
        
        dpr = self.devicePixelRatioF()
        physical_rect = QRect(
            int(rect.x() * dpr),
            int(rect.y() * dpr),
            int(rect.width() * dpr),
            int(rect.height() * dpr)
        )
        save_path = os.path.join(os.path.expanduser("~"), "Desktop", "snip_recording.mp4")
        
        self.thread = VideoRecorderThread(physical_rect, filename=save_path)
        self.thread.finished.connect(self.on_recording_finished)
        self.thread.start()

        self.stop_window = QWidget()
        self.stop_window.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.stop_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        frame = QFrame(self.stop_window)
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 30, 240);
                border: 1px solid rgba(255, 255, 255, 20);
                border-radius: 20px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        frame.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 6, 10, 6)
        layout.setSpacing(12)

        self.is_collapsed = False

        # 2. Perfect circle for the recording dot (Now a toggle button!)
        self.dot = QPushButton()
        self.dot.setFixedSize(14, 14)
        self.dot.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dot.setStyleSheet("background-color: #ff4444; border-radius: 7px; border: none;")
        self.dot.setToolTip("Collapse / Expand")
        self.dot.clicked.connect(self.toggle_collapse)
        layout.addWidget(self.dot)

        # 3. Live timer
        self.time_label = QLabel("00:00")
        self.time_label.setStyleSheet("color: white; font-size: 14px; font-weight: 600; font-family: 'Segoe UI Variable', sans-serif;")
        self.time_label.setMinimumWidth(45) 
        layout.addWidget(self.time_label)

        # 4. Control Buttons
        btn_style = """
            QPushButton { background-color: transparent; border: none; border-radius: 14px; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 30); }
            QPushButton:pressed { background-color: rgba(255, 255, 255, 50); }
        """
        
        self.pause_path = "M6 19h4V5H6v14zm8-14v14h4V5h-4z"
        self.play_path = "M8 5v14l11-7z"
        self.stop_path = "M6 6h12v12H6z"

        self.pause_btn = QPushButton()
        self.pause_btn.setFixedSize(28, 28)
        self.pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pause_btn.setStyleSheet(btn_style)
        self.pause_btn.setIcon(self.create_svg_icon(self.pause_path))
        self.pause_btn.clicked.connect(self.toggle_pause)
        layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton()
        self.stop_btn.setFixedSize(28, 28)
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.setStyleSheet(btn_style.replace("rgba(255, 255, 255, 30)", "rgba(232, 17, 35, 200)"))
        self.stop_btn.setIcon(self.create_svg_icon(self.stop_path, "#ff4444"))
        self.stop_btn.clicked.connect(self.stop_recording)
        layout.addWidget(self.stop_btn)

        main_layout = QVBoxLayout(self.stop_window)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(frame)

        self.stop_window.adjustSize()

        self.record_time = 0
        self.timer = QTimer(self.stop_window)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        toolbar_width = self.stop_window.width()
        toolbar_height = self.stop_window.height()

        x = rect.center().x() - (toolbar_width // 2)
        y = rect.top() - toolbar_height - 10
        if y < 0: y = rect.top() + 10

        self.stop_window.move(x, y)
        self.stop_window.show()

    def update_timer(self):
        if self.thread.paused:
            return 
            
        self.record_time += 1
        mins = self.record_time // 60
        secs = self.record_time % 60
        self.time_label.setText(f"{mins:02d}:{secs:02d}")

        if self.record_time % 2 == 0:
            self.dot.setStyleSheet("background-color: #ff4444; border-radius: 7px; border: none;")
        else:
            self.dot.setStyleSheet("background-color: rgba(255, 68, 68, 60); border-radius: 7px; border: none;")

    def toggle_pause(self):
        is_paused = self.thread.toggle_pause()
        if is_paused:
            self.pause_btn.setIcon(self.create_svg_icon(self.play_path))
            self.dot.setStyleSheet("background-color: #ffcc00; border-radius: 7px; border: none;") 
        else:
            self.pause_btn.setIcon(self.create_svg_icon(self.pause_path))
            self.dot.setStyleSheet("background-color: #ff4444; border-radius: 7px; border: none;")

    def toggle_collapse(self):
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.time_label.hide()
            self.pause_btn.hide()
            self.stop_btn.hide()
        else:
            self.time_label.show()
            self.pause_btn.show()
            self.stop_btn.show()
            
        self.stop_window.adjustSize()

    def stop_recording(self):
        self.timer.stop()
        self.stop_window.close()
        self.thread.stop()

    def on_recording_finished(self, filename):
        self.recording_completed.emit(filename)
        self.close()