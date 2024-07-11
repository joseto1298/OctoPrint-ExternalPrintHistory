# coding=utf-8
from __future__ import absolute_import
import os

import octoprint.plugin
from .history_manager import HistoryManager

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin


class PrinterhistoryPlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.EventHandlerPlugin
):


    def __init__(self):
        self._history_file = self._get_history_file_path()
        self._history_manager = HistoryManager(self._history_file)


    def _get_history_file_path(self):
        return os.path.join(octoprint.plugin.plugin_manager.get_plugin("Printerhistory Plugin").plugin_object.plugin_data_folder, "history.json")


    def on_print_started(self, printer, name, path):
        job = {
            "event": "print_started",
            "name": name,
            "path": path
        }
        self._history_manager.add_to_history(job)


    def on_print_done(self, printer, name, path, success):
        job = {
            "event": "print_done",
            "name": name,
            "path": path,
            "success": success
        }
        self._history_manager.add_to_history(job)


    def on_print_failed(self, printer, name, path):
        job = {
            "event": "print_failed",
            "name": name,
            "path": path
        }
        self._history_manager.add_to_history(job)


    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/printerHistory.js"],
            "css": ["css/printerHistory.css"],
            "less": ["less/printerHistory.less"]
        }
    
    
    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "printerHistory": {
                "displayName": "Printerhistory Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "joseto1298",
                "repo": "OctoPrint-Printerhistory",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/joseto1298/OctoPrint-Printerhistory/archive/{target_version}.zip",
            }
        }


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Printerhistory Plugin"


# Set the Python version your plugin is compatible with below. Recommended is Python 3 only for all new plugins.
# OctoPrint 1.4.0 - 1.7.x run under both Python 3 and the end-of-life Python 2.
# OctoPrint 1.8.0 onwards only supports Python 3.
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PrinterhistoryPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }

