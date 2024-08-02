import base64
import os

class Print:
    def __init__(self, plugin, logger):
        self.logger = logger
        self.plugin = plugin