import time
from pynput import mouse, keyboard
from trackers.base import BaseTracker
from models.app_activity import AppActivity
import threading
from collections import deque, Counter
import platform
from constants import  CACHE_FLUSH_INTERVAL, DB_FLUSH_INTERVAL, ACTIVITY_TIMEOUT,  THRESHOLD_ACTIVATION, THRESHOLD_SUSPICIOUS_TIME

class ActivityTracker(BaseTracker):
    def __init__(self):
        super().__init__()
        self.app_dict = {}
        self.dir = "trackers/app_activity/"
        self.last_cache_flush = time.time()
        self.last_db_flush = time.time()
        self.platform = platform.system().lower()
        self.keep_running = True
        self.active_app = None
        self.last_activity_time = time.time()
        self.model = AppActivity
       
        # for suspicious activities
        self.last_keys = []
        self.last_key_times = []
        self.mouse_positions = []
        self.suspicious_time = 0
        self.suspicious_tag = None
        self.suspicious_start_time = None

    def detect_suspicious_activity(self, key=None, x=None, y=None):
        now = time.time()

        # Track key press activity
        if key:
            self.last_keys.append(str(key))
            self.last_key_times.append(now)

            # If there’s an active suspicious activity timer
            if self.suspicious_start_time and (now - self.suspicious_start_time > THRESHOLD_ACTIVATION):
                # Calculate time delta
                time_delta = now - self.suspicious_start_time
                if time_delta > THRESHOLD_SUSPICIOUS_TIME:
                    self.log_suspicious_activity("key_activity")
            
            # Pattern 1: Repeated key (e.g., hitting 'space' repeatedly)
            key_counts = Counter(self.last_keys)
            for k, count in key_counts.items():
                if count > 20:  # threshold for repeated key activity
                    if not self.suspicious_start_time:
                        self.suspicious_start_time = now  # start the timer
                    self.suspicious_tag = f"repeated_key_{k}"
                    self.suspicious_time += 1

            # Pattern 2: Regular intervals (key press intervals)
            if len(self.last_key_times) >= 10:
                intervals = [self.last_key_times[i + 1] - self.last_key_times[i] for i in range(len(self.last_key_times) - 1)]
                if max(intervals) - min(intervals) < 0.2:  # all nearly same
                    if not self.suspicious_start_time:
                        self.suspicious_start_time = now
                    self.suspicious_tag = "regular_input_pattern"
                    self.suspicious_time += 1
                                                                                                              
        # Track mouse movement activity
        if x is not None and y is not None:
            self.mouse_positions.append((x, y))
            if len(set(self.mouse_positions)) == 1:  # Static mouse detection
                if not self.suspicious_start_time:
                    self.suspicious_start_time = now
                self.suspicious_tag = "static_mouse"
                self.suspicious_time += 1

            # After 5 seconds of activity, check for time delta
            if self.suspicious_start_time and (now - self.suspicious_start_time > THRESHOLD_ACTIVATION):
                time_delta = now - self.suspicious_start_time
                if time_delta > THRESHOLD_SUSPICIOUS_TIME:
                    self.log_suspicious_activity("mouse_activity")

    def log_suspicious_activity(self, activity_type):
        # Log the suspicious activity in the database or a separate table
        print(f"Suspicious activity detected: {activity_type} | Time: {self.suspicious_start_time} | Tag: {self.suspicious_tag}")
        self.suspicious_start_time = None  # Reset timer

    def track_activity(self):
        now = time.time()
        if self.active_app:
            elapsed = now - self.last_activity_time
            if elapsed < ACTIVITY_TIMEOUT:  # only count if it's still "active"
                self.app_dict.setdefault(self.active_app, 0)
                self.app_dict[self.active_app] += int(elapsed)
        self.last_activity_time = now

    def on_activity(self, event=None):
        self.track_activity()
        self.active_app = self.get_active_app()
    

    def evaluate(self):
        def on_mouse_move(x, y): 
            self.on_activity()
            self.detect_suspicious_activity(x=x, y=y)
        def on_click(x, y, button, pressed): 
            self.on_activity()
            self.detect_suspicious_activity(key= "mouse", x=x, y=y)
        def on_scroll(x, y, dx, dy):
            self.on_activity()
            self.detect_suspicious_activity(x=dx, y=dy)
            
        def on_key_press(key): 
            self.on_activity()
            self.detect_suspicious_activity(key=key)
        
        mouse_listener = mouse.Listener(on_move=on_mouse_move, on_click=on_click, on_scroll=on_scroll)
        keyboard_listener = keyboard.Listener(on_press=on_key_press)

        mouse_listener.start()
        keyboard_listener.start()
        

    def run(self):
        self.dump_cache_to_db()
        self.evaluate()
        thread = threading.Thread(target=self.app_switch_observer)
        thread.daemon = True 
        thread.start()
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
            
        else: 
            thread.join()


   
        
    def stop(self):
        self.keep_running = False
        self.write_to_cache()
        self.dump_cache_to_db()
        self.clear_cache()
        
    def app_switch_observer(self):
        while self.keep_running:
            print("[Observer]: Running")
            time.sleep(2)
            print(self.active_app)
            print(self.get_active_app())

            if self.active_app != self.get_active_app():
                print("Active app changed. Switching...")
                self.active_app = self.get_active_app()

        print("[Observer] Worker has stopped, observer finalizing...")
        time.sleep(2)
        print("[Observer]: Stopped")

