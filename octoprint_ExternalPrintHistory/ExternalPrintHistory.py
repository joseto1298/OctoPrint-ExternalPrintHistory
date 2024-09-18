# coding=utf-8
from __future__ import absolute_import

import logging
import octoprint.plugin
import flask

from flask import request
from octoprint.events import Events
from .modules.eventHandler import EventHandler
from .modules.databaseManager import DatabaseManager
from .modules.configurationManager import ConfigurationManager
from .modules.pluginChecker import PluginChecker
from .common.SettingsKeys import SettingsKeys

class ExternalPrintHistoryPlugin(octoprint.plugin.StartupPlugin,
                                octoprint.plugin.TemplatePlugin,
                                octoprint.plugin.SettingsPlugin,
                                octoprint.plugin.AssetPlugin,
                                octoprint.plugin.EventHandlerPlugin,
                                octoprint.plugin.SimpleApiPlugin,
                                octoprint.plugin.BlueprintPlugin):
    
    def __init__(self):
        self._logger = logging.getLogger("octoprint.plugins.ExternalPrintHistory")
        self.database_manager = DatabaseManager(plugin=self, _logger=self._logger)
        self.event_handler = EventHandler(plugin=self, _logger=self._logger)
        self.config_manager = ConfigurationManager(plugin=self, _logger=self._logger)
        self.plugin_Checker = PluginChecker(plugin=self, _logger=self._logger)
        self._isInitialized = False

    def initialize(self):
        self._logger.info("Initializing ExternalPrintHistory Plugin")
        self._isInitialized = True
        
    def on_startup(self, host, port):
        self._logger.info("ExternalPrintHistory Plugin started")
        self.config_manager._initialize_key_and_salt()
        settings = self.config_manager._load_config()
        self.database_manager._set_and_test_connection(settings)
        
    #def on_after_startup(self):
        
    def on_shutdown(self):
        self._logger.info("Shutting down ExternalPrintHistory plugin")
        
    def get_settings_defaults(self):
        settings = {
            SettingsKeys.PLUGIN_DEPENDENCY_CHECK: True,
            SettingsKeys.PRINTER_ID: 0,
            SettingsKeys.DB_USER: "",
            SettingsKeys.DB_PASSWORD: "",
            SettingsKeys.DB_HOST: "",
            SettingsKeys.DB_DATABASE: "",            
            SettingsKeys.DB_PORT: 3306,
            SettingsKeys.CURRENCY: "\u20ac",
            SettingsKeys.ELECTRICITY_COST: 0.0
        }

        return settings
    
    def on_settings_load(self):  
        settings = self.config_manager._load_config()
        self.database_manager._set_and_test_connection(settings)
        
        return settings
    
    def on_settings_save(self, data):
        result = {"error": False}       
        setting, printer_data = self.config_manager._update_dictionaries(data)
        config = self.config_manager._load_config()
        
        if setting:
            config.update(setting)

        if printer_data:
            result = self.database_manager._set_and_test_connection(config)
            
            if not result.get("error"):
                result = self.database_manager._update_insert_printer_config(printer_data, self.config_manager._get_printer_id())
                self._logger.info(f"Result: {result}")
            
            if result.get("error"):
                self._logger.error(f"Error saving data: {result}")
                self.config_manager._showPopUp("error", "Error saving data", "Data not updated.", False)
            elif result.get("insert"):
                config.update({SettingsKeys.PRINTER_ID: result.get("printer_id")})
        
        if not result.get("error"):
            self.config_manager._showPopUp("success", "Saved Data", "Data was updated", True)
        
        db_password = config.get(SettingsKeys.DB_PASSWORD)
        encrypted_db_password = self.config_manager._encrypt(db_password)
        config.update({SettingsKeys.DB_PASSWORD: encrypted_db_password})
        
        octoprint.plugin.SettingsPlugin.on_settings_save(self, config)

    def register_custom_events(*args, **kwargs):
        return []
    
    def on_sentGCodeHook(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        if not self._isInitialized:
            return
        # Aquí puedes manejar el código G según sea necesario.
        pass
    
    def on_event(self, event, payload):
        
        #self._logger.info(f"Handling event: {event}")
        #self._logger.info(payload)

        if event == Events.CLIENT_OPENED:
            if self.config_manager._get_plugin_dependency_check():
                self.plugin_Checker._checkAndLoadThirdPartyPluginInfos()

        elif event == Events.PRINT_STARTED:
            self.event_handler._handle_print_started(payload)

        elif event == Events.PRINT_DONE:
            self.event_handler._handle_print_done(payload)

        elif event == Events.PRINT_FAILED:
            self.event_handler._handle_print_failed(payload)

        elif event == Events.METADATA_STATISTICS_UPDATED:
            self.event_handler._handle_metadata_statistics_updated(payload)
        
        elif event == Events.METADATA_ANALYSIS_FINISHED:
            self.event_handler._handle_metadata_analysis_finished(payload)
    
    ###################################################################
    ##################### API ROUTES ##################################
    ###################################################################
    @octoprint.plugin.BlueprintPlugin.route("/testdbconnection", methods=["PUT"])
    def test_db_connection(self):
        # self._logger.info("testdbconnection" + str(request.json))
        try:
            response = self.database_manager._test_connection(request.json)
            # Save data
        except Exception as e:
            self._logger.error(f"Database connection test failed: {str(e)}")
            response = {"error": True, "message": "Failed to test database connection"}
        
        return flask.jsonify(response)

    @octoprint.plugin.BlueprintPlugin.route("/selectPrinter", methods=["PUT"])
    def select_printer_config(self):
        data = request.json
        # self._logger.info("selectPrinter: " + str(data))
        try:  
            response = self.database_manager._select_Printer(self.config_manager._get_printer_id())
            # self._logger.info("response: " + str(response))
        except Exception as e:
            self._logger.error(f"Error select printer config: {str(e)}")
            response = {"error": True, "message": str(e)}
        
        return flask.jsonify(response)

    @octoprint.plugin.BlueprintPlugin.route("/deactivatePluginCheck", methods=["PUT"])
    def deactivatePluginCheck(self):
        response = {"error": False, "message": "Plugin check deactivated"}
        self._settings.set([SettingsKeys.PLUGIN_DEPENDENCY_CHECK], False)
        return flask.jsonify(response)
    
    def is_blueprint_csrf_protected(self):
        return True
    
    def get_template_configs(self):
        return [
            dict(type="settings", name="External Print History", custom_bindings=True, template="ExternalPrintHistory_settings.jinja2"),
            dict(type="tab", name="External Print History", custom_bindings=True, template="ExternalPrintHistory_tab.jinja2")
        ]

    def get_assets(self):
        return dict(
            js = [
                "js/ExternalPrintHistory_ApiRest.js",
                "js/ExternalPrintHistory_pluginCheckDialog.js",                
                "js/ExternalPrintHistory_settings.js",
                "js/ExternalPrintHistory.js",           
                ],
            css = [
                "css/ExternalPrintHistory.css"
                ]
        )
    
    #def on_settings_migrate(self, target, current=None):

    def get_version(self):
        return self._plugin_version      

    def get_update_information(self):
        """
        The function `get_update_information` returns update information for a plugin named "ExternalPrintHistory
        Plugin" from a GitHub repository.
        :return: A dictionary containing information about the "ExternalPrintHistory" plugin, including its
        display name, version, type, user, repository, current version, and a link to download the plugin
        from GitHub.
        """
        return {
            "ExternalPrintHistory": {
                "displayName": "ExternalPrintHistory",
                "displayVersion": self._plugin_version,
                "type": "github_release",
                "user": "joseto1298",
                "repo": "OctoPrint-ExternalPrintHistory",
                "current": self._plugin_version,
                "pip": "https://github.com/joseto1298/OctoPrint-ExternalPrintHistory/archive/{target_version}.zip",
            }
        }
