# coding=utf-8
from __future__ import absolute_import

import copy
from datetime import datetime
from ..common.SettingsKeys import SettingsKeys
from ..thirdparty.gcodeInterpreter import gcode

class EventPrinter():

    def initialize_print(self):
        # Initialize dictionaries to store the print data and the spool info
        self.estimated_cost_used_printer = {}  # Dictionary to store the estimated cost of the printer
        self.estimated_spool_info = {}  # Dictionary to store the estimated spool info
        self.spool = {}  # Dictionary to store the spool info
        self.print = {}  # Dictionary to store the print data
        self.tool_select = "0"  # String to store the currently selected tool
        
        self.lastPrintOdometer = None
        self.lastPrintOdometerLoad = None
        
    def handle_printer_state_changed(self, payload):
        # Retrieve the current printer state from the payload
        self.printer_state = payload.get("state_id", None)
        
    def handle_print_started(self, payload):
        self.print.update({
            'print_id': None,
            'printer_id': self.get_printer_id(),
            'name': self.file_name(payload),
            'start_time': datetime.now(),
            'estimated_time': self._time_estimated(payload),
            'state': 'PRINTING',
            'thumbnail': self.take_thumbnail_image(payload),
            'bed_temperature': None,
            'chamber_temperature': None,
            'layers': None,
            'total_layers': None,
            'height': None,
            'total_height': None,
            'end_time': None
        })

        # Clear previous spool info
        self.spool = {}

        # Attempt to update or insert the print record in the database
        result = self.update_insert_print(self.print)

        # Handle database error
        if result["error"]:
            self.show_popup("error", "Error starting printing", "Database error, Printing paused", False)
            self._printer.pause_print()
        else:
            # Update print_id with the assigned ID from the database
            self.print["print_id"] = result["print_id"]
        
        # Log the print start event
        self._logger.info(f"Print started: {self.print}")

        self.lastPrintCancelled = False
        self.lastPrintOdometer = gcode()
        self.lastPrintOdometerLoad = self.lastPrintOdometer._load(None)

        next(self.lastPrintOdometerLoad)

        self._logger.info("printer started")
        
    def handle_client_opened(self, payload):
        job = self._printer.get_current_job()
        
        # Check if a file is currently being printed
        if job.get('file', {}).get('name', None):
            # Send message to the client to show the estimated cost of printing the file
            self._plugin_manager.send_plugin_message(self._identifier, dict(action="costEstimated", visibility="visible", estimatedCost=self.estimated_cost_used_printer))
        
        # Check if the plugin can run the third-party plugin check
        if self.get_plugin_dependency_check():
            # Run the third-party plugin check
            self.checkAndLoadThirdPartyPluginInfos()
            
    def handle_file_deselected(self, payload):
        
        self.estimated_cost_used_printer.update({
            'currency': self._settings.get([SettingsKeys.CURRENCY]) or "€",
            'filamentCost': 0,
            'electricityCost': 0,
            'printerCost': 0,
        })       
        
        self._plugin_manager.send_plugin_message(self._identifier, dict(action="costEstimated", visibility="hidden", estimatedCost=self.estimated_cost_used_printer))

    def handle_file_selected(self, payload):
        selectedSpoolIds = self._settings.get([SettingsKeys.SELECTED_SPOOL_IDS])
        jobFilamentUsage = self.get_current_job_filament_usage()
        hours_use = self.seconds_to_hours(self._time_estimated(payload))
        electricity_cost = self.calculate_electricity_cost(hours_use)
        printer_cost = self.calculate_printer_cost(hours_use)
        filamentCost = 0.0

        for toolIdx, spoolData in selectedSpoolIds.items():
            selectedSpoolId = spoolData.get('spoolId', None)
            
            if selectedSpoolId:
                self.info_spool(selectedSpoolId, toolIdx)
                
            else:
                self._logger.warning("No spoolId found for extruder %s", toolIdx)
                
        if jobFilamentUsage['jobHasFilamentLengthData']:
            for toolIndex, filamentLength in enumerate(jobFilamentUsage["jobFilamentLengthsPerTool"]):
                
                weight = self.get_weight(str(toolIndex), filamentLength)
                filamentCost += self.get_cost(str(toolIndex), weight)
                
        self.estimated_cost_used_printer.update({
            'electricityCost': electricity_cost,
            'printerCost': printer_cost,
            'filamentCost': filamentCost,
        })
        
        self._plugin_manager.send_plugin_message(
            self._identifier, 
            dict(action="costEstimated", visibility="visible", estimatedCost=self.estimated_cost_used_printer)
        )
    
    def estimated_spool_changed(self, payload):
        
        tool_idx = str(payload.get("toolIdx", None))

        if tool_idx not in self.estimated_spool_info:
            self.estimated_spool_info[tool_idx] = {}
        
        self.estimated_spool_info[tool_idx].update({
            'extrusionLength': payload.get("estimatedExtrusionLength", 0),
            'weight': payload.get("estimatedWeight", 0),
            'cost': payload.get("estimatedCost", 0),
            'name': payload.get("name", "Unnamed"),
            'spool_id': payload.get("spoolId", None),
            'material': payload.get("material", "Unknown"),
            'colorHex': payload.get("colorHex", "#000000"),
        })
        
        # Calculate the estimated filament cost for the changed spool
        filamentCost = sum(data.get('cost', 0) for data in self.estimated_spool_info.values())
        
        # Update the estimated cost used for the printer
        self.estimated_cost_used_printer.update({
            'filamentCost': filamentCost,
        })
        
        # Send a plugin message with the estimated cost details
        self._plugin_manager.send_plugin_message(self._identifier, dict(action="costEstimated", visibility="visible", estimatedCost=self.estimated_cost_used_printer))

    def handle_print_paused(self, payload):
        self.print['state'] = "PAUSED"
        result = self.update_insert_print(self.print)
        if result["error"]:
            # Show an error popup if there was an error updating the print record
            self.show_popup("error", "Error pausing printing", "Database error", False)

        self.commit_spool_usage()
        
    def handle_print_resumed(self, payload):
        # Set the print state to "PRINTING"
        self.print['state'] = "PRINTING"
        
        # Update the print record in the database
        result = self.update_insert_print(self.print)
        
        # Check if there was an error updating the print record
        if result["error"]:
            # Show an error popup and pause the print if an error occurred
            self.show_popup("error", "Error continuing printing", "Database error, Printing paused", False)
            self._printer.pause_print()

    def handle_layer_changed(self, payload):
        try:
            # Check if the current layer is provided in the payload
            if payload.get("currentLayer", "-") != "-":
                # Update the current layer in the print information
                self.print['layers'] = payload.get("currentLayer")
            
            # Check if the total layers are provided in the payload
            if payload.get("totalLayer", "-") != "-":
                # Update the total layers in the print information
                self.print['total_layers'] = payload.get("totalLayer")
        except Exception as e:
            # Log any exceptions that occur during the handling of the layer change
            self._logger.error("Error handling layer changed: %s", e)

    def handle_height_changed(self, payload):
        try:
            # Check if the current height is provided in the payload
            if payload.get("currentHeight", "-") != "-":
                # Update the current height in the print information
                self.print['height'] = payload.get("currentHeight")

            # Check if the total height is provided in the payload
            if payload.get("totalHeight", "-") != "-":
                # Update the total height in the print information
                self.print['total_height'] = payload.get("totalHeight")
        except Exception as e:
            # Log any exceptions that occur during the execution of the method
            self._logger.error("Error handling height changed: %s", e)

    def handle_print_cancelled(self, payload):
        self.print['state'] = payload.get("reason", '').upper()
        self.lastPrintCancelled = True
        self.handle_print_finished(payload)
        
    def handle_print_done(self, payload):
        self.print['state'] = 'DONE'
        self.handle_print_finished(payload)

    def handle_print_failed(self, payload):
        self.print['state'] = payload.get("reason", '').upper()
        self.handle_print_finished(payload)

    def handle_print_finished(self, payload):
        # Set the print end time to the current time
        self.print["end_time"] = datetime.now()

        # Update the print record in the database
        result = self.update_insert_print(self.print)

        # Check if there was an error updating the print record
        if result["error"]:
            # Show an error popup if an error occurred
            self.show_popup("error", "Error starting printing", "Database error, Printing paused", False)

        self.lastPrintOdometer = None
        self.lastPrintOdometerLoad = None
        self.commit_spool_usage()
        
        self.spool = {}
        self.tool_select = "0"
                
    def update_nozzle_temperature(self):
        # Check if the currently selected tool exists in the spool info dictionary
        if self.tool_select not in self.spool:
            # Initialize a dictionary for the tool if it doesn't exist
            self.spool[self.tool_select] = {}

        # Retrieve the current nozzle temperature for the currently selected tool
        temperature = self._printer.get_current_temperatures().get('tool' + self.tool_select, {}).get('target', None)

        # Update the spool info dictionary with the new temperature value
        self.spool[self.tool_select]['temperature'] = temperature

    def update_bed_temperature(self):
        # Retrieve the current bed temperature from the printer
        temperature = self._printer.get_current_temperatures().get('bed', {}).get('target', None)

        # Update the "bed_temperature" key in the print dictionary with the new value
        self.print['bed_temperature'] = temperature

    def update_chamber_temperature(self):
        # Retrieve the current chamber temperature from the printer
        temperature = self._printer.get_current_temperatures().get('chamber', {}).get('target', None)
        
        # Update the "chamber_temperature" key in the print dictionary with the new value
        self.print['chamber_temperature'] = temperature

    def select_tool(self, tool_idx):
        # Check if the tool index is already present in the spool info dictionary
        if tool_idx not in self.spool:
            # If not, create an empty dictionary for it
            self.spool[tool_idx] = {}

        # Store the selected tool index in the `tool_select` variable
        self.tool_select = tool_idx

    def handle_printing_gcode(self, command):
        try:
            peek_stats_helpers = self.lastPrintOdometerLoad.send(command)
        except Exception as e:
            self._logger.debug("Error handling printing gcode: %s", e)
            
    def commit_spool_usage(self):
        peek_stats_helpers = self.lastPrintOdometerLoad.send(False)

        current_extrusion_stats = copy.deepcopy(peek_stats_helpers['get_current_extrusion_stats']())

        peek_stats_helpers['reset_extrusion_stats']()
        
        self.resetExtruder = True

        selectedSpoolIds = self._settings.get([SettingsKeys.SELECTED_SPOOL_IDS])

        for toolIdx, toolExtrusionLength in enumerate(current_extrusion_stats['extrusionAmount']):
            selectedSpool = None

            try:
                selectedSpool = selectedSpoolIds[str(toolIdx)]
            except:
                self._logger.info("Extruder '%s', spool id: none", toolIdx)

            if (
                not selectedSpool or
                selectedSpool.get('spoolId', None) == None
            ):
                continue

            selectedSpoolId = selectedSpool['spoolId']

            weight = self.get_weight(str(toolIdx),toolExtrusionLength)
            cost = self.get_cost(str(toolIdx),weight)
            
            filament = self.spool.get(str(toolIdx), {}).get('filament', {})
            
            name = filament.get('name', None)
            material = filament.get('material', None)
            colorHex = filament.get('color_hex', None)
            
            self._logger.info(
                "Extruder '%s', spool id: %s, usage length: %s, weight: %s, cost: %s name: %s material: %s colorHex: %s",
                toolIdx,
                selectedSpoolId,
                toolExtrusionLength,
                weight,
                cost,
                name,
                material,
                colorHex
            )

            result = self.getSpoolmanConnector().handleCommitSpoolUsage(selectedSpoolId, toolExtrusionLength)

            if result.get('error', None):
                self._logger.error("Commit spool usage error: %s", result['error'])

            tool_idx = str(toolIdx)

            if tool_idx not in self.spool:
                self.spool[tool_idx] = {}

            self.spool[tool_idx]['extrusionLength'] = self.spool[tool_idx].get('extrusionLength', 0) + toolExtrusionLength
            self.spool[tool_idx]['weight'] = self.spool[tool_idx].get('weight', 0) + weight
            self.spool[tool_idx]['cost'] = self.spool[tool_idx].get('cost', 0) + cost
            self.spool[tool_idx]['name'] = name
            self.spool[tool_idx]['spool_id'] = selectedSpoolId
            self.spool[tool_idx]['material'] = material
            self.spool[tool_idx]['colorHex'] = colorHex

            result = self._update_insert_spool(self.spool[tool_idx], self.print["print_id"], tool_idx)
            if result.get('error', None):
                self.show_popup("error", "Error printing", "Database error, Printing paused", False)
                
    def get_weight(self,toolIdx,toolExtrusionLength):
            if toolIdx not in self.spool:
                return 0
            
            spool_data = self.spool[toolIdx]['filament']
            
            density = spool_data.get('density', None)
            diameter = spool_data.get('diameter', None)

            if density is None or diameter is None:
                return 0
            
            weight = self.get_filament_weight(toolExtrusionLength, density, diameter)
            
            return weight
        
    def get_cost(self,toolIdx,weight):
        if toolIdx not in self.spool:
            return 0
        
        spool_data = self.spool[toolIdx]
        
        initial_weight = spool_data.get('initial_weight', 0)
        price = spool_data.get('price', 0)
        
        if initial_weight <= 0 or price <= 0:
            return 0

        cost_use = (weight / initial_weight) * price
        
        return cost_use
    
    def info_spool(self,SpoolId,toolId):
        if  SpoolId is None:
            return
        
        result = self.getSpoolmanConnector().handleCommitSpoolInfo(SpoolId)

        if result.get('error', None):
            self._logger.error("Spool info error: %s" % result['error'])
            return

        self.spool[toolId] = result