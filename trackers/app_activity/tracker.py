import time
from pynput import mouse, keyboard
from trackers.base import BaseTracker
from models.app_activity import AppActivity
import threading
from collections import deque, Counter
import platform
from constants import  CACHE_FLUSH_INTERVAL, DB_FLUSH_INTERVAL, ACTIVITY_TIMEOUT,  THRESHOLD_ACTIVATION, THRESHOLD_SUSPICIOUS_TIME, PATTERN_WINDOW, THRESHOLD_LONG_PRESS
from events.stop_timer import StopTimer

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
        self.last_keys = deque(maxlen=PATTERN_WINDOW)
        self.last_key_times = deque(maxlen=PATTERN_WINDOW)
        self.mouse_positions = deque(maxlen=PATTERN_WINDOW)
        
        self.held_keys = {}
        self.held_key_start = {}

        self.suspicious_start_time = None
        self.suspicious_active_type = None  # "keyboard", "mouse", etc.
        

    def log_suspicious_activity(self, activity_type, start_time, end_time):
        duration = round(end_time - start_time, 2)
        print(f"[LOGGED] Suspicious {activity_type} activity from {start_time} to {end_time} ({duration} seconds)")

    def reset_suspicion(self):
        self.suspicious_start_time = None
        self.suspicious_active_type = None
        stop_timer_event = StopTimer()
        stop_timer_event.dispatch()

    def detect_patterns(self):
        now = time.time()
        pattern_detected = None
        
        
        # Pattern 3: Static mouse
        if not pattern_detected and len(self.mouse_positions) >= 10:
            if len(set(self.mouse_positions)) == 1:
                pattern_detected = "static_mouse"
                return pattern_detected

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

       

        return pattern_detected

    def update(self, key=None, x=None, y=None):
        now = time.time()

        if key is not None:
            self.last_keys.append(str(key))
            self.last_key_times.append(now)

        if x is not None and y is not None:
            self.mouse_positions.append((x, y))

        detected_pattern = self.detect_patterns()

        if detected_pattern:
            if not self.suspicious_start_time:
                self.suspicious_start_time = now
                self.suspicious_active_type = detected_pattern
                print("Suspicious activity detected: Observing for next 30 secs for continue")
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
        def on_mouse_move(x, y): 
            self.on_activity()
            self.update(x=x, y=y)
        def on_click(x, y, button, pressed): 
            self.on_activity()
            self.update(x=x, y=y)
        def on_scroll(x, y, dx, dy):
            self.on_activity()
            self.update(x=dx, y=dy)

        def on_key_press(key):
            self.on_activity()
            self.update(key=key)
            
            key_str = str(key)
            now = time.time()

            # Store when the key was first pressed
            if key_str not in self.held_keys:
                self.held_keys[key_str] = True
                self.held_key_start[key_str] = now

        def on_key_release(key):
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
        

    def run(self):
        self.dump_cache_to_db()
        self.evaluate()
        thread = threading.Thread(target=self.app_switch_observer)
        thread.daemon = True 
        thread.start()
        current_time = time.time()
        last_cache_time = current_time
        last_flush_time = current_time
        now = time.time()
        self.keep_running = True
            
        while self.keep_running:
            time.sleep(1)  # reduce CPU usage

            if time.time() - last_cache_time >= CACHE_FLUSH_INTERVAL:
                self.write_to_cache()
                last_cache_time = time.time()
                
            for key_str in self.held_keys:
                start_time = self.held_key_start.get(key_str, now)
                held_duration = now - start_time
                if held_duration > THRESHOLD_ACTIVATION:  # e.g., 5 seconds
                    print(f"{key_str} is pressed for {held_duration} secs")
            

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

