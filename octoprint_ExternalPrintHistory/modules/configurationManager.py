# coding=utf-8
from __future__ import absolute_import

import base64
import binascii
import os
from cryptography.fernet import Fernet
from ..common.SettingsKeys import SettingsKeys

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes

class ConfigurationManager():
    def __init__(self, plugin, _logger):
        self._logger = _logger
        self.plugin = plugin
        self.key_file_path = None
        self.salt_file_path = None       
        
    def _load_config(self):
        config = {}
        config[SettingsKeys.PRINTER_ID] = self.plugin._settings.get([SettingsKeys.PRINTER_ID]) or 0
        config[SettingsKeys.CURRENCY] = self.plugin._settings.get([SettingsKeys.CURRENCY]) or "\u20ac"
        config[SettingsKeys.ELECTRICITY_COST] = self.plugin._settings.get([SettingsKeys.ELECTRICITY_COST]) or 0.0
        config[SettingsKeys.DB_HOST] = self.plugin._settings.get([SettingsKeys.DB_HOST]) or ''
        config[SettingsKeys.DB_USER] = self.plugin._settings.get([SettingsKeys.DB_USER]) or ''
        config[SettingsKeys.DB_PASSWORD] = self.plugin._settings.get([SettingsKeys.DB_PASSWORD]) or ''
        config[SettingsKeys.DB_DATABASE] = self.plugin._settings.get([SettingsKeys.DB_DATABASE]) or ''
        config[SettingsKeys.DB_PORT] = self.plugin._settings.get([SettingsKeys.DB_PORT]) or 3306
        config[SettingsKeys.PLUGIN_DEPENDENCY_CHECK] = self.plugin._settings.get([SettingsKeys.PLUGIN_DEPENDENCY_CHECK])
        
        if config[SettingsKeys.DB_PASSWORD] != '':
            config[SettingsKeys.DB_PASSWORD] = self._decrypt(config[SettingsKeys.DB_PASSWORD])
        
        if config[SettingsKeys.PLUGIN_DEPENDENCY_CHECK] is None:
            config[SettingsKeys.PLUGIN_DEPENDENCY_CHECK] = True
        
        return config

    def _get_plugin_dependency_check(self):
        if self.plugin._settings.get([SettingsKeys.PLUGIN_DEPENDENCY_CHECK]) == None:
            return True
        return self.plugin._settings.get_boolean([SettingsKeys.PLUGIN_DEPENDENCY_CHECK])

    def _get_printer_id(self):
        return self.plugin._settings.get([SettingsKeys.PRINTER_ID]) or 0
            
    def _update_dictionaries(self, data, config_data={}, printer_data={}):        
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
        "plugin_dependency_check"
        ]
        
        for key in keys_printer_to_check:
            if key in data:
                printer_data[key] = data.get(key)
                
        for key in keys_config_to_check:
            if key in data:
                config_data[key] = data.get(key)
                
        return config_data, printer_data
    
        # popupType = 'notice', 'info', 'success', or 'error'.
    def _showPopUp(self, popupType, title, message, hide):
            self.plugin._plugin_manager.send_plugin_message(self.plugin._identifier, dict(action="showPopUp", popupType=popupType, title=title, message=message, hide=hide))
            
    def _initialize_key_and_salt(self):
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
                self._logger.info("Generated and saved new encryption key and salt")
            except Exception as e:
                self._logger.error(f"Error generating key and salt: {e}")
        else:
            try:
                with open(self.key_file_path, 'rb') as key_file:
                    self.key = key_file.read()
                with open(self.salt_file_path, 'rb') as salt_file:
                    self.salt = salt_file.read()
            except Exception as e:
                self._logger.error(f"Error loading key and salt: {e}")
                
    def _encrypt(self, password):
        cipher = AES.new(self.key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(password.encode())
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode()
    
    def _decrypt(self, encrypted_password):
        try:
            data = base64.b64decode(encrypted_password)
            nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
            cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag).decode()
        except (ValueError, KeyError, binascii.Error) as e:
            self._logger.error(f"Decryption failed: {e}")
            return None