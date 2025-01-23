# coding=utf-8
from __future__ import absolute_import
import math
import os

from pathlib import Path

from ..common.SettingsKeys import SettingsKeys
from ..common.PluginsKeys import PluginsKeys

class PrinterUtil():
    def get_file_data(self, payload):
        """
        Retrieves the metadata for a given file from the OctoPrint file manager.

        Args:
            payload (dict): The payload of the event. Must contain the "origin" and "path" keys.

        Returns:
            dict: The metadata for the file.
        """
        return self._file_manager.get_metadata(payload["origin"], payload["path"])

    def take_thumbnail_image(self, payload):
        """
        Retrieves the thumbnail from the PrusaSlicerThumbnail plugin
        and converts it to a binary blob.

        Args:
            payload (dict): The payload of the event.

        Returns:
            bytes: The thumbnail image as a binary blob.
        """
        plugin_folder = Path(self._settings.global_get_basefolder('data')) / PluginsKeys.PLUGIN_PRUSA_SLICER_THUMNAIL['key']
        
        image_path = self.get_file_data(payload).get("thumbnail", "")
        
        file_name = image_path.split('/')[-1].split('?')[0]
        
        cleaned_path = Path(os.path.join(plugin_folder, file_name))
        
        if not os.path.exists(cleaned_path):
            self._logger.error(f"Image not found at the path: {cleaned_path}")
            return None
        
        try:
            with open(cleaned_path, 'rb') as file:
                img_blob = file.read()
            return img_blob
        except Exception as e:
            self._logger.error(f"Error converting image to blob: {str(e)}")
            return None
        
    def file_name(self, payload):
        """
        Retrieves the name of the file without the .gcode extension.

        Args:
            payload (dict): The payload of the event.

        Returns:
            str: The name of the file without the .gcode extension.
        """
        file_name = payload.get("name", "")
        return file_name.replace('.gcode', '') if file_name else ''
    
    def get_nozzle_temperatures(self, tool):
        """
        Retrieves the current nozzle temperatures for a given tool.

        Args:
            tool (str): The tool for which to retrieve the nozzle temperatures.

        Returns:
            int: The current nozzle temperature in degrees Celsius.

        Raises:
            Exception: If an error occurs while retrieving the temperatures.
        """
        try:
            temperatures = self._printer.get_current_temperatures()
            
            # Check if the tool exists in the temperatures dictionary
            if tool in temperatures:
                # Get the target temperature for the tool
                tool_temperature = temperatures[tool].get("target", 0)
            else:
                # If the tool does not exist, set the temperature to 0
                tool_temperature = 0 

            # Return the nozzle temperature
            return tool_temperature

        except Exception as e:
            # Log an error if an exception occurs
            self._logger.error(f"Error getting temperatures for {tool}: {e}")
            # Return 0 if an error occurs
            return 0

    def _time_estimated(self, payload):
        """
        Retrieves the estimated time for a print job from the payload.

        Args:
            payload (dict): The payload of the event.

        Returns:
            int: The estimated time in seconds.1
        """
        exit_time = 0  # Default to 0 if no estimated time is found

        data_file = self.get_file_data(payload)  # Get the file data
        analysis = data_file.get("analysis", {})  # Get the analysis data

        if not analysis.get("analysisPending", True):  # Check if analysis is done
            exit_time = analysis.get("estimatedPrintTime", 0)  # Get the estimated time

        return exit_time
    
    def get_print_status(self):
        """
        Retrieves the current printer state.

        Returns:
            tuple: A tuple containing the text status and flags of the printer.
        """
        # Retrieve the current printer data
        printer_data = self._printer.get_current_data()
        
        # Extract the text status and flags from the printer data
        text_state = printer_data.get("state", {}).get("text", None)
        flags = printer_data.get("state", {}).get("flags", {})
        
        # Return the text status and flags
        return text_state, flags

    def calculate_electricity_cost(self, print_time_hours):
        # Retrieve the electricity cost per kilowatt-hour from the settings
        electricity_cost_per_kwh = self._settings.get([SettingsKeys.ELECTRICITY_COST])

        # If the electricity cost is not set, return 0
        if electricity_cost_per_kwh is None:
            return 0

        # Retrieve the power consumption of the printer in kilowatts
        power_consumption_kw = self.select_printer(self.get_printer_id())
        power_consumption_kw = power_consumption_kw.get("printer_data", {}).get('power_consumption', 0)
        # If the power consumption is not set, return 0
        if power_consumption_kw == 0:
            return 0

        # Calculate and return the total electricity cost
        return float(power_consumption_kw) * float(electricity_cost_per_kwh) * float(print_time_hours)

    def calculate_printer_cost(self, print_time_hours):

        # Get the maintenance cost per hour from the database
        maintenance_cost_per_hour = self.select_printer(self.get_printer_id())
        maintenance_cost_per_hour = maintenance_cost_per_hour.get("printer_data", {}).get("maintenance_costs", 0)

        # If the maintenance cost is 0, return 0
        if maintenance_cost_per_hour == 0:
            return 0

        # Calculate the cost of the printer based on the print time
        return float(maintenance_cost_per_hour) * float(print_time_hours)

    def seconds_to_hours(self, seconds):
        return seconds / 3600

    def get_current_job_filament_usage(self):
        printer = self._printer
        fileManager = self._file_manager

        result = {
            "jobFilamentLengthsPerTool": [],
            "jobHasFilamentLengthData": False,
        }

        if ("job" not in printer.get_current_data()):
            return result

        jobData = printer.get_current_data()["job"]

        if ("file" not in jobData):
            return result

        fileData = jobData["file"]
        origin = fileData["origin"]
        path = fileData["path"]

        if (origin == None or path == None):
            return result

        metadata = fileManager.get_metadata(origin, path)

        if ("analysis" not in metadata or "filament" not in metadata["analysis"]):
            return result

        # Unused tools (eg. with 3 tools, only 1 & 3 are used) are still present on the list
        for toolName, toolData in metadata["analysis"]["filament"].items():
            toolIndex = int(toolName[4:])

            result["jobFilamentLengthsPerTool"] += [0.0] * (toolIndex + 1 - len(result["jobFilamentLengthsPerTool"]))
            result["jobFilamentLengthsPerTool"][toolIndex] = toolData["length"]

            result["jobHasFilamentLengthData"] = True

        return result

    @staticmethod
    def get_filament_usage_data_per_tool(filamentLengthPerTool, selectedSpoolsPerTool, spoolsAvailable):
        usageDataPerTool = {}

        for toolIdx, toolExtrusionLength in enumerate(filamentLengthPerTool):
            toolIdxStr = str(toolIdx)

            # In cases where tool has no spool selection (eg. new tool or print job tools mismatch)
            # default to "spoolId = None"
            toolSelectedSpoolData = selectedSpoolsPerTool.get(toolIdxStr, {})
            toolSpoolId = toolSelectedSpoolData.get("spoolId", None)

            toolSpool = None

            if toolSpoolId != None:
                toolSpool = next(
                    (spool for spool in spoolsAvailable if str(spool["id"]) == toolSpoolId),
                    None
                )

            if not toolSpool:
                usageDataPerTool[toolIdxStr] = {
                    "spoolId": None,
                    "filamentLength": toolExtrusionLength,
                    "filamentWeight": None,
                }

                continue

            filamentDensity = toolSpool["filament"]["density"]
            filamentDiameter = toolSpool["filament"]["diameter"]

            toolExtrusionWeight = PrinterUtil.get_filament_weight(
                length = toolExtrusionLength,
                density = filamentDensity,
                diameter = filamentDiameter,
            )

            usageDataPerTool[toolIdxStr] = {
                "spoolId": toolSpool["id"],
                "filamentLength": toolExtrusionLength,
                "filamentWeight": toolExtrusionWeight,
            }

        return usageDataPerTool

    @staticmethod
    def get_filament_weight(length, density, diameter):
        radius = diameter / 2.0;
        volume = length * math.pi * (radius * radius) / 1000
        weight = volume * density

        return weight