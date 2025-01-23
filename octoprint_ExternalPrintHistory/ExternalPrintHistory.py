# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

from octoprint.events import Events
from .modules.eventPrinter import EventPrinter
from .modules.databaseManager import DatabaseManager
from .modules.configurationManager import ConfigurationManager
from .modules.PluginAPI import PluginAPI
from .modules.pluginChecker import PluginChecker
from .common.SettingsKeys import SettingsKeys
from .modules.SpoolmanConnector import SpoolmanConnector
from .modules.printerUtil import PrinterUtil

class ExternalPrintHistoryPlugin(octoprint.plugin.StartupPlugin,
                                octoprint.plugin.TemplatePlugin,
                                octoprint.plugin.SettingsPlugin,
                                octoprint.plugin.AssetPlugin,
                                octoprint.plugin.EventHandlerPlugin,
                                octoprint.plugin.SimpleApiPlugin,
                                octoprint.plugin.BlueprintPlugin,
                                DatabaseManager,
                                SpoolmanConnector,
                                ConfigurationManager,
                                PluginChecker,
                                PluginAPI,
                                PrinterUtil,
                                EventPrinter,
                                ):
    
    def initialize(self) -> None:
        """
        Initializes the plugin.

        Sets the flag indicating that the plugin is initialized to True, and
        calls initialize_print to initialize the print data dictionaries.

        :return: None
        """
        self._isInitialized = True
        self.initialize_print()
                
    def on_startup(self, host, port):
        # Load the configuration settings from the settings file.
        """
        Called by OctoPrint when the server is fully started up and all plugins have been loaded.

        Loads the configuration settings from the settings file and sets the database connection, then tests it.

        :param host: (not used)
        :param port: (not used)
        """
        settings = self.load_config()
        
        # Set the database connection and test it.
        self.set_and_test_connection(settings)

    #def on_after_startup(self):
        
    #def on_shutdown(self):
        
    def get_settings_defaults(self):
        """
        Returns the default settings for the plugin.
        
        :return: A dictionary containing the default configuration settings.
        """
        settings = {
            # Enable plugin dependency check. This setting is used to check if the
            # required plugins are installed and enabled.
            SettingsKeys.PLUGIN_DEPENDENCY_CHECK: True,
            # The ID of the printer.
            SettingsKeys.PRINTER_ID: 0,
            # The username to use when connecting to the database.
            SettingsKeys.DB_USER: "",
            # The password to use when connecting to the database.
            SettingsKeys.DB_PASSWORD: "",
            # The hostname or IP address of the database.
            SettingsKeys.DB_HOST: "",
            # The name of the database to use.
            SettingsKeys.DB_DATABASE: "",
            # The port to use when connecting to the database.
            SettingsKeys.DB_PORT: 3306,
            # The currency symbol to use when displaying costs.
            SettingsKeys.CURRENCY: "\u20ac",
            # The URL of the Spoolman server.
            SettingsKeys.SPOOLMAN_URL: "",
            # Whether to verify the Spoolman server's SSL certificate.
            SettingsKeys.SPOOLMAN_CERT_VERIFY_ENABLED: False,
            # The path to the Spoolman server's SSL certificate.
            SettingsKeys.SPOOLMAN_CERT_PEM_PATH: "",
        }
        
        return settings

    def on_settings_load(self):
        """
        Loads and validates the plugin's settings.

        This method retrieves the current configuration from the settings file,
        establishes a connection to the database to ensure the settings are valid,
        and returns the loaded settings.

        :return: A dictionary containing the current configuration settings.
        """
        # Load the current plugin configuration from the settings file
        settings = self.load_config()
        
        # Establish and validate the database connection with the loaded settings
        self.set_and_test_connection(settings)
        
        # Return the loaded configuration settings
        return settings
    
    def on_settings_save(self, data):
        """
        Saves the plugin's settings and updates the database connection accordingly.

        This method takes the new configuration data, updates the current configuration
        with the new data, tests the database connection with the updated settings, and
        saves the updated configuration to disk. If the database connection test fails
        or updating the printer configuration fails, a popup is shown to the user with
        an appropriate error message.

        :param data: The new configuration data to save.
        :return: None
        """

        config = self.load_config()
        updated_config, updated_printer_data = self.update_dictionaries(data)
        config.update(updated_config)
        
        if updated_printer_data:
            result = self.set_and_test_connection(config)
            
            if result.get("error"):
                self.show_popup("error", "Error saving data", "Data not updated.", False)
            else:
                # TODO: Implement the code to update the config with the returned printer_id
                result = self.update_insert_printer_config(updated_printer_data, self.get_printer_id())
                
                if result.get("error"):
                    self.show_popup("error", "Error saving data", "Printer configuration not updated.", False)
                else:
                    self.show_popup("success", "Data saved", "Printer configuration updated.", True)
                    config[SettingsKeys.PRINTER_ID] = result.get("printer_id")
        
        if data.get(SettingsKeys.ELECTRICITY_COST, False):
            config[SettingsKeys.ELECTRICITY_COST] = float(config[SettingsKeys.ELECTRICITY_COST])
        
        octoprint.plugin.SettingsPlugin.on_settings_save(self, config)

    #def register_custom_events(*args, **kwargs):
    #    return []
    
    def on_sentGCodeHook(self, comm_instance, phase, command, cmd_type, gcode, *args, **kwargs):
        """Handles GCODE commands sent by OctoPrint."""
        if self._printer.get_state_id() == "PRINTING":
            if command.startswith("T"):
                if len(command) > 1:
                    self.select_tool(command[1])
            elif command.startswith(("M104", "M109")):
                self.update_nozzle_temperature()
            elif command.startswith(("M140", "M190")):
                self.update_bed_temperature()
            elif command.startswith("M141"):
                self.update_chamber_temperature()

        if self._isInitialized:
            self.handle_printing_gcode(command)
        
    def on_event(self, event, payload):
        """
        Handles events fired by the OctoPrint server.

        This method handles the following events:
        - CLIENT_OPENED: Initializes the plugin and checks if the third-party
        - PRINTER_STATE_CHANGED: Updates the printer state.
        - PRINT_STARTED: Starts a new print job.
        - PRINT_CANCELLED: Cancels a print job.
        - PRINT_DONE: Finishes a print job.
        - PRINT_FAILED: Fails a print job.
        - PRINT_PAUSED: Pauses a print job.
        - PRINT_RESUMED: Resumes a print job.
        - DisplayLayerProgress_layerChanged: Updates the layer progress.
        - DisplayLayerProgress_heightChanged: Updates the height progress.
        - plugin_Spoolman_spool_usage_committed: Updates the spool usage.
        - plugin_Spoolman_spool_usage_committed_recovery: Recovers the spool usage from an error.
        - plugin_Spoolman_spool_file_selected: Updates the spool file selected.

        Args:
            event (str): The event name.
            payload (dict): The event payload.
        """
        #self._logger.info(f"on_event: {event}")
        #self._logger.info(payload)
        
        if event == Events.CLIENT_OPENED:            
            #self.handle_client_opened(payload)
            if self._settings.get([SettingsKeys.PLUGIN_DEPENDENCY_CHECK]):
                self.checkAndLoadThirdPartyPluginInfos()
                    
        elif event == Events.PRINTER_STATE_CHANGED:
            #self.handle_printer_state_changed(payload)
            pass
                
        elif event == Events.PRINT_STARTED:
            #self.handle_print_started(payload)
            pass
        
        elif event == Events.PRINT_CANCELLED:
            self.handle_print_cancelled(payload)
            
        elif event == Events.PRINT_DONE:
            self.handle_print_done(payload)
            
        elif event == Events.PRINT_FAILED:
            self.handle_print_failed(payload)
            
        elif event == Events.PRINT_PAUSED:  
            self.handle_print_paused(payload)
        
        elif event == Events.PRINT_RESUMED:
            self.handle_print_resumed(payload)
        
        elif event == Events.FILE_DESELECTED:
            self.handle_file_deselected(payload)
        
        elif event == Events.FILE_SELECTED:
            self.handle_file_selected(payload)
            
        elif event == 'DisplayLayerProgress_heightChanged':
            self.handle_height_changed(payload)
            
    def get_template_configs(self):
        """
        Returns the template configurations for the plugin.

        This method defines the various template configurations used by the plugin
        for settings, tabs, and sidebars. Each configuration specifies the type of 
        template, the name to be displayed, whether custom bindings are used, and 
        the path to the Jinja2 template file.

        Returns:
            list: A list of dictionaries, each containing template configuration 
            details such as type, name, custom bindings, and template path.
        """

        return [
            dict(
                type="settings",
                name="External Print History",
                custom_bindings=True,
                template="ExternalPrintHistory_settings.jinja2"
            ),
            dict(
                type="tab",
                name="External Print History",
                custom_bindings=True,
                template="ExternalPrintHistory_tab.jinja2"
            ),
            dict(
                type="sidebar",
                name="External Print History",
                custom_bindings=True,
                template="ExternalPrintHistory_sidebar.jinja2"
            ), 
        ]
        
    def get_assets(self):
        """
        Returns the assets required by the plugin.

        This method provides the list of JavaScript and CSS files that are necessary
        for the plugin's functionality. These assets are used in various parts of
        the plugin such as API interactions, cost estimations, plugin checks, settings,
        sidebar, and main functionality.

        Returns:
            dict: A dictionary containing lists of JavaScript and CSS files 
            used by the plugin.
        """

        return dict(
            # List of JavaScript files that are used by the plugin
            js = [
                # JavaScript file containing the cost estimate calculations
                "js/ExternalPrintHistory_costEstimate.js",
                # JavaScript file containing the plugin check dialog
                "js/ExternalPrintHistory_pluginCheckDialog.js",
                # JavaScript file containing the plugin settings
                "js/ExternalPrintHistory_settings.js",
                "js/ExternalPrintHistory_sidebar.js",
                # JavaScript file containing the main code of the plugin
                "js/ExternalPrintHistory.js",
            ],
            # List of CSS files that are used by the plugin
            css = [
                # CSS file containing the styles for the plugin
                "css/ExternalPrintHistory.css"
            ]
        )

    
    #def on_settings_migrate(self, target, current=None):

    def get_version(self):
        """
        Retrieves the current version of the plugin.

        Returns:
            str: The current plugin version as a string.
        """

        return self._plugin_version

    def get_update_information(self):
        """
        Retrieves information about plugin updates.

        This method provides information about the latest version of the plugin, the
        currently installed version, and the URL of the plugin's repository.

        Returns:
            dict: A dictionary containing the plugin's name, display name, type of update
            information, repository user name, repository name, the current version, and
            the URL of the repository.
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
