from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSlot
from PyQt5.QtGui import QPainter, QLinearGradient, QColor
from managers.tracker_manager import TrackerManager
from trackers import TRACKER_SERVICES
from events.stop_timer import stop_timer_singleton
from typing import List
from datetime import datetime
from models.timer_session import TimerSession


class FocusTimer(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#81C2E3"))
        gradient.setColorAt(1, QColor("#FFFCCF"))
        painter.fillRect(self.rect(), gradient)

    def __init__(self):
        super().__init__()
        self.tracker_manager = TrackerManager()
        for tracker in TRACKER_SERVICES:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
            context = tracker()                                      
            self.tracker_manager.add_tracker(context)
                                                                                                                                    


        print("[TIMER] Connecting stop timer signal...")
        print("[DEBUG] StopTimer instance(FocusTimer):", id(stop_timer_singleton))
        try:
            stop_timer_singleton.execute.connect(self.pause_timer_from_event)
            print("[TIMER] Connected StopTimer signal to pause_timer_from_event")
        except Exception as e:
            print("[TIMER] Connection failed:", e)
        
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
        
        self.last_updated = datetime.now()
        self.start_time = datetime.now()
        self.paused_time_total = 0
        self.pause_start_time = None
        self.is_paused = False

        self.update_button_states()
        
    def update_timer(self):
        if self.is_paused:
            return  # Skip update if paused

        now = datetime.now()

        inactivity = (now - self.last_updated).total_seconds()
        if inactivity > 5:
            print(f"Detected long inactivity: {inactivity} seconds")

        self.last_updated = now

        elapsed = (now - self.start_time if self.start_time is not None else 0).total_seconds() - self.paused_time_total

        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)

        self.label.setText(f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}")
        
        #checking for signals

    def update_button_states(self):
        self.start_btn.setEnabled(not self.timer_running or self.is_paused)
        self.pause_btn.setEnabled(self.timer_running and not self.is_paused)
        self.stop_btn.setEnabled(self.timer_running or self.is_paused)

    def resume_timer(self):
        paused_duration = (datetime.now() - self.pause_start_time).total_seconds()
        self.paused_time_total += paused_duration
        self.pause_start_time = None
        self.is_paused = False
        self.last_updated = datetime.now()  # reset to avoid false "inactivity"
        print("Timer resumed.")

    def start_timer(self):
        if not self.timer_running:
            self.timer.start(1000)
            self.timer_running = True
            self.start_time = datetime.now()
            if self.is_paused:
                self.resume_timer()
            self.tracker_manager.start_all()
            self.update_button_states()

    @pyqtSlot(str)
    def pause_timer_from_event(self,msg):
        print("stop event recived!" + msg)
        QMessageBox.warning(self, "Timer Paused", "Suspicious activity detected!")
        self.pause_timer()
        
        
    def pause_timer(self):
        if self.timer_running:
            self.timer.stop()
            self.timer_running = False
            if not self.is_paused:
                self.pause_start_time = datetime.now()
                self.is_paused = True
                print("Timer paused.")
            self.tracker_manager.stop_all()
            self.update_button_states()

    def stop_timer(self):
        self.pause_timer()
        print(f"Total Focused Time: {self.label.text()}")
        self.seconds = 0
        end_time = datetime.now()
        total_tracked_time = (end_time - self.start_time).total_seconds() - self.paused_time_total
        session = TimerSession.create(
            start_time=self.start_time,
            end_time=end_time,
            active_duration=int(total_tracked_time),
            date=self.start_time.date().isoformat()
        )
        if session:
            self.start_time = None
            self.paused_time_total = 0
            self.timer_running = False
            self.is_paused = False
            print("Session added to database")
        
        self.update_button_states()
        self.label.setText("00:00:00")

                                                                                                                                                                                                                                                                              