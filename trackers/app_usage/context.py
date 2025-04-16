import time
from datetime import datetime
from rules.base import EvalType
from models.app_usage import AppUsage
import psutil
import threading
import json
import os
import platform
from constants import IMPORTANT_APPS, CACHE_FILE ,CACHE_INTERVAL, CACHE_FLUSH_INTERVAL, DB_FLUSH_INTERVAL

 

class AppUsageTracker(EvalType):
    def __init__(self):
        self.cache = []
        self.last_cache_flush = time.time()
        self.last_db_flush = time.time()
        self.lock = threading.Lock()
        self.platform = platform.system().lower()
        self.keep_running = True
        self.app_dict = {}
        self.dir = "trackers/app_usage/"
        
    # Getting the focused app.
    def get_active_app(self):
        if self.platform == "darwin":
            from .platform_utils.mac import get_focused_app as get_focused_app_mac
            return get_focused_app_mac()
        elif self.platform == "windows":
            from .platform_utils.windows import get_focused_app as get_focused_app_win
            return get_focused_app_win()
        else:
            raise NotImplementedError("Focused app detection not supported on this OS yet.")
        
    def get_running_apps(self):
        apps = set()
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name']
                if name:
                    apps.add(name.lower())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return list(apps)
        
    def evaluate(self):
        active_app = self.get_active_app()
        running_apps = self.get_running_apps()
        
        # Keep only important apps
        important_running_apps = list(set(running_apps) & set(IMPORTANT_APPS))
        
        # Include active app explicitly if not in important_running_apps
        if active_app and active_app not in important_running_apps:
            important_running_apps.append(active_app)
        
        for app in important_running_apps:
            if app not in self.app_dict:
                self.app_dict[app] = {"focused": 0, "background": 0}

            if app == active_app:
                self.app_dict[app]["focused"] += CACHE_INTERVAL
            else:
                self.app_dict[app]["background"] += CACHE_INTERVAL
        
        # Dev log
        print(f"[{time.strftime('%H:%M:%S')}] Active: {active_app} | Dict: {self.app_dict}")

    def write_to_cache(self):
        with open(self.dir + CACHE_FILE, "w") as f:
            json.dump(self.app_dict, f, indent=4)
             # Dev log
            print(f"Data ached {CACHE_FILE}: {self.app_dict}")
            
    def clear_cache(self):
        with open(self.dir + CACHE_FILE, "w") as f:
            json.dump({}, f, indent=4)
            self.app_dict = {}
             # Dev log
            print(f"Cache cleared")

    def flush_to_db(self):
        AppUsage.flush_to_db(self.app_dict)
       
    def dump_cache_to_db(self):
        print("[⚙️] Flushing existing cache to DB before starting engine...")
        with open(self.dir + CACHE_FILE, "r") as f:
            try:
                cache = json.load(f)
                self.app_dict = cache
                self.flush_to_db()
                # Optionally clear file after dumping
                self.clear_cache()
            except json.JSONDecodeError:
                print("[⚠️] cache.json was corrupted or empty. Skipping DB flush.")       
            
    def run(self):
        
        # Start by flushing previous cache data to the database
        self.dump_cache_to_db()

        # Initialize timestamps for cache and DB flush intervals
        current_time = time.time()
        last_cache_time = current_time
        last_flush_time = current_time

        # Flag to keep the engine running
        self.keep_running = True

        # Main loop
        while self.keep_running:
            # Evaluate app usage and update the in-memory app_dict
            self.evaluate()

            # Wait for the next cycle
            time.sleep(CACHE_INTERVAL)

            # Periodically write current in-memory app usage to the cache file
            if time.time() - last_cache_time >= CACHE_FLUSH_INTERVAL:
                self.write_to_cache()
                last_cache_time = time.time()

            # Periodically flush cache data from memory to the database
            if time.time() - last_flush_time >= DB_FLUSH_INTERVAL:
                self.flush_to_db()       # Move data from memory to DB
                self.clear_cache()       # Clear the local JSON cache file
                self.app_dict = {}       # Reset in-memory app usage tracking
                last_flush_time = time.time()

                
    def stop(self):
        self.keep_running = False
        self.write_to_cache()
        self.dump_cache_to_db()
        self.clear_cache()
        