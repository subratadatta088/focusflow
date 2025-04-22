from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

# -------------------------------------
# Worker Wrapper (inherits QObject!)
# -------------------------------------
class FocusWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker
        self._running = True

    @pyqtSlot()
    def run(self):
        print("[FocusWorker] Running tracker")
        self.tracker.run()  # Make sure tracker.run() is blocking and looped properly
        self.finished.emit()

    def stop(self):
        print("[FocusWorker] Stopping tracker")
        self.tracker.stop()
        self._running = False

# -------------------------------------
# Thread + Worker Wrapper
# -------------------------------------
class TrackerWorker:
    def __init__(self, tracker_instance):
        self.worker = FocusWorker(tracker_instance)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)

    def start(self):
        if not self.thread.isRunning():
            self.thread.start()

    def stop(self):
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()


# -------------------------------------
# Manager for Multiple Trackers
# -------------------------------------
class TrackerManager:
    def __init__(self):
        self.trackers = []

    def add_tracker(self, tracker_obj):
        worker = TrackerWorker(tracker_obj)
        self.trackers.append(worker)

    def start_all(self):
        for worker in self.trackers:
            worker.start()

    def stop_all(self):
        for worker in self.trackers:
            worker.stop()
