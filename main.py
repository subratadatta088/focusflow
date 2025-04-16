
from trackers.app_usage.tracker import AppUsageTracker
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import QObject, QTimer, Qt, pyqtSignal, QThread

import sys

class FocusWorker(QObject):
    finished = pyqtSignal()
    update = pyqtSignal(dict)

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    def run(self):
        self.ctx.run()
        pass

    def stop(self):
        self.ctx.stop()
        
class FocusTimer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FocusFlow")
        self.setFixedSize(250, 180)

        self.seconds = 0
        self.timer_running = False

        self.label = QLabel("00:00:00", self)
        self.label.setStyleSheet("font-size: 48px;color:#bc9272")
        self.label.setAlignment(Qt.AlignCenter)

        # Timer buttons
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_timer)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.pause_timer)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_timer)


        # Layouts
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.stop_btn)


        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.seconds = 0
        self.timer_running = False
        
        self.app_usage_context = AppUsageTracker()

        self.start_btn.clicked.connect(self.start_timer)
        self.pause_btn.clicked.connect(self.pause_timer)
        self.stop_btn.clicked.connect(self.stop_timer)
        
        self.worker_thread = QThread()
        self.worker = FocusWorker(self.app_usage_context)

        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)

    def update_timer(self):
        self.seconds += 1
        hours, remainder = divmod(self.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")

        # Here you can call your focus eval logic every X seconds
        if self.seconds % 3 == 0:  # for example every 3 seconds
            print("Running evalEngine()...")
            # evalEngine()

    def start_timer(self):
        if not self.timer_running:
            self.timer.start(1000)
            self.timer_running = True
            self.worker_thread.start()
            # self.app_usage_context.run()
            

    def pause_timer(self):
        if self.timer_running:
            self.timer.stop()
            self.timer_running = False
            self.worker.stop()
            # self.app_usage_context.stop()

    def stop_timer(self):
        self.pause_timer()
        print(f"Total Focused Time: {self.label.text()}")
        # Save data, export to JSON, etc.
        self.seconds = 0
        self.label.setText("00:00:00")
        self.worker.stop()
        # self.app_usage_context.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FocusTimer()
    window.show()
    sys.exit(app.exec_())
