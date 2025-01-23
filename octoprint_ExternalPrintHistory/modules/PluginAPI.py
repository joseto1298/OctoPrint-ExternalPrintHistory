# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import flask
import http

from flask import request
from ..common.SettingsKeys import SettingsKeys

class PluginAPI():
    
    def is_blueprint_csrf_protected(self):
        return True
        
    @octoprint.plugin.BlueprintPlugin.route("/getAllSpools", methods=["GET"])
    def handle_get_spools_available(self):
        result = self.getSpoolmanConnector().handleGetSpoolsAvailable()

        if result.get('error', False):
            response = flask.jsonify(result)
            response.status = http.HTTPStatus.BAD_REQUEST

            return response
        
        self._logger.info(f"Spools available: {result}")
        
        return flask.jsonify(result)

    @octoprint.plugin.BlueprintPlugin.route("/updateSpool", methods=["POST"])
    def handle_update_active_spool(self):
        jsonData = flask.request.json

        toolId = self.get_int_from_JSON_or_none("toolIdx", jsonData)
        spoolId = self.get_string_from_JSON_or_none("spoolId", jsonData)

        spools = self._settings.get([SettingsKeys.SELECTED_SPOOL_IDS])

        spools[toolId] = {
            'spoolId': spoolId,
        }

        self._settings.set([SettingsKeys.SELECTED_SPOOL_IDS], spools)
        self._settings.save()
                
        self.infoSpool(spoolId,toolId)

        jobFilamentUsage = self.get_current_job_filament_usage()
            
        if jobFilamentUsage['jobHasFilamentLengthData']:
            filamentLength = jobFilamentUsage["jobFilamentLengthsPerTool"][toolId]
            weight = self.get_weight(toolId, filamentLength)
            cost = self.getCost(toolId, weight)
            
            filament = self.spool.get(toolId, {}).get('filament', {})
            
            name = filament.get('name', None)
            material = filament.get('material', None)
            colorHex = filament.get('color_hex', None)
        
            spoolInfo = {
                    'toolIdx': str(toolId),
                    'spoolId': spoolId,
                    'estimatedExtrusionLength': filamentLength,
                    'estimatedWeight': weight,
                    'estimatedCost': cost,
                    'name': name,
                    'material': material,
                    'colorHex': colorHex
                }
        
        self.estimated_spool_changed(spoolInfo)
        
        return flask.jsonify({
            "data": {}
        })

    @octoprint.plugin.BlueprintPlugin.route("/currentJobRequirements", methods=["GET"])
    def handle_get_current_job_requirements(self):

        getSpoolsAvailableResult = self.getSpoolmanConnector().handleGetSpoolsAvailable()

        if getSpoolsAvailableResult.get('error', False):
            response = flask.jsonify(getSpoolsAvailableResult)
            response.status = http.HTTPStatus.BAD_REQUEST

            return response

        spoolsAvailable = getSpoolsAvailableResult["data"]["spools"]

        jobFilamentUsage = self

        if not jobFilamentUsage["jobHasFilamentLengthData"]:
            return flask.jsonify({
                "data": {
                    "isFilamentUsageAvailable": False,
                    "tools": {},
                },
            })

        selectedSpools = self._settings.get([SettingsKeys.SELECTED_SPOOL_IDS])

        filamentUsageDataPerTool = self.get_filament_usage_data_per_tool(
            filamentLengthPerTool = jobFilamentUsage['jobFilamentLengthsPerTool'],
            selectedSpoolsPerTool = selectedSpools,
            spoolsAvailable = spoolsAvailable,
        )

        return flask.jsonify({
            "data": {
                "isFilamentUsageAvailable": True,
                "tools": filamentUsageDataPerTool,
            },
        })
        
    @octoprint.plugin.BlueprintPlugin.route("/testdbconnection", methods=["PUT"])
    def test_db_connection(self):
        """
        Tests the database connection with the provided configuration.

        This route handles a PUT request to test the database connection
        using the configuration provided in the request body.

        Returns:
            flask.Response: A JSON response containing the result of the connection test.
        """
        
        self._logger.info("Testing database connection: " + str(request.json))
        # Attempt to test the database connection with the provided configuration
        response = self.set_and_test_connection(request.json)

        # Return the result of the connection test as a JSON response
        return flask.jsonify(response)

    @octoprint.plugin.BlueprintPlugin.route("/selectPrinter", methods=["GET"])
    def select_printer_config(self):
        """
        Endpoint to select the printer configuration.

        This route handles a PUT request to select the printer configuration
        based on the current printer ID stored in the settings.

        Returns:
            flask.Response: A JSON response containing the printer data or an error message.
        """
        # Fetch the printer configuration from the database using the current printer ID
        response = self.select_printer(self.get_printer_id())
                
        # Return the response as a JSON object
        return flask.jsonify(response)

    @octoprint.plugin.BlueprintPlugin.route("/deactivatePluginCheck", methods=["PUT"])
    def deactivate_plugin_check(self):
        """
        Deactivates the plugin dependency check.

        This function updates the plugin settings to deactivate the plugin
        dependency check and saves the updated settings.

        Returns:
            flask.Response: A JSON response indicating that the plugin check was deactivated.
        """
        # Prepare the response indicating the plugin check was deactivated
        response = {"error": False, "message": "Plugin check deactivated"}

        # Update the settings to deactivate the plugin dependency check
        self._settings.set([SettingsKeys.PLUGIN_DEPENDENCY_CHECK], False)

        # Save the updated settings
        self._settings.save()

        # Return the JSON response
        return flask.jsonify(response)

    @octoprint.plugin.BlueprintPlugin.route("/getTools", methods=["GET"])
    def get_tools(self):
        try:
            selected_spools = self._settings.get([SettingsKeys.SELECTED_SPOOL_IDS]) or {}
            current_temperatures = self._printer.get_current_temperatures()

            tools_info = []
            for temperature_key, temperature_value in current_temperatures.items():
                if 'tool' in temperature_key:
                    tool_id = temperature_key.replace('tool', '')
                    spool_id = selected_spools.get(tool_id, -1)

                    spool_info_result = self.getSpoolmanConnector().handleCommitSpoolInfo(spool_id)

                    tool_data = {"tool": tool_id}

                    if not spool_info_result.get('error', False):
                        tool_data.update({
                            "spoolId": spool_info_result.get("id"),
                            "material": spool_info_result.get("material"),
                            "displayName": spool_info_result.get("filament", {}).get("name"),
                            "vendor": spool_info_result.get("vendor", {}).get("name"),
                            "remainingWeight": spool_info_result.get("remaining_weight"),
                            "color": spool_info_result.get("color_hex", "white"),
                        })
                    
                    elif spool_info_result.get('error', {}).get("code") != "spoolman_api__spool_not_found":
                        self._logger.error(f"Error in Spoolman: {spool_info_result}")
                        return flask.jsonify(spool_info_result), 400
                    
                    elif spool_info_result.get('error', {}).get("code") == "spoolman_api__spool_not_found" and spool_id != -1:
                        tool_data.update({
                            "notFound": True
                        })
                    
                    tools_info.append(tool_data)

            return flask.jsonify(tools_info), 200
        
        except Exception as e:
            self._logger.error(f"Error in get_tools: {str(e)}", exc_info=True)
            return flask.jsonify({"error": "An internal error occurred", "details": str(e)}), 500

    @octoprint.plugin.BlueprintPlugin.route("/getUrlSpoolman", methods=["GET"])
    def get_url_spoolman(self):
        try:
            spoolman_url = self._settings.get([SettingsKeys.SPOOLMAN_URL])
            if spoolman_url is None:
                self._logger.error("Spoolman URL setting is missing.")
                return flask.jsonify({"error": "Spoolman URL setting is missing."}), 400

            if not isinstance(spoolman_url, str):
                self._logger.error("Spoolman URL setting is not a string.")
                return flask.jsonify({"error": "Spoolman URL setting is not a string."}), 400

            return flask.jsonify(spoolman_url), 200
        except Exception as e:
            self._logger.error(f"Error retrieving Spoolman URL: {str(e)}", exc_info=True)
            return flask.jsonify({"error": "An internal error occurred", "details": str(e)}), 500
