import base64
import binascii
import json
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes

class ConfigurationManager:
    def __init__(self, plugin, logger):
        """
        Initializes a new instance of the ConfigurationManager class.

        Parameters:
            plugin (object): The plugin instance associated with this configuration manager.
            logger (object): The logger instance used for logging events and errors.

        Returns:
            None
        """
        self.logger = logger
        self.plugin = plugin
        
        self.key_file_path = None
        self.salt_file_path = None
        self.config_folder_path = None
        self.config_file_path = None
        
    def _create_config_file(self):
        """
        The `_create_config_file` function creates a configuration file with default settings if it does
        not already exist.
        """
        self.config_folder_path = self.plugin.get_plugin_data_folder()
        self.config_file_path = os.path.join(self.config_folder_path, "config.json")
    
        if not os.path.exists(self.config_folder_path):
            os.makedirs(self.config_folder_path)
        if not os.path.exists(self.config_file_path):
            try:
                with open(self.config_file_path, 'w') as config_file:
                    config_file.write(json.dumps(self._get_default_config(), indent=4))
            except Exception as e:
                self.logger.error(f"Error creating configuration file: {e}")

    def _get_default_config(self):
        return {
            "db_user": "",
            "db_password": "",
            "db_host": "",
            "db_port": 3306,
            "db_database": "",
            "printer_id": 0,
            "currency": "\u20ac",
            "electricity_cost": 0.0,
            "plugin_check_activated": True
        }

    def _get_printer_data(self):
        return {
        "printer_name": "",
        "printer_brand": "",
        "printer_model": "",
        "printer_power_consumption": 0,
        "printer_purchase_price": 0,
        "printer_estimated_lifespan": 0,
        "printer_maintenance_costs": 0 
        }
                
    def _load_existing_config(self):
        """
        The function `_load_existing_config` reads and returns a JSON configuration file, logging an error
        if there is an issue.
        :return: The method `_load_existing_config` is returning the loaded JSON data from the configuration
        file if the file is successfully opened and read. If an exception occurs during the process (such as
        file not found or invalid JSON format), it logs an error message using the logger and returns
        `None`.
        """
        try:
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            return None
            
    def _update_config(self, data):
        """
        Updates the existing configuration with the provided data.
        :param data: A dictionary containing the updated configuration settings.
        :return: None
        """
        updated_settings = self._load_existing_config()
        updated_settings.update(data)

        try:
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(updated_settings, f, indent=4)
            #self.logger.info("Configuration updated successfully.")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    #def _initialize_settings(self, settings):
    #    self.settings = settings
    
    def _initialize_config_files(self):
        """
        The function `_initialize_config_files` initializes key, salt, and creates a configuration file.
        """
        self._initialize_key_and_salt()
        self._create_config_file()
        
    def _initialize_key_and_salt(self):
        """
        Initializes the encryption key and salt for the plugin.

        This function checks if the encryption key and salt files exist in the plugin's data folder. If they do not exist,
        it generates a new encryption key and salt, saves them to the respective files, and logs the successful
        generation. If the files already exist, it reads the encryption key and salt from the files.
        Parameters:
            self (ConfigurationManager): The instance of the ConfigurationManager class.
        Returns:
            None
        Raises:
            Exception: If there is an error generating or loading the encryption key and salt.

        """
        self.key_file_path = os.path.join(self.plugin.get_plugin_data_folder(), 'key.key')
        self.salt_file_path = os.path.join(self.plugin.get_plugin_data_folder(), 'salt.key')

        if not (os.path.exists(self.key_file_path) and os.path.exists(self.salt_file_path)):
            self.salt = get_random_bytes(16)
            self.key = scrypt(b'some_password', self.salt, 32, N=2**14, r=8, p=1)
            try:
                with open(self.key_file_path, 'wb') as key_file:
                    key_file.write(self.key)
                with open(self.salt_file_path, 'wb') as salt_file:
                    salt_file.write(self.salt)
                self.logger.info("Generated and saved new encryption key and salt")
            except Exception as e:
                self.logger.error(f"Error generating key and salt: {e}")
        else:
            try:
                with open(self.key_file_path, 'rb') as key_file:
                    self.key = key_file.read()
                with open(self.salt_file_path, 'rb') as salt_file:
                    self.salt = salt_file.read()
            except Exception as e:
                self.logger.error(f"Error loading key and salt: {e}")

    def _encrypt(self, password):
        """
        Encrypts a given password using AES encryption with EAX mode.

        Parameters:
            password (str): The password to be encrypted.

        Returns:
            str: The encrypted password as a base64 encoded string.
        """
        cipher = AES.new(self.key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(password.encode())
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

    def _decrypt(self, encrypted_password):
        """
        Decrypts an encrypted password using AES encryption with EAX mode.

        Args:
            encrypted_password (str): The encrypted password to be decrypted.

        Returns:
            str: The decrypted password as a string.

        Raises:
            ValueError: If the encrypted password is not a valid base64 encoded string.
            KeyError: If the decryption key is not valid.
            binascii.Error: If the ciphertext is not valid.º

        """
        try:
            data = base64.b64decode(encrypted_password)
            nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
            cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag).decode()
        except (ValueError, KeyError, binascii.Error) as e:
            self.logger.error(f"Decryption failed: {e}")
            return None

    #def _get_database_settings(self):
    #    db_config = {
    #    'db_host': self.settings.get(['db_host']) or 'HOST',
    #    'db_user': self.settings.get(['db_user']) or 'USER',
    #    'db_password': self.settings.get(['db_password']) or 'PASSWORD',
    #    'db_database': self.settings.get(['db_password']) or 'DATABASE',
    #    'db_port': self.settings.get(['db_port']) or 3306
    #    }
    #    
    #    return db_config
    
    #def _get_settings(self):
    #    config = {}
    #    config["printer_id"] = self.settings.get(['printer_id']) or 0
    #    config["currency"] = self.settings.get(['currency']) or "\u20ac"
    #    config["electricity_cost"] = self.settings.get(['electricity_cost']) or 0.0
    #    config["plugin_check_activated"] = self.settings.get_boolean(['plugin_check_activated']) or True    
    #    
    #    return config
    
    #def _save_setting(self, data):
    #        config = {}
    #        
    #        for key, value in data.items():
    #            self.settings.set([str(key)], value)
    #            config[key] = value
    #        
    #        self.settings.save()
    #        
    #        for key in data.keys():
    #            saved_value = self.settings.get([str(key)])
    #            self.logger.info(f"Saved setting: {key} = {saved_value}")
    #        
    #        self.logger.info(f"Saved settings in config: {config}")
    #        
    #        return config
    
    def _transform_printer_data(self, data):
        config = {}
        printer_info = data.get('printer_data', {})
        config["printer_name"] = printer_info.get("name", "")
        config["printer_model"] = printer_info.get("model", "")
        config["printer_brand"] = printer_info.get("brand", "")
        config["printer_power_consumption"] = printer_info.get("power_consumption", 0)
        config["printer_purchase_price"] = printer_info.get("purchase_price", 0)
        config["printer_estimated_lifespan"] = printer_info.get("estimated_lifespan", 0)
        config["printer_maintenance_costs"] = printer_info.get("maintenance_costs", 0)
        
        return config
    
    def _update_dictionaries_on_save(self, data, config, printer_data):
        keys_printer_to_check = [
        "printer_name",
        "printer_model",
        "printer_brand",
        "printer_power_consumption",
        "printer_purchase_price",
        "printer_estimated_lifespan",
        "printer_maintenance_costs"
        ]
        keys_config_to_check = [
        "db_user",
        "db_password",
        "db_port",
        "db_host",
        "db_database",
        "currency",
        "electricity_cost",
        "plugin_check_activated"
        ]
        
        for key in keys_printer_to_check:
            if key in data:
                printer_data[key] = data.get(key)
                
        for key in keys_config_to_check:
            if key in data:
                config[key] = data.get(key)
                
        #self.logger.info("Saved config: " + str(config))
        #self.logger.info("Saved printer: " + str(printer_data))
        
        return config, printer_data
    
        # popupType = 'notice', 'info', 'success', or 'error'.
    def _showPopUp(self, popupType, title, message, hide):
            self.plugin._plugin_manager.send_plugin_message(self.plugin._identifier, dict(action="showPopUp", popupType=popupType, title=title, message=message, hide=hide))