import time
from pynput import mouse, keyboard
from trackers.base import BaseTracker
from models.app_activity import AppActivity
import threading
from collections import deque, Counter
import platform
from constants import  CACHE_INTERVAL,CACHE_FLUSH_INTERVAL, DB_FLUSH_INTERVAL, ACTIVITY_TIMEOUT,  THRESHOLD_ACTIVATION, THRESHOLD_SUSPICIOUS_TIME, PATTERN_WINDOW, THRESHOLD_LONG_PRESS
from events.stop_timer import stop_timer_singleton

class ActivityTracker(BaseTracker):
    def __init__(self):
        super().__init__()
        self.app_dict = {}
        self.dir = "trackers/app_activity/"
        self.last_cache_flush = time.time()
        self.last_db_flush = time.time()
        self.platform = platform.system().lower()
        self.keep_running = False
        self.active_app = None
        self.last_activity_time = time.time()
        self.model = AppActivity
       
        # for suspicious activities
        self.last_keys = deque(maxlen=PATTERN_WINDOW)
        self.last_key_times = deque(maxlen=PATTERN_WINDOW)
        self.mouse_positions = deque(maxlen=PATTERN_WINDOW)
        
        self.held_keys = {}
        self.held_key_start = {}

        self.suspicious_start_time = None
        self.suspicious_active_type = None  # "keyboard", "mouse", etc.
        
        self.stop_event = stop_timer_singleton
        print("[DEBUG] StopTimer instance(ActivityTracker):", id(self.stop_event))
        
        def on_mouse_move(x, y): 
            if self.keep_running:
                self.on_activity()
                self.update(x=x, y=y)
                if x is not None and y is not None:
                    self.mouse_positions.append((x, y))
        def on_click(x, y, button, pressed): 
            if self.keep_running:
                self.on_activity()
                if x is not None and y is not None:
                    self.mouse_positions.append((x, y))
        def on_scroll(x, y, dx, dy):
            if self.keep_running:
                self.on_activity()
                self.update()
                self.mouse_positions = []

        def on_key_press(key):
            if self.keep_running:
                self.on_activity()
                self.update(key=key)
                
                key_str = str(key)
                now = time.time()

                # Store when the key was first pressed
                if key_str not in self.held_keys:
                    self.held_keys[key_str] = True
                    self.held_key_start[key_str] = now

        def on_key_release(key):
            if self.keep_running:
                key_str = str(key)
                now = time.time()

                if key_str in self.held_keys:
                    start_time = self.held_key_start.get(key_str, now)
                    held_duration = now - start_time

                    # Clean up
                    del self.held_keys[key_str]
                    del self.held_key_start[key_str]

                    if held_duration > THRESHOLD_LONG_PRESS:  # e.g., 30 seconds
                        self.log_suspicious_activity("long_key_hold", start_time, now)
                        self.reset_suspicion()
        
        mouse_listener = mouse.Listener(on_move=on_mouse_move, on_click=on_click, on_scroll=on_scroll)
        keyboard_listener = keyboard.Listener(on_press=on_key_press, on_key_release = on_key_release)

        mouse_listener.start()
        keyboard_listener.start()
            
        
    def log_suspicious_activity(self, activity_type, start_time, end_time):
        duration = round(end_time - start_time, 2)
        print(f"[LOGGED] Suspicious {activity_type} activity from {start_time} to {end_time} ({duration} seconds)")
        print("[DEBUG] StopTimer instance(ActivityTracker):", id(self.stop_event))
        self.stop_event.execute.emit("pause")

    def reset_suspicion(self):
        self.suspicious_start_time = None
        self.suspicious_active_type = None
       

    def detect_patterns(self):
        now = time.time()
        pattern_detected = None
        
        
       
        # Pattern 1: Repeated key
        if self.last_keys:
            key_counts = Counter(self.last_keys)
            for k, count in key_counts.items():
                if count > 20:
                    pattern_detected = "repeated_key_"+str(k)
                    return pattern_detected

        # Pattern 2: Regular interval typing
        if not pattern_detected and len(self.last_key_times) >= 10:
            intervals = [self.last_key_times[i + 1] - self.last_key_times[i] for i in range(len(self.last_key_times) - 1)]
            if max(intervals) - min(intervals) < 0.2:  # Very regular
                pattern_detected = "regular_key_intervals"
                return
            
        # Pattern 3: Static mouse
        if not pattern_detected and len(self.mouse_positions) >= 10:
            if len(set(self.mouse_positions)) == 1:
                pattern_detected = "static_mouse"
                return pattern_detected

       

        return pattern_detected

    def update(self, key=None, x=None, y=None):
        if self.keep_running:
            now = time.time()

            if key is not None:
                self.last_keys.append(str(key))
                self.last_key_times.append(now)

           

            detected_pattern = self.detect_patterns()

            if detected_pattern:
                if not self.suspicious_start_time:
                    self.suspicious_start_time = now
                    self.suspicious_active_type = detected_pattern
                    print(f"Suspicious activity detected: {detected_pattern} Observing for next 30 secs for continue")
                else:
                    active_duration = now - self.suspicious_start_time
                    if active_duration > THRESHOLD_SUSPICIOUS_TIME:
                        self.log_suspicious_activity(self.suspicious_active_type, self.suspicious_start_time, now)
                        self.reset_suspicion()
            else:
                # Pattern broke before activation — reset if timer was running but not yet active
                if self.suspicious_start_time and (now - self.suspicious_start_time < THRESHOLD_ACTIVATION):
                    self.reset_suspicion()
                
                
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
        pass
        

    def run(self):
        self.dump_cache_to_db()
         # Start listeners in a dedicated thread
        eval_thread = threading.Thread(target=self.evaluate)
        eval_thread.daemon = True
        eval_thread.start()
      
        current_time = time.time()
        last_cache_time = current_time
        last_flush_time = current_time
        now = time.time()
        self.keep_running = True
            
        while self.keep_running:
            time.sleep(CACHE_INTERVAL)  # reduce CPU usage
            
            print(f"[🧠] Activity Data: {self.app_dict}")
            
            if self.active_app != self.get_active_app():
                print("Active app changed. Switching...")
                self.active_app = self.get_active_app()

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
        
