# coding=utf-8
from __future__ import absolute_import

from ..common.SettingsKeys import SettingsKeys

class ConfigurationManager():

    def load_config(self):
        """
        Loads the plugin configuration from the configuration file.

        This method retrieves the current plugin configuration by loading
        it from the configuration file.

        Returns:
            dict: A dictionary containing the plugin configuration.
        """
        config = {
            SettingsKeys.PRINTER_ID: self._settings.get_int([SettingsKeys.PRINTER_ID]),
            SettingsKeys.CURRENCY: self._settings.get([SettingsKeys.CURRENCY]),
            SettingsKeys.ELECTRICITY_COST: self._settings.get_float([SettingsKeys.ELECTRICITY_COST]),
            SettingsKeys.DB_HOST: self._settings.get([SettingsKeys.DB_HOST]),
            SettingsKeys.DB_USER: self._settings.get([SettingsKeys.DB_USER]),
            SettingsKeys.DB_PASSWORD: self._settings.get([SettingsKeys.DB_PASSWORD]),
            SettingsKeys.DB_DATABASE: self._settings.get([SettingsKeys.DB_DATABASE]),
            SettingsKeys.DB_PORT: self._settings.get_int([SettingsKeys.DB_PORT]),
            SettingsKeys.PLUGIN_DEPENDENCY_CHECK: self._settings.get_boolean([SettingsKeys.PLUGIN_DEPENDENCY_CHECK]),
            SettingsKeys.SPOOLMAN_URL: self._settings.get([SettingsKeys.SPOOLMAN_URL]),
            SettingsKeys.SPOOLMAN_CERT_PEM_PATH: self._settings.get([SettingsKeys.SPOOLMAN_CERT_PEM_PATH]),
            SettingsKeys.SPOOLMAN_CERT_VERIFY_ENABLED: self._settings.get_boolean([SettingsKeys.SPOOLMAN_CERT_VERIFY_ENABLED])
        }

        return config

    def get_plugin_dependency_check(self):
        """
        Retrieves the state of the plugin check.

        Returns:
            bool: True if the plugin check is activated, False otherwise.
        """
        # Return the current state of the plugin check
        return self._settings.get_boolean([SettingsKeys.PLUGIN_DEPENDENCY_CHECK])

    def get_printer_id(self):
        """
        Retrieves the printer ID from the settings.

        Returns:
            int: The printer ID if set, otherwise returns 0.
        """
        # Get the printer ID from settings or return 0 if not set
        return self._settings.get([SettingsKeys.PRINTER_ID]) or 0
            
    def update_dictionaries(self, data, config_data={}, printer_data={}):
        """
        Updates the configuration and printer data dictionaries.

        This method checks the given data against predefined keys for printer and 
        configuration settings. If a key is present in the data, 
        it updates the respective dictionary with the key-value pair.

        Args:
            data (dict): The data containing potential updates for the dictionaries.
            config_data (dict, optional): The configuration dictionary to update. Defaults to {}.
            printer_data (dict, optional): The printer data dictionary to update. Defaults to {}.

        Returns:
            tuple: A tuple containing the updated config_data and printer_data dictionaries.
        """

        # List of keys to check for printer data
        keys_printer_to_check = [
            "printer_name",
            "printer_model",
            "printer_brand",
            "printer_power_consumption",
            "printer_purchase_price",
            "printer_estimated_lifespan",
            "printer_maintenance_costs"
        ]
        
        # List of keys to check for configuration data
        keys_config_to_check = [
            "db_user",
            "db_password",
            "db_port",
            "db_host",
            "db_database",
            "currency",
            "electricity_cost",
            "plugin_dependency_check",
            "spoolman_url",
            "spoolman_cert_verify_enabled",
            "spoolman_cert_pem_path"
        ]
        
        # Update printer data if key is present in data
        for key in keys_printer_to_check:
            if key in data:
                printer_data[key] = data.get(key)
                
        # Update configuration data if key is present in data
        for key in keys_config_to_check:
            if key in data:
                config_data[key] = data.get(key)
                
        return config_data, printer_data

    def show_popup(self, popupType, title, message, hide):
        """
        Displays a pop up message to the user.

        This method sends a message to the plugin manager to display a pop up
        to the user. The pop up type, title, and message are passed as parameters.
        The hide parameter is used to determine if the pop up should be displayed
        or hidden.

        Args:
            popupType (str): The type of the pop up. Can be "success", "error", or "info".
            title (str): The title of the pop up.
            message (str): The message to be displayed in the pop up.
            hide (bool): If True, the pop up will be hidden. If False, the pop up
                will be displayed.
        """
        self._plugin_manager.send_plugin_message(self._identifier, dict(action="showPopUp", popupType=popupType, title=title, message=message, hide=hide))