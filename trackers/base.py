from abc import ABC, abstractmethod
import threading
import platform
import psutil
import json
from constants import CACHE_FILE 

class BaseTracker(ABC):
    def __init__(self):
        self.platform = platform.system().lower()
        self.dir = "trackers/base/"
        self.app_dict = {}
        self.model = None
        
    @abstractmethod
    def evaluate(self):
        """
       evaluate method which will looped
        """
        pass

    @abstractmethod
    def run(self):
        """
       Runs the tracker
        """
        pass
    
    @abstractmethod
    def stop(self):
        """
       Stops the tracker
        """
        pass
    
     # Getting the focused app.
    def get_active_app(self):
        if self.platform == "darwin":
            from platform_utils.mac import get_focused_app as get_focused_app_mac
            return get_focused_app_mac()
        elif self.platform == "windows":
            from platform_utils.windows import get_focused_app as get_focused_app_win
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
    
    def write_to_cache(self):
        with open(self.dir + CACHE_FILE, "w") as f:
            json.dump(self.app_dict, f, indent=4)
            print(f"[🧠] Activity Cache Saved: {self.app_dict}")
   
    def clear_cache(self):
        with open(self.dir + CACHE_FILE, "w") as f:
            json.dump({}, f, indent=4)
            self.app_dict = {}
             # Dev log
            print(f"Cache cleared")     
            
                
    def dump_cache_to_db(self):
        print("[⚙️] Flushing previous activity cache to DB...")
        try:
            with open(self.dir + CACHE_FILE, "r") as f:
                cache = json.load(f)
                self.app_dict = cache
                self.flush_to_db()
                self.clear_cache()
        except json.JSONDecodeError:
            print("[⚠️] Activity cache corrupted. Skipping.")
            
    def flush_to_db(self):
        self.model.flush_to_db(self.app_dict)
