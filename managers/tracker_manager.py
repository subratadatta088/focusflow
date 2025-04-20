from PyQt5.QtCore import QThread, QObject
from multiprocessing import Process

# -------------------------------------
# Worker wrapper (inherits QObject!)
# -------------------------------------
class FocusWorker(QObject):
    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker
        self.p = Process(target = tracker.run)
        self.p.daemon = True
        

    def run(self):
        self.p.start()

    def stop(self):
        self.tracker.stop()
        self.p.terminate()
        
        
class TrackerWorker:
    def __init__(self, tracker_instance):
        tracker = FocusWorker(tracker_instance)
        thread = QThread()
        tracker.moveToThread(self.thread)
        thread.started.connect(self.tracker.run)

    def start(self):
        if not self.thread.isRunning():
            self.thread.start()

    def stop(self):
        if self.thread.isRunning():
            self.tracker.stop()
            self.thread.quit()
            self.thread.wait()

class TrackerManager:
    def __init__(self):
        self.trackers = []

    def add_tracker(self, tracker_obj):
        worker = TrackerWorker(tracker_obj)
        self.trackers.append(worker)

    def start_all(self):
        for tracker,thread in self.trackers:
            thread.start()

    def stop_all(self):
       for tracker,thread in self.trackers:
            thread.stop()