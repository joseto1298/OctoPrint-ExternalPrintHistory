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
        """
        Initializes the PrinterhistoryPlugin instance.

        Sets up the logger, event handler, database manager, and configuration manager.
        """
        self._logger = logging.getLogger("octoprint.plugins.printerhistory")
        self.event_handler = EventHandler(plugin=self, logger=self._logger)
        self.database_manager = DatabaseManager(plugin=self, logger=self._logger)
        self.config_manager = ConfigurationManager(plugin=self, logger=self._logger)
        self.config_settings = None

    def on_startup(self, host, port):
        """
        The `on_startup` function initializes configuration settings and retrieves printer data from a
        database, handling any exceptions that may occur.
        """
        try:
            self._logger.info("PrinterHistory Plugin started with configuration")
            self.config_manager._initialize_config_files()
            self.config_settings = self.config_manager._load_existing_config()
            self.database_manager._set_connection_settings(self.config_settings)        
            printer_data = self.database_manager._select_printer_config(self.config_settings.get("printer_id", 0))

            printer_info = printer_data.get('printer_data', {})
            self.config_settings["printer_name"] = printer_info.get("name", "")
            self.config_settings["printer_model"] = printer_info.get("model", "")
            self.config_settings["printer_brand"] = printer_info.get("brand", "")
            self.config_settings["printer_power_consumption"] = printer_info.get("power_consumption", 0)
            self.config_settings["printer_purchase_price"] = printer_info.get("purchase_price", 0)
            self.config_settings["printer_estimated_lifespan"] = printer_info.get("estimated_lifespan", 0)
            self.config_settings["printer_maintenance_costs"] = printer_info.get("maintenance_costs", 0)
            
        except Exception as e:
            self.logger.error(f"Error on startup: {e}")

    def on_shutdown(self):
        """
        The `on_shutdown` function logs a message indicating the shutdown of the PrinterHistory plugin.
        """
        self._logger.info("Shutting down PrinterHistory plugin")

    def get_settings_defaults(self):
        """
        The function `get_settings_defaults` returns the default settings for the plugin.
        :return: The `get_settings_defaults` method is returning the `config_settings` attribute of the
        object.
        """
        return self.config_settings
 
    def on_settings_load(self):
        """
        The `on_settings_load` function is called when the settings are loaded and returns the
        `config_settings`.
        :return: The `config_settings` attribute is being returned.
        """
        return self.config_settings
    
    #def on_settings_save(self, data):
        #"""Called when the settings are saved."""

    def on_event(self, event, payload):
        #self._logger.info(f"Handling event: {event} {payload}")
        self.event_handler.handle_event(event, payload)

    ##################################
    ########## API ###################
    ##################################

    @octoprint.plugin.BlueprintPlugin.route("/testdbconnection", methods=["PUT"])
    def test_db_connection(self):
        """
        The `test_db_connection` function tests a database connection, updates configuration settings, and
        logs any errors encountered.
        :return: The `test_db_connection` method is returning a JSON response using Flask's `jsonify`
        function. The response will contain the result of testing the database connection and updating
        configuration settings based on the data received in the request. If an error occurs during the
        process, an error message will be included in the response.
        """
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
        """
        This Python function updates printer configuration settings based on the data provided in the
        request.
        :return: The `update_printer_config` method returns a JSON response containing the result of
        updating the printer configuration settings. The response may include information about any
        errors encountered during the update process.
        """
        data = request.json
        try:
            response = self.database_manager._update_insert_printer_config(data)
            self._logger.info(f"response: {response}")           
            if response.get("insert", False):
                self.config_settings["printer_id"] = response.get("printer_id", 0)
                self.config_manager._update_config(self.config_settings)            
        except Exception as e:
            self._logger.error(f"Error update printer settings: {str(e)}")
            response = {"error": True, "message": str(e)}
        
        return flask.jsonify(response)            

    @octoprint.plugin.BlueprintPlugin.route("/selectprinterconfig", methods=["PUT"])
    def select_printer_config(self):
        """
        The function `select_printer_config` retrieves printer configuration data based on the provided
        printer ID and handles any exceptions that may occur during the process.
        :return: The `select_printer_config` method returns a JSON response containing the result of
        selecting a printer configuration from the database. The response could either be the printer
        configuration data if the selection was successful, or an error message if an exception occurred
        during the process.
        """
        data = request.json
        try:
            response = self.database_manager._select_printer_config(data.get("printer_id", 0))
        except Exception as e:
            self._logger.error(f"Error select printer config: {str(e)}")
            response = {"error": True, "message": str(e)}
        
        return flask.jsonify(response)

    @octoprint.plugin.BlueprintPlugin.route("/saveData", methods=["PUT"])
    def save_data(self):
        """
        The `save_data` function in Python saves input data to a configuration manager and updates
        specific settings, handling any errors that may occur.
        :return: The `save_data` method returns a JSON response containing information about whether the
        data was saved successfully or if there was an error. The response includes an "error" key
        indicating if an error occurred (True or False) and a "message" key providing a corresponding
        message.
        """
        data = request.json
        try:
            self.config_manager._update_config(data) 
            self.config_settings["electricity_cost"] = data.get("electricity_cost")
            self.config_settings["currency"] = data.get("currency")
            response = {"error": False, "message": "Data saved"}                     
        except Exception as e:
            self._logger.error(f"Error saving data: {str(e)}")
            response = {"error": True, "message": str(e)}
        
        return flask.jsonify(response)
    

    def get_template_configs(self):
        """
        The `get_template_configs` function returns a list of template configurations for a Printer History
        plugin.
        :return: A list of dictionary objects containing template configurations for the "Printer History"
        settings, with custom bindings enabled and using the "PrinterhistoryPlugin_settings.jinja2"
        template.
        """
        """
        Returns the template configurations.
        """
        return [
            dict(type="settings", name="Printer History", custom_bindings=True, template="PrinterhistoryPlugin_settings.jinja2")
        ]

    def get_assets(self):
        """
        The `get_assets` function returns the assets (JS and CSS) required by the plugin.
        :return: The `get_assets` method returns a dictionary with two keys: "js" and "css". The value of
        the "js" key is a list containing the path to a JavaScript file
        "js/PrinterhistoryPlugin_settings.js", and the value of the "css" key is a list containing the
        path to a CSS file "css/printerHistory.css".
        """
        """
        Returns the assets (JS and CSS) required by the plugin.
        """
        return {
            "js": ["js/PrinterhistoryPlugin_settings.js"],
            "css": ["css/printerHistory.css"]
        }

    def get_update_information(self):
        """
        The function `get_update_information` returns update information for a plugin named "Printerhistory
        Plugin" from a GitHub repository.
        :return: A dictionary containing information about the "Printerhistory" plugin, including its
        display name, version, type, user, repository, current version, and a link to download the plugin
        from GitHub.
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
    """
    Initializes the plugin by creating an instance of the PrinterhistoryPlugin class and setting up the necessary hooks.
    This function is automatically called when the plugin is loaded.

    Parameters:
        None

    Returns:
        None
    """
    global __plugin_implementation__
    __plugin_implementation__ = PrinterhistoryPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
