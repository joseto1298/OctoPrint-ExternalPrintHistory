# coding=utf-8
from __future__ import absolute_import

from .ExternalPrintHistory import ExternalPrintHistoryPlugin

__plugin_name__ = "ExternalPrintHistory"
__plugin_version__ = "0.2.0"
__plugin_description__ = "Plugin integrating OctoPrint with external print history manager."
__plugin_pythoncompat__ = ">=3.7,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = ExternalPrintHistoryPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.gcode.sent": __plugin_implementation__.on_sentGCodeHook,
        "octoprint.events.register_custom_events": __plugin_implementation__.register_custom_events,
    }