from __future__ import absolute_import
import logging
import octoprint.plugin
import flask
from flask import request
from octoprint.events import Events
from octoprint_ExternalPrintHistory.eventHandler import EventHandler
from octoprint_ExternalPrintHistory.databaseManager import DatabaseManager
from octoprint_ExternalPrintHistory.configurationManager import ConfigurationManager
from octoprint_ExternalPrintHistory.pluginChecker import PluginChecker

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
        self.database_manager = DatabaseManager(plugin=self, logger=self._logger)
        self.event_handler = EventHandler(plugin=self, logger=self._logger)
        self.config_manager = ConfigurationManager(plugin=self, logger=self._logger)
        self.plugin_Checker = PluginChecker(plugin=self, logger=self._logger)
        self.config = {}
        self.printer_data = {}
        
    def on_startup(self, host, port):
        #self._logger.info("ExternalPrintHistory Plugin started with configuration")

        self.config_manager._initialize_config_files()
        self.config = self.config_manager._load_existing_config()
        self.printer_data = self.config_manager._get_printer_data()
        
        result = self.database_manager._set_and_test_connection(self.config)
        if not result.get("error"):
            printer_data = self.database_manager._select_Printer(self.config.get("printer_id", 0))
            printer_data = self.config_manager._transform_printer_data(printer_data)
            self.printer_data.update(printer_data)
            
        #self._logger.info(f"Methods and attributes of SpoolManager: {methods_and_attributes}")
        
        #if spool_manager:
        #    spools_data = spool_manager.get_current_spools()
        #
        #    for spool in spools_data:
        #        spool_name = spool.get("spoolName")
        #        tool_id = spool.get("toolId")
        #        used_weight = spool.get("usedWeight")
        #        remaining_weight = spool.get("remainingWeight")
        #
        #        self._logger.info(f"Spool: {spool_name}, Tool: {tool_id}, Used: {used_weight}g, Remaining: {remaining_weight}g")


    #def on_after_startup(self):
        #self.plugin_Checker._checkAndLoadThirdPartyPluginInfos()

    def on_shutdown(self):
        self._logger.info("Shutting down ExternalPrintHistory plugin")

    def get_settings_defaults(self):
        setting = {}
        setting.update(self.config)
        setting.update(self.printer_data)
        
        return setting
    
    def on_settings_load(self):
        setting = {}
        setting.update(self.config)
        setting.update(self.printer_data)
        
        return setting
    
    def on_settings_save(self, data):
        
        #self._logger.info("data save: " + str(data))
                
        #if data.get("electricity_cost") is not None:
        #   self.config['electricity_cost'] = data["electricity_cost"]
        #
        #if data.get("plugin_check_activated") is not None:
        #   self.config['plugin_check_activated'] = data["plugin_check_activated"]
                        
        config, printer_data = self.config_manager._update_dictionaries_on_save(data, self.config, self.printer_data)
        result = self.database_manager._set_and_test_connection(config)
        if not result.get("error"):
            result = self.database_manager._update_insert_printer_config(printer_data, self.config["printer_id"])
        if result.get("error"):
            self._logger.error("Error saving data: " + str(result))
            self.config_manager._showPopUp("error", "Error saving data", "Data not updated.", False)
        else:
            self.config = config
            self.config_manager._update_config(self.config)
            self.printer_data = printer_data
            self.config_manager._showPopUp("success", "Saved Data", "Data was updated", True)
            
    
        #self._logger.info("Saved self.config: " + str(self.config))
        #self._logger.info("Saved self.printer: " + str(self.printer_data))
    
    def on_event(self, event, payload):
        self._logger.info(f"Handling event : {event}")    
        self._logger.info(payload)    

        if event == Events.CLIENT_OPENED:
            if self.config["plugin_check_activated"]:
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
            #self.config["plugin_check_activated"] = False
            #self._settings.set(['plugin_check_activated'], False)
            #self._settings.save()
            self.config["plugin_check_activated"] = False
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

__plugin_name__ = "ExternalPrintHistory"
__plugin_pythoncompat__ = ">=3,<4"

def __plugin_load__():
    """
    Initializes the plugin by creating an instance of the ExternalPrintHistoryPlugin class and setting up the necessary hooks.
    This function is automatically called when the plugin is loaded.

    Parameters:
        None

    Returns:
        None
    """
    global __plugin_implementation__
    __plugin_implementation__ = ExternalPrintHistoryPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }