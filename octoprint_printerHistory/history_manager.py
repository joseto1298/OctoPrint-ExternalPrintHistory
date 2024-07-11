import os
import json
import datetime

class HistoryManager:
    def __init__(self, history_file):
        self._history_file = history_file
        self._history_data = self._load_history_data()

    def _load_history_data(self):
        try:
            with open(self._history_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def _save_history_data(self):
        with open(self._history_file, "w") as f:
            json.dump(self._history_data, f, indent=4)

    def add_to_history(self, job):
        timestamp = datetime.datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "job": job
        }
        self._history_data.append(entry)
        self._save_history_data()

    def get_history(self):
        return self._history_data
