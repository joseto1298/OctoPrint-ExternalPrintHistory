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

class ExternalPrintHistoryPlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.BlueprintPlugin
    ):
    
    def __init__(self):
        self._logger = logging.getLogger("octoprint.plugins.ExternalPrintHistory")
        self.database_manager = DatabaseManager(plugin=self,_logger=self._logger)
        self.event_handler = EventHandler(plugin=self,_logger=self._logger)
        self.config_manager = ConfigurationManager(plugin=self,_logger=self._logger)
        self.plugin_Checker = PluginChecker(plugin=self,_logger=self._logger)
        self._isInitialized = False

    def initialize(self):
        self._isInitialized = True
        
    def on_startup(self, host, port):
        self._logger.info("ExternalPrintHistory Plugin started with configuration")

    #def on_after_startup(self):
        #self.plugin_Checker._checkAndLoadThirdPartyPluginInfos()

    def on_shutdown(self):
        self._logger.info("Shutting down ExternalPrintHistory plugin")

    def get_settings_defaults(self):
        return self.config_manager._load_config()
    
    def on_settings_load(self):        
        return self.config_manager._load_config()

    def on_settings_save(self, data):
        #self._logger.info("data save: " + str(data))
        
        setting, printer_data = self.config_manager._update_dictionaries(data,self.config_manager._load_config())
        result = self.database_manager._set_and_test_connection(setting)
        if not result.get("error"):
            result = self.database_manager._update_insert_printer_config(printer_data, setting["printer_id"])
            
        if result.get("error"):
            self._logger.error("Error saving data: " + str(result))
            self.config_manager._showPopUp("error", "Error saving data", "Data not updated.", False)
        else:
            self.config_manager._save_config(setting)
            self.config_manager._showPopUp("success", "Saved Data", "Data was updated", True)            
    
        #self._logger.info("Saved config: " + str(config))
        #self._logger.info("Saved printer_data: " + str(printer_data))
        
    def register_custom_events(*args, **kwargs):
        return []
    
    def on_sentGCodeHook(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        if not self._isInitialized:
            return
        
        pass
    
    def on_event(self, event, payload):
        self._logger.info(f"Handling event : {event}")    
        self._logger.info(payload)    

        if event == Events.CLIENT_OPENED:
            if self.config["plugin_dependency_check"]:
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
        #self._logger.info("testdbconnection" + str(request.json))
        response = self.database_manager._set_and_test_connection(request.json)                
        return flask.jsonify(response)

    @octoprint.plugin.BlueprintPlugin.route("/selectPrinter", methods=["PUT"])
    def select_printer_config(self):
        data = request.json
        #self._logger.info("selectPrinter: " + str(data))
        try:  
            response = self.database_manager._set_and_test_connection(data)
            if not response.get("error", True):
                response = self.database_manager._select_Printer(data.get("printer_id", 0))
                printer_data = getattr(response, 'printer_data', None)
                if printer_data is not None:
                    self.printer_data.update(printer_data)
                    self.printer_data.pop("printer_id")
            #self._logger.info("response: " + str(response))
            
        except Exception as e:
            self._logger.error(f"Error select printer config: {str(e)}")
            response = {"error": True, "message": str(e)}
        
        return flask.jsonify(response)

    @octoprint.plugin.BlueprintPlugin.route("/deactivatePluginCheck", methods=["PUT"])
    def deactivatePluginCheck(self):
            #self.config["plugin_dependency_check"] = False
            #self._settings.set(['plugin_dependency_check'], False)
            #self._settings.save()
            self.config["plugin_dependency_check"] = False
            self.config_manager._update_config(self.config)
            
            response = {"error": False, "message": "Plugin check deactivated"}
            return flask.jsonify(response)
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
            css = ["css/ExternalPrintHistory.css"]
        )
    
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