from __future__ import absolute_import

import json
import os
import logging
import octoprint.plugin
from .eventHandler import Event

class PrinterhistoryPlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.SimpleApiPlugin
):
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self.config_folder = None
        self.config_file = None
        self.config = None
        self.event_handler = None
    
    def initialize(self):
        self.config_folder = self.get_plugin_data_folder()
        self.config_file = os.path.join(self.config_folder, "config.json")
        self.config = self.load_config()
        self.event_handler = Event(db=None, logger=self._logger)
        
    def on_startup(self, host, port):
        self.event_handler = Event(db=None, logger=self._logger) 
        self._logger.info("Printerhistory Plugin started with configuration: {}".format(self.config))

    def on_shutdown(self):
        self._logger.info("Shutting down Printerhistory plugin")
    
    def get_settings_defaults(self):
        return self.load_config()
        
    def on_settings_load(self):
        return self.load_config()
    
    def on_settings_save(self, data):
        self._logger.info("Saving settings...")
        self.save_config(data)
        self.config = data

    def load_config(self):
        self._logger.info("Load config")
        try:
            if not os.path.exists(self.config_folder):
                os.makedirs(self.config_folder)

            if not os.path.exists(self.config_file):
                default_config = [{
                    "database": {
                        "user": "",
                        "password": "",
                        "host": "",
                        "port": 0,
                        "database": ""
                    }
                }]
                self.save_config(default_config)
                self._logger.info("Create default_config")
                return default_config

            with open(self.config_file, 'r') as f:
                self._logger.info("Load config 2")
                config = json.load(f)
                self._logger.info("Loaded configuration: %s", config)
                return config

        except Exception as e:
            self._logger.error(f"Error loading config: {e}")
            return {}

    def save_config(self, config):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
                self._logger.info("Configuration saved successfully.")
        except Exception as e:
            self._logger.error(f"Error saving config: {e}")

    def on_event(self, event, payload):
        if self.event_handler:
            self.event_handler.handle_event(event, payload)

    def get_template_configs(self):
        return [
            dict(type="settings", name="Printer History", custom_bindings=True, template="PrinterhistoryPlugin_settings.jinja2")
        ]

    def get_assets(self):
        return {
            "js": ["js/printerHistory.js"],
            "css": ["css/printerHistory.css"]
        }

    def get_update_information(self):
        return {
            "printerHistory": {
                "displayName": "Printerhistory Plugin",
                "displayVersion": self._plugin_version,
                "type": "github_release",
                "user": "joseto1298",
                "repo": "OctoPrint-Printerhistory",
                "current": self._plugin_version,
                "pip": "https://github.com/joseto1298/OctoPrint-Printerhistory/archive/{target_version}.zip",
            }
        }

__plugin_name__ = "Printerhistory Plugin"
__plugin_pythoncompat__ = ">=3,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PrinterhistoryPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
