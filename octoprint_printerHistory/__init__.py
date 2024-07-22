from __future__ import absolute_import

import os
import json
import logging
import octoprint.plugin
from .eventHandler import Event
from .configManager import ConfigManager

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
        self.event_handler = None
        self.config_Manager = None
       
    def on_startup(self, host, port):
        self._logger.info("Printerhistory Plugin started with configuration")
        self.event_handler = Event(db=None, logger=self._logger)
        self.config_Manager = ConfigManager(logger=self._logger)
                
    def on_shutdown(self):
        self._logger.info("Shutting down Printerhistory plugin")
    
    def get_settings_defaults(self):
        return self.modify_config()

    def on_settings_load(self):
        return self.modify_config()
    
    def on_settings_save(self, data):
        return self.modify_config(data=data)

    def modify_config(self, data=None):
        self.config_folder = self.get_plugin_data_folder()
        self.config_file = os.path.join(self.config_folder, "config.json")

        try:
            if not os.path.exists(self.config_folder):
                os.makedirs(self.config_folder)

            if not os.path.exists(self.config_file):
                default_config = {
                    "db_user": "user", 
                    "db_password": "password", 
                    "db_host": "host", 
                    "db_port": "3306", 
                    "db_database": "database"
                }
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
            
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            if data:
                combined_data = {**config, **data}
                with open(self.config_file, 'w') as f:
                    json.dump(combined_data, f, indent=4)
                return {}

            return config

        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return {}
        
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