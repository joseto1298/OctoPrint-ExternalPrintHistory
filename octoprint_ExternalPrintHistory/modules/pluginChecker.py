# coding=utf-8
from __future__ import absolute_import

import logging
import semantic_version
from ..common.PluginsKeys import PluginsKeys

class PluginChecker():
    
    PLUGIN_DEPENDENCY_CHECK = "pluginCheckActivated"

    """
    Checks if the required plugins are installed and enabled.

    The checker is responsible for retrieving the state and implementation of the
    required plugins. The state is whether the plugin is enabled or not, and the
    implementation is the actual plugin implementation.
    """

    def __init__(self):
        """
        Initializes the plugin checker.

        All the plugin implementations are set to None initially.
        The plugin states are set to None initially as well.
        """
        self._pluginImplementation = None

        # The implementation of the DisplayLayerProgress plugin
        self._displayLayerProgressPluginImplementation = None
        # The state of the DisplayLayerProgress plugin. True if enabled, False otherwise.
        self._displayLayerProgressPluginImplementationState = None

        # The implementation of the UltimakerFormatPackage plugin
        self._ultimakerFormatPluginImplementation = None
        # The state of the UltimakerFormatPackage plugin. True if enabled, False otherwise.
        self._ultimakerFormatPluginImplementationState = None

        # The implementation of the PrusaSlicerThumbnails plugin
        self._prusaSlicerThumbnailsPluginImplementation = None
        # The state of the PrusaSlicerThumbnails plugin. True if enabled, False otherwise.
        self._prusaSlicerThumbnailsPluginImplementationState = None

        # The implementation of the PrintTimeGenius plugin
        self._PrintTimeGeniusPluginImplementationStateImplementation = None
        # The state of the PrintTimeGenius plugin. True if enabled, False otherwise.
        self._PrintTimeGeniusPluginImplementationState = None
        
    def checkAndLoadThirdPartyPluginInfos(self):
        """
        Checks if the required plugins are installed and enabled.

        Plugins checked are:
        - DisplayLayerProgress
        - UltimakerFormatPackage (cura thumbnails)
        - PrusaSlicerThumbnails
        - PrintTimeGenius

        The function retrieves the state (enabled or disabled) and the
        implementation of the plugins. If any of the plugins are not
        installed or enabled, it will show a message in the Plugin Check tab.

        The plugin versions are also checked to ensure they are at least
        at the minimum required version. If any of the plugins are not
        at the minimum required version, it will show a message in the
        Plugin Check tab.
        """

        # Check DisplayLayerProgress plugin
        pluginInfo = self._get_plugin_information(PluginsKeys.PLUGIN_DISPLAY_LAYER_PROGRESS)
        self._displayLayerProgressPluginImplementationState = pluginInfo[0]
        self._displayLayerProgressPluginImplementation = pluginInfo[1]
        displayLayerCurrentVersion = pluginInfo[2]
        displayLayerRequiredVersion = pluginInfo[3]

        # Check UltimakerFormatPackage plugin
        pluginInfo = self._get_plugin_information(PluginsKeys.PLUGIN_ULTIMAKER_FORMAT_PACKAGE)
        self._ultimakerFormatPluginImplementationState = pluginInfo[0]
        self._ultimakerFormatPluginImplementation = pluginInfo[1]
        ultimakerCurrentVersion = pluginInfo[2]
        ultimakerRequiredVersion = pluginInfo[3]

        # Check PrusaSlicerThumbnails plugin
        pluginInfo = self._get_plugin_information(PluginsKeys.PLUGIN_PRUSA_SLICER_THUMNAIL)
        self._prusaSlicerThumbnailsPluginImplementationState = pluginInfo[0]
        self._prusaSlicerThumbnailsPluginImplementation = pluginInfo[1]
        prusaSlicerCurrentVersion = pluginInfo[2]
        prusaSlicerRequiredVersion = pluginInfo[3]

        # Check PrintTimeGenius plugin
        pluginInfo = self._get_plugin_information(PluginsKeys.PLUGIN_PRINT_TIME_GENIUS)
        self._printTimeGeniusPluginImplementationState = pluginInfo[0]
        self._printTimeGeniusPluginImplementation = pluginInfo[1]
        printTimeGeniusCurrentVersion = pluginInfo[2]
        printTimeGeniusRequiredVersion = pluginInfo[3]

        # Log plugin-state information
        self._logger.info("Plugin-State information:\n"
                            "| DisplayLayerProgress=" + self._displayLayerProgressPluginImplementationState + " (" + str(displayLayerCurrentVersion) + ")\n"
                            "| UltimakerFormat=" + self._ultimakerFormatPluginImplementationState + " (" + str(ultimakerCurrentVersion) + ")\n"
                            "| PrusaSlicerThumbnail=" + self._prusaSlicerThumbnailsPluginImplementationState + " (" + str(prusaSlicerCurrentVersion) + ")\n"
                            "| PrintTimeGenius=" + self._printTimeGeniusPluginImplementationState + " (" + str(printTimeGeniusCurrentVersion) + ")\n"                            
                            )

        if (self._displayLayerProgressPluginImplementation is None
        or self._ultimakerFormatPluginImplementation is None
        or self._prusaSlicerThumbnailsPluginImplementation is None
        or self._printTimeGeniusPluginImplementationState is None):
                    
            missingMessage = ""

            if self._displayLayerProgressPluginImplementation is None:
                missingMessage += (
                    "<li><a target='_newTab' href='https://plugins.octoprint.org/plugins/DisplayLayerProgress/'>"
                    f"DisplayLayerProgress ({displayLayerRequiredVersion}+)</a> (<b>{self._displayLayerProgressPluginImplementationState}</b>)</li>"
                )

            if self._ultimakerFormatPluginImplementation is None:
                missingMessage += (
                    "<li><a target='_newTab' href='https://plugins.octoprint.org/plugins/UltimakerFormatPackage/'>"
                    f"Cura Thumbnails ({ultimakerRequiredVersion}+)</a> (<b>{self._ultimakerFormatPluginImplementationState}</b>)</li>"
                )

            if self._prusaSlicerThumbnailsPluginImplementation is None:
                missingMessage += (
                    "<li><a target='_newTab' href='https://plugins.octoprint.org/plugins/prusaslicerthumbnails/'>"
                    f"PrusaSlicer Thumbnails ({prusaSlicerRequiredVersion}+)</a> (<b>{self._prusaSlicerThumbnailsPluginImplementationState}</b>)</li>"
                )
            
            if self._printTimeGeniusPluginImplementation is None:
                missingMessage += (
                    "<li><a target='_newTab' href='https://plugins.octoprint.org/plugins/PrintTimeGenius/'>"
                    f"PrintTimeGenius ({printTimeGeniusRequiredVersion}+)</a> (<b>{self._printTimeGeniusPluginImplementationState}</b>)</li>"
                )
                                
            if missingMessage != "":
                missingMessage = f"<ul>{missingMessage}</ul>"
                self._plugin_manager.send_plugin_message(self._identifier, dict(action="PluginCheck", message=missingMessage))
            
    # get the plugin with status information
    # [0] == status-string
    # [1] == implementaiton of the plugin
    # [2] == version of the plugin, as str like 3.3.0
    # [3] == requiredVersion of the plugin, as str like 1.3.0
    def _get_plugin_information(self, pluginInfo):
        """
        Retrieves information about a specific plugin.

        Args:
            pluginInfo (dict): A dictionary containing the plugin's key and minimum required version.
            
        Returns:
            list: A list containing the status, implementation, version, and required version of the plugin.
            Status can be 'enabled', 'disabled', 'incompatible', 'missing', or 'wrong version'.
        """
        pluginKey = pluginInfo["key"]
        requiredVersion = pluginInfo["minVersion"]

        status = None
        implementation = None
        version = None

        # Check if the plugin is in the plugin manager
        if pluginKey in self._plugin_manager.plugins:
            plugin = self._plugin_manager.plugins[pluginKey]
            if plugin is not None:
                if plugin.enabled:
                    status = "enabled"
                    # Check if the plugin is marked as incompatible
                    if hasattr(plugin, 'incompatible'):
                        if not plugin.incompatible:
                            implementation = plugin.implementation
                        else:
                            status = "incompatible"
                    else:
                        implementation = plugin.implementation
                else:
                    status = "disabled"
                version = plugin.version
        else:
            status = "missing"

        # Compare the current version with the required version
        if requiredVersion is not None and version is not None:
            canBeUsed = False
            try:
                # Convert versions to comparable semantic versions
                comparableVersion = self._get_comparable_version_semantic(version)
                comparableRequiredVersion = self._get_comparable_version_semantic(requiredVersion)
                # Determine if the current version meets the minimum required version
                canBeUsed = comparableVersion >= comparableRequiredVersion
            except ValueError:
                logging.exception(f"Something is wrong with the {pluginKey} version numbers")

            if not canBeUsed:
                status = "wrong version"
                implementation = None

        return [status, implementation, version, requiredVersion]
    
    def _get_comparable_version_semantic(self, version_string, force_base=True):
        """
        Returns the comparable version of the given version string.

        Converts the given version string into a comparable version using the
        semantic version library. If `force_base` is set to True, the resulting
        comparable version will be forced to have a base version (i.e. 3 parts).

        Args:
            version_string (str): The version string to be parsed.
            force_base (bool, optional): If True, the resulting comparable version will be forced to have a base version (i.e. 3 parts). Defaults to True.

        Returns:
            semantic_version.Version: The comparable version.

        Raises:
            ValueError: If the version string is invalid.
        """
        # Parse the version string using the semantic version library
        version = semantic_version.Version.coerce(version_string, partial=False)
        if force_base:
            # Force the version to have 3 parts (major, minor, patch)
            version_string = "{}.{}.{}".format(version.major, version.minor, version.patch)
            version = semantic_version.Version.coerce(version_string, partial=False)

        # Return the comparable version
        return version        
