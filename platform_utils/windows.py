
import win32gui
import win32process
import psutil

def get_focused_app():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        return process.name().lower()
    except Exception as e:
        print(f"[Windows] Focused app error: {e}")
        return None