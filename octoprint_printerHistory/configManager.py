# configManager.py

import os
import json

class ConfigManager:
    def __init__(self, plugin):
        self.plugin = plugin
        self.config_folder = os.path.join(self.plugin.get_plugin_data_folder())
        self.config_file = os.path.join(self.config_folder, "config.json")
        self.config = self.load_config()

    def load_config(self):
        try:
            if not os.path.exists(self.config_folder):
                os.makedirs(self.config_folder)

            if not os.path.exists(self.config_file):
                default_config = {
                    "database": {
                        "user": "",
                        "password": "",
                        "host": "",
                        "port": 0,
                        "database": ""
                    }
                }
                self.save_config(default_config)
                self._logger.info("Create default_config")
                return default_config

            with open(self.config_file, 'r') as f:
                return json.load(f)

        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        self.config = config

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config(self.config)

    def get_db_config(self):
        return self.config.get('database', {})
