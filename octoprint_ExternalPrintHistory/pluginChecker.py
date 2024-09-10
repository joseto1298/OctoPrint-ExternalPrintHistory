import logging
import semantic_version
from .SettingsKeys import SettingsKeys

class PluginChecker:
    
    PLUGIN_DEPENDENCY_CHECK = "pluginCheckActivated"

    def __init__(self, plugin, logger):
        self.logger = logger
        self.plugin = plugin
        
        self._pluginImplementation = None
        self._preHeatPluginImplementationState = None
        self._displayLayerProgressPluginImplementation = None
        self._displayLayerProgressPluginImplementationState = None
        self._ultimakerFormatPluginImplementation = None
        self._ultimakerFormatPluginImplementationState = None
        self._prusaSlicerThumbnailsPluginImplementation = None
        self._prusaSlicerThumbnailsPluginImplementationState = None

    def _checkAndLoadThirdPartyPluginInfos(self):
        pluginInfo = self._getPluginInformation(SettingsKeys.PLUGIN_PREHEAT)
        self._preHeatPluginImplementationState = pluginInfo[0]
        self._preHeatPluginImplementation = pluginInfo[1]
        preHeatCurrentVersion = pluginInfo[2]
        preHeatRequiredVersion = pluginInfo[3]

        pluginInfo = self._getPluginInformation(SettingsKeys.PLUGIN_DISPLAY_LAYER_PROGRESS)
        self._displayLayerProgressPluginImplementationState = pluginInfo[0]
        self._displayLayerProgressPluginImplementation = pluginInfo[1]
        displayLayerCurrentVersion = pluginInfo[2]
        displayLayerRequiredVersion = pluginInfo[3]

        pluginInfo = self._getPluginInformation(SettingsKeys.PLUGIN_ULTIMAKER_FORMAT_PACKAGE)
        self._ultimakerFormatPluginImplementationState = pluginInfo[0]
        self._ultimakerFormatPluginImplementation = pluginInfo[1]
        ultimakerCurrentVersion = pluginInfo[2]
        ultimakerRequiredVersion = pluginInfo[3]

        pluginInfo = self._getPluginInformation(SettingsKeys.PLUGIN_PRUSA_SLICER_THUMNAIL)
        self._prusaSlicerThumbnailsPluginImplementationState = pluginInfo[0]
        self._prusaSlicerThumbnailsPluginImplementation = pluginInfo[1]
        prusaSlicerCurrentVersion = pluginInfo[2]
        prusaSlicerRequiredVersion = pluginInfo[3]

        self.logger.info("Plugin-State information:\n"
                            "| PreHeat=" + self._preHeatPluginImplementationState + " (" + str(preHeatCurrentVersion) + ")\n"
                            "| DisplayLayerProgress=" + self._displayLayerProgressPluginImplementationState + " (" + str(displayLayerCurrentVersion) + ")\n"
                            "| UltimakerFormat=" + self._ultimakerFormatPluginImplementationState + " (" + str(ultimakerCurrentVersion) + ")\n"
                            "| PrusaSlicerThumbnail=" + self._prusaSlicerThumbnailsPluginImplementationState + " (" + str(prusaSlicerCurrentVersion) + ")\n"
                            )
            
        if (self._preHeatPluginImplementation is None
        or self._displayLayerProgressPluginImplementation is None
        or self._ultimakerFormatPluginImplementation is None
        or self._prusaSlicerThumbnailsPluginImplementation is None):

            #self.plugin._settings.set([SettingsKeys.PLUGIN_DEPENDENCY_CHECK], True)
            #self.plugin._settings.save()
            
            missingMessage = ""

            if self._preHeatPluginImplementation is None:
                missingMessage += (
                    "<li><a target='_newTab' href='https://plugins.octoprint.org/plugins/preheat/'>"
                    f"PreHeat Button ({preHeatRequiredVersion}+)</a> (<b>{self._preHeatPluginImplementationState}</b>)</li>"
                )

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

            if missingMessage != "":
                missingMessage = f"<ul>{missingMessage}</ul>"
                self.plugin._plugin_manager.send_plugin_message(self.plugin._identifier, dict(type="PluginCheck", message=missingMessage))

            
    # get the plugin with status information
    # [0] == status-string
    # [1] == implementaiton of the plugin
    # [2] == version of the plugin, as str like 3.3.0
    # [3] == requiredVersion of the plugin, as str like 1.3.0
    def _getPluginInformation(self, pluginInfo):
        pluginKey = pluginInfo["key"]
        requiredVersion = pluginInfo["minVersion"]

        status = None
        implementation = None
        version = None
        
        if pluginKey in self.plugin._plugin_manager.plugins:
            plugin = self.plugin._plugin_manager.plugins[pluginKey]
            if plugin != None:
                if (plugin.enabled == True):
                    status = "enabled"
                    if (hasattr(plugin, 'incompatible')):
                        if (plugin.incompatible == False):
                            implementation = plugin.implementation
                        else:
                            status = "incompatible"
                    else:
                        implementation = plugin.implementation
                    pass
                else:
                    status = "disabled"
                version = plugin.version
        else:
            status = "missing"

        if (requiredVersion != None and version != None):
            canBeUsed = False
            try:
                comparabelVersion = self._get_comparable_version_semantic(version)
                comparabelRequiredVersion = self._get_comparable_version_semantic(requiredVersion)
                canBeUsed = comparabelVersion >= comparabelRequiredVersion
            except (ValueError) as error:
                logging.exception("Something is wrong with the " +pluginKey+ " version numbers")

            if (canBeUsed == False):
                status = "wrong version"
                implementation = None
        return [status, implementation, version, requiredVersion]
    
    def _get_comparable_version_semantic(self, version_string, force_base=True):
        version = semantic_version.Version.coerce(version_string, partial=False)
        if force_base:
            version_string = "{}.{}.{}".format(version.major, version.minor, version.patch)
            version = semantic_version.Version.coerce(version_string, partial=False)

        return version
        
