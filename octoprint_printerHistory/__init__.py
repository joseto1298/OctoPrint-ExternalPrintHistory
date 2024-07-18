# __init__.py

from __future__ import absolute_import
from .configManager import ConfigManager

import logging
import octoprint.plugin

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
        self.config_manager = None
        self._logger.info("Plugin initialized successfully.")

    def on_after_startup(self):
        self.config_manager = ConfigManager(self)
        self._logger.info("Printerhistory Plugin started with configuration: {}".format(self.config_manager.config))

    def on_shutdown(self):
        self._logger.info("Shutting down Printerhistory plugin")

    #def get_settings_defaults(self):
    #    self._logger.info("get_settings_defaults")
    #    return dict (
	#		databaseUser = "",
	#		databasePassword = "",
	#		databaseHost = "",
	#		databasePort = 3306,
	#		databaseName = "",
	#	)
    
    def get_settings_defaults(self):
        return self.config_manager.config if self.config_manager else {}

    def on_settings_save(self, data):
        # Acceder y guardar los datos específicos de configuración
        if "databaseSettings" in data:
            database_settings = data["databaseSettings"]
            self._settings.set(["database", "user"], database_settings.get("user"))
            self._settings.set(["database", "password"], database_settings.get("password"))
            self._settings.set(["database", "host"], database_settings.get("host"))
            self._settings.set_int(["database", "port"], int(database_settings.get("port")))
            self._settings.set(["database", "database"], database_settings.get("database"))
            self._settings.save()
            self._logger.info("Database settings saved")

    def get_template_configs(self):
        self._logger.info("Database template_config")
        return [
            dict(type="settings", name="Printer History", custom_bindings=True)
        ]

    def get_assets(self):
        return {
            "js": ["js/printerHistory.js"],
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

    def on_event(self, event, payload):
        if self.event_handler:
            self.event_handler.handle_event(event, payload)

__plugin_name__ = "Printerhistory Plugin"
__plugin_pythoncompat__ = ">=3,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PrinterhistoryPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
