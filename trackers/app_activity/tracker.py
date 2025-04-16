import time
from pynput import mouse, keyboard
from trackers.base import BaseTracker
from models.app_activity import AppActivity
import threading
import platform
from constants import  CACHE_FLUSH_INTERVAL, DB_FLUSH_INTERVAL, ACTIVITY_TIMEOUT

class ActivityTracker(BaseTracker):
    def __init__(self):
        super().__init__()
        self.app_dict = {}
        self.dir = "trackers/app_activity/"
        self.last_cache_flush = time.time()
        self.last_db_flush = time.time()
        self.lock = threading.Lock()
        self.platform = platform.system().lower()
        self.keep_running = True
        self.active_app = None
        self.last_activity_time = time.time()
        self.model = AppActivity

    def track_activity(self):
        now = time.time()
        if self.active_app:
            elapsed = now - self.last_activity_time
            if elapsed < ACTIVITY_TIMEOUT:  # only count if it's still "active"
                self.app_dict.setdefault(self.active_app, 0)
                self.app_dict[self.active_app] += elapsed
        self.last_activity_time = now

    def on_activity(self, event=None):
        self.track_activity()
        self.active_app = self.get_active_app()
    

    def listen_to_input(self):
        
        def on_mouse_move(x, y): self.on_activity()
        def on_click(x, y, button, pressed): self.on_activity()
        def on_scroll(x, y, dx, dy): self.on_activity()
        def on_key_press(key): self.on_activity()
        
        mouse_listener = mouse.Listener(on_move=on_mouse_move, on_click=on_click, on_scroll=on_scroll)
        keyboard_listener = keyboard.Listener(on_press=on_key_press)

        mouse_listener.start()
        keyboard_listener.start()
        

    def run(self):
        self.dump_cache_to_db()
        self.listen_to_input()
        
        current_time = time.time()
        last_cache_time = current_time
        last_flush_time = current_time

        self.keep_running = True

        while self.keep_running:
            time.sleep(1)  # reduce CPU usage

            if time.time() - last_cache_time >= CACHE_FLUSH_INTERVAL:
                self.write_to_cache()
                last_cache_time = time.time()

            if time.time() - last_flush_time >= DB_FLUSH_INTERVAL:
                self.flush_to_db()
                self.clear_cache()
                self.app_dict = {}
                last_flush_time = time.time()

    def stop(self):
        self.keep_running = False
        self.write_to_cache()
        self.dump_cache_to_db()
        self.clear_cache()
