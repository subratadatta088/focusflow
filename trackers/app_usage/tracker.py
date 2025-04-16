import time
from rules.base import BaseTracker
from models.app_usage import AppUsage


import json
from constants import IMPORTANT_APPS, CACHE_FILE ,CACHE_INTERVAL, CACHE_FLUSH_INTERVAL, DB_FLUSH_INTERVAL

 

class AppUsageTracker(BaseTracker):
    def __init__(self):
        self.cache = []
        self.last_cache_flush = time.time()
        self.last_db_flush = time.time()
        self.model = AppUsage
        self.keep_running = True
        self.app_dict = {}
        self.dir = "trackers/app_usage/"
        
   
        
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
        