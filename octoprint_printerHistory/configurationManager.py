import base64
import binascii
import json
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes

class ConfigurationManager:
    def __init__(self, plugin, logger):
        self.logger = logger
        self.plugin = plugin
        self.key_file_path = None
        self.salt_file_path = None
        self.config_file_path = None
        self.config_folder_path = None

    def _create_config_file(self):
        """
        Creates the configuration file if it does not exist.
        """
        self.config_folder_path = self.plugin.get_plugin_data_folder()
        self.config_file_path = os.path.join(self.config_folder_path, "config.json")

        if not os.path.exists(self.config_folder_path):
            os.makedirs(self.config_folder_path)
        if not os.path.exists(self.config_file_path):
            default_config = self._get_default_config()
            try:
                with open(self.config_file_path, 'w') as f:
                    json.dump(default_config, f, indent=4)
            except Exception as e:
                self.logger.error(f"Error creating configuration file: {e}")

    def _get_default_config(self):
        """
        Returns the default configuration values.
        """
        return {
            "db_user": "user",
            "db_password": "password",
            "db_host": "host",
            "db_port": "3306",
            "db_database": "database",
            "printer_id": 0,
            "printer_name": "name",
            "printer_model": "model",
            "printer_brand": "brand",
            "printer_power_consumption": 0.00,
        }

    def _initialize_config_files(self):
        """
        Initializes and creates necessary configuration and key files if they do not exist.
        """
        self._initialize_key_and_salt()
        self._create_config_file()

    def _load_existing_config(self):
        """
        Loads the existing configuration from the configuration file.
        """
        try:
            with open(self.config_file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            return None
            
    def _update_config(self, data):
        """
        Updates the configuration with new data.
        """
        try:
            with open(self.config_file_path, 'w') as f:
                json.dump(data, f, indent=4)
            self.logger.info("Configuration updated successfully.")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def _process_database_changes(self, data, current_config):
        """
        Processes changes in database configuration and determines if updates are needed.
        """
        db_keys = ['db_user', 'db_password', 'db_host', 'db_port', 'db_database']
        updates = {key: data.get(key, current_config.get(key)) for key in db_keys}
        changes = {key: value for key, value in updates.items() if value != current_config.get(key)}

        return bool(changes)

    def _process_printer_changes(self, data, current_config):
        """
        Processes changes in printer configuration and determines if updates are needed.
        """
        printer_keys = ['printer_id', 'printer_name', 'printer_model', 'printer_brand', 'printer_power_consumption']
        updates = {key: data.get(key, current_config.get(key)) for key in printer_keys}
        changes = {key: value for key, value in updates.items() if value != current_config.get(key)}

        return bool(changes)

    def _initialize_key_and_salt(self):
        """
        Loads or generates encryption key and salt.
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
        """
        cipher = AES.new(self.key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(password.encode())
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

    def _decrypt(self, encrypted_password):
        """
        Decrypts an encrypted password using AES decryption with EAX mode.
        """
        try:
            data = base64.b64decode(encrypted_password)
            nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
            cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag).decode()
        except (ValueError, KeyError, binascii.Error) as e:
            self.logger.error(f"Decryption failed: {e}")
            return None
