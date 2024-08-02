from __future__ import absolute_import
import logging
import octoprint.plugin
from .eventHandler import EventHandler
from .databaseManager import DatabaseManager
from .configurationManager import ConfigurationManager

class PrinterhistoryPlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.BlueprintPlugin
):
    def __init__(self):
        self._logger = logging.getLogger("octoprint.plugins.printerhistory")
        self.event_handler = EventHandler(plugin=self, logger=self._logger)
        self.database_manager = DatabaseManager(plugin=self, logger=self._logger)
        self.config_manager = ConfigurationManager(plugin=self, logger=self._logger)
        self.printer_id = None

    def on_startup(self, host, port):
        self._logger.info("PrinterHistory Plugin started with configuration")
        self.database_manager._set_connection_settings(self.config_manager._load_existing_config())

    def on_shutdown(self):
        self._logger.info("Shutting down PrinterHistory plugin")

    def get_settings_defaults(self):
        """Returns the default settings for the plugin."""
        return self.config_manager._initialize_config_files()

    def on_settings_load(self):
        """Called when the settings are loaded."""
        settings_data = self.config_manager._load_existing_config()
        self.printer_id = settings_data.get("printer_id")
        return settings_data
    
    def on_settings_save(self, data):
        """Called when the settings are saved."""
        current_settings = self.config_manager._load_existing_config()
        updated_settings = current_settings.copy()
        updated_settings.update(data)

        db_changes = self.config_manager._process_database_changes(data, current_settings)
        printer_changes = self.config_manager._process_printer_changes(data, current_settings)

        if db_changes:
            self.database_manager._set_connection_settings(updated_settings)
        if printer_changes:
            self.printer_id = self.database_manager._update_insert_printer_config(updated_settings)
            updated_settings["printer_id"] = self.printer_id
        
        if db_changes or printer_changes:
            self.config_manager._update_config(updated_settings)

    def on_event(self, event, payload):
        """Handles events triggered by OctoPrint."""
        self._logger.info(f"Handling event: {event} {payload}")
        self.event_handler.handle_event(event, payload)

    def get_template_configs(self):
        """
        Returns the template configurations.
        """
        return [
            dict(type="settings", name="Printer History", custom_bindings=True, template="PrinterhistoryPlugin_settings.jinja2")
        ]

    def get_assets(self):
        """
        Returns the assets (JS and CSS) required by the plugin.
        """
        return {
            "js": ["js/printerHistory.js"],
            "css": ["css/printerHistory.css"]
        }

    def get_update_information(self):
        """
        Returns update information for the plugin.
        """
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