from __future__ import absolute_import
import logging
import flask
import octoprint.plugin
from .eventHandler import EventHandler
from .databaseManager import DatabaseManager
from .configurationManager import ConfigurationManager
from flask import jsonify, request, make_response, Response, send_file


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
        self.config_settings = None

    def on_startup(self, host, port):
        self._logger.info("PrinterHistory Plugin started with configuration")
        self.config_manager._initialize_config_files()
        self.config_settings = self.config_manager._load_existing_config()
        self.database_manager._set_connection_settings(self.config_settings)        
        printer_data = self.database_manager._select_printer_config(self.config_settings.get("printer_id", 0))
        if not printer_data.get("error") :
            printer_info = printer_data.get('printer_data', {})
            self.config_settings["printer_name"] = printer_info.get("name", " ")
            self.config_settings["printer_model"] = printer_info.get("model", " ")
            self.config_settings["printer_brand"] = printer_info.get("brand", " ")
            self.config_settings["printer_power_consumption"] = printer_info.get("power_consumption", 0)

    def on_shutdown(self):
        self._logger.info("Shutting down PrinterHistory plugin")

    #def get_settings_defaults(self):
    """Returns the default settings for the plugin."""
              
    def on_settings_load(self):
        """Called when the settings are loaded."""
        return self.config_settings
    
    #def on_settings_save(self, data):
    """Called when the settings are saved."""

    def on_event(self, event, payload):
        """Handles events triggered by OctoPrint."""
        #self._logger.info(f"Handling event: {event} {payload}")
        self.event_handler.handle_event(event, payload)
        
    @octoprint.plugin.BlueprintPlugin.route("/testdbconnection", methods=["PUT"])
    def test_db_connection(self):
        data = request.json
        try:
            response = self.database_manager._test_connection(data)
            if not response.get("error") :
                self.config_manager._update_config(data)
                self.database_manager._set_connection_settings(data)
        except Exception as e:
            self._logger.error(f"Error testing DB connection: {str(e)}")
            response = {"error": True, "message": str(e)}
        
        return flask.jsonify(response)

    @octoprint.plugin.BlueprintPlugin.route("/updateprinterconfig", methods=["PUT"])
    def update_printer_config(self):
        data = request.json
        try:
            response = self.database_manager._update_insert_printer_config(data)
            if response.get("insert", False):
                self.config_settings["printer_id"] = response.get("printer_id")
                self.config_manager._update_config(self.config_settings) 
        except Exception as e:
            self._logger.error(f"Error testing DB connection: {str(e)}")
            response = {"error": False, "message": str(e)}
        
        return flask.jsonify(response)            

    @octoprint.plugin.BlueprintPlugin.route("/selectprinterconfig", methods=["PUT"])
    def select_printer_config(self):
        data = request.json
        try:
            response = self.database_manager._select_printer_config(data.get("printer_id", 0))
        except Exception as e:
            self._logger.error(f"Error testing DB connection: {str(e)}")
            response = {"error": True, "message": str(e)}
        
        return flask.jsonify(response)

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
