import cv2
import numpy as np
import mss
import time
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal, QThread
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout

class VideoRecorderThread(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, rect, filename="capture.mp4", fps=20):
        super().__init__()
        self.rect = rect
        self.filename = filename
        self.fps = fps
        self.running = True
        
    def run(self):
        with mss.mss() as sct:
            # Setup monitor dict for mss
            monitor = {"top": self.rect.y(), "left": self.rect.x(), "width": self.rect.width(), "height": self.rect.height()}
            
            # Setup OpenCV Video Writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(self.filename, fourcc, self.fps, (self.rect.width(), self.rect.height()))
            
            while self.running:
                start_time = time.time()
                
                # Grab frame
                img = np.array(sct.grab(monitor))
                
                # Convert BGRA (mss format) to BGR (opencv format)
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                out.write(frame)
                
                # Lock FPS to prevent sped-up/slowed-down video
                elapsed = time.time() - start_time
                sleep_time = max(1./self.fps - elapsed, 0)
                time.sleep(sleep_time)
                
            out.release()
            self.finished.emit(self.filename)
            
    def stop(self):
        self.running = False

class VideoSnipOverlay(QWidget):
    recording_completed = pyqtSignal(str) # Emits the filepath of the video

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
            painter.setBrush(QColor(0, 0, 0, 0)) # Clear the inside
            
            rect = QRect(self.begin, self.end).normalized()
            # "Cut out" the dark overlay inside the rectangle so the user can see what they are recording
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

    def start_recording(self, rect):
        import os
        save_path = os.path.join(os.path.expanduser("~"), "Desktop", "snip_recording.mp4")
        self.thread = VideoRecorderThread(rect, filename=save_path)
        self.thread.finished.connect(self.on_recording_finished)
        self.thread.start()

        self.stop_window = QWidget()
        self.stop_window.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        
        # Make the background translucent using RGBA
        self.stop_window.setStyleSheet("background-color: rgba(30, 30, 30, 200); border-radius: 8px; border: 1px solid rgba(255, 68, 68, 200);")
        layout = QVBoxLayout(self.stop_window)
        
        stop_btn = QPushButton("⏹ Stop Recording")
        stop_btn.setStyleSheet("color: white; font-weight: bold; padding: 10px 20px; background: transparent; border: none;")
        stop_btn.clicked.connect(self.stop_recording)
        
        layout.addWidget(stop_btn)
        
        # Position it firmly in the top-right corner of the screen
        screen_geom = QApplication.primaryScreen().availableGeometry()
        # Assume the button is roughly 160px wide, place it 50px from the edges
        self.stop_window.move(screen_geom.right() - 160 - 50, screen_geom.top() + 50)
        self.stop_window.show()

    def stop_recording(self):
        self.stop_window.close()
        self.thread.stop()

    def on_recording_finished(self, filename):
        self.recording_completed.emit(filename)
        self.close()