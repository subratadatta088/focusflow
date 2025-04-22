from PyQt5.QtCore import QObject, pyqtSignal

class StopTimer(QObject):
    execute = pyqtSignal(str) # Signal to send data
    
    def dispatch(self):
        self.execute.emit("stop") 
        print("dispatched event: stop timer")                     