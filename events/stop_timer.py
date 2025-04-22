from PyQt5.QtCore import QObject, pyqtSignal

class StopTimer(QObject):
    execute = pyqtSignal(str)

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            QObject.__init__(cls._instance)  # ✅ Init QObject
        return cls._instance

    def dispatch(self):
        print("[EVENT] Dispatching stop event")
        self.execute.emit("stop")


stop_timer_singleton = StopTimer()