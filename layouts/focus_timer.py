from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt, QThread
from PyQt5.QtGui import QPainter, QLinearGradient, QColor
from managers.tracker_manager import FocusWorker
from trackers import TRACKER_SERVICES
from typing import List

class FocusTimer(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#81C2E3"))
        gradient.setColorAt(1, QColor("#FFFCCF"))
        painter.fillRect(self.rect(), gradient)

    def __init__(self):
        super().__init__()
        self.trackers: List[FocusWorker] = []
        for service in TRACKER_SERVICES:
            context = service()
            worker = FocusWorker(context)
            self.trackers.append(worker)

        self.setWindowTitle("FocusFlow")
        self.setFixedSize(250, 180)
        self.label = QLabel("00:00:00", self)
        self.label.setStyleSheet("font-size: 48px;color:#02124f")
        self.label.setAlignment(Qt.AlignCenter)

        self.start_btn = QPushButton("Start")
        self.pause_btn = QPushButton("Pause")
        self.stop_btn = QPushButton("Stop")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.stop_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.seconds = 0
        self.timer_running = False
        
        self.start_btn.clicked.connect(self.start_timer)
        self.pause_btn.clicked.connect(self.pause_timer)
        self.stop_btn.clicked.connect(self.stop_timer)

    def update_timer(self):
        self.seconds += 1
        h, r = divmod(self.seconds, 3600)
        m, s = divmod(r, 60)
        self.label.setText(f"{h:02}:{m:02}:{s:02}")

        if self.seconds % 3 == 0:
            print("Running evalEngine()...")

    def start_timer(self):
        if not self.timer_running:
            self.timer.start(1000)
            self.timer_running = True
             
            for worker in self.trackers:
                worker.run()

    def pause_timer(self):
        if self.timer_running:
            self.timer.stop()
            self.timer_running = False
            for worker in self.trackers:
                worker.stop()

    def stop_timer(self):
        self.pause_timer()
        print(f"Total Focused Time: {self.label.text()}")
        self.seconds = 0
        self.label.setText("00:00:00")

