
from PyQt5.QtWidgets import QApplication
from layouts.focus_timer import FocusTimer
import sys
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FocusTimer()
    window.show()
    sys.exit(app.exec_())
