# focusflow/core/buffer_manager.py
import json
import os
from datetime import datetime

class BufferManager:
    def __init__(self, cache_file_path: str):
        self.cache_file_path = cache_file_path
        self.buffer = {
            "timestamp": datetime.now().isoformat(),
            "app_usage": {}
        }

        self.load_buffer_from_file()

    def add_usage(self, app_name: str, seconds: int):
        current = self.buffer["app_usage"].get(app_name, 0)
        self.buffer["app_usage"][app_name] = current + seconds

    def write_to_file(self):
        with open(self.cache_file_path, "w") as f:
            json.dump(self.buffer, f)

    def load_buffer_from_file(self):
        if os.path.exists(self.cache_file_path):
            try:
                with open(self.cache_file_path, "r") as f:
                    data = json.load(f)
                    if "app_usage" in data:
                        self.buffer = data
            except Exception as e:
                print(f"⚠️ Failed to load cache: {e}")

    def flush_to_db(self, session):
        from focusflow.models.app_usage import AppUsage  # assuming model path

        for app, seconds in self.buffer["app_usage"].items():
            record = AppUsage(app_name=app, usage_seconds=seconds, date=datetime.now().date())
            session.add(record)

        session.commit()
        self.clear_buffer()

    def clear_buffer(self):
        self.buffer = {
            "timestamp": datetime.now().isoformat(),
            "app_usage": {}
        }

        # remove file too
        if os.path.exists(self.cache_file_path):
            os.remove(self.cache_file_path)
