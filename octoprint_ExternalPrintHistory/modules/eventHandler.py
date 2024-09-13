# coding=utf-8
from __future__ import absolute_import

import base64
import os
from octoprint.events import Events

class EventHandler():
    def __init__(self,plugin,_logger):
        self._logger = _logger
        self.plugin = plugin
        
    def _handle_print_started(self, payload):
        self._logger.info("Print started")
        metadata = self.get_metadata(payload)

        self._logger.info(f"metadata: {metadata}")
        self._logger.info(f"payload: {payload}")

        thumbnail_path = self._takeThumbnailImage(metadata.get("thumbnail",""))

        self._logger.info(f"thumbnail_path: {thumbnail_path}")

        #print_id 
        #printer_id
        #start_datetime	
        #end_datetime
        #duration
        #estimated_time
        #thumbnail
        #calculated_length
        #total_length
        #calculated_height
        #total_height
        #calculated_layers
        #total_layers
        #calculated_weight
        #total_weight
        #nozzle_temperature
        #bed_temperature
        #print_time
        #printer_state
        #file_path

    def _handle_print_done(self, payload):
        self._logger.info("Print done: %s", payload)
       
    def _handle_print_failed(self, payload):
        self._logger.info("Print failed: %s", payload)
      
    def _handle_metadata_statistics_updated(self, payload):
        self._logger.info("Metadata statistics updated: %s", payload)
        #self._update_metadata(payload)

    def get_metadata(self, payload):
        return self._file_manager.get_metadata(payload["origin"], payload["path"])

    def _extract_print_parameters(self, payload):
        
        return {
            "file_name": payload.get("name", "N/A"),
            "file_path": payload.get("path", "N/A"),
            "start_time": payload.get("time", "N/A"),  # Unix timestamp
            "material_used": payload.get("material", "N/A"),  # Requires further processing
            "print_time": payload.get("printTime", "N/A"),  # Total print time
            "printer_state": payload.get("state", "N/A"),
            #"thumbnail": self._takeThumbnailImage(payload.get("path"))  # Extract thumbnail
        }
    
    def _takeThumbnailImage(self, path):        
            thumbnail_path = path.split('?')[0]
            return thumbnail_path
    

    def _get_other_plugin_data_folder(self, plugin_identifier):
        """
        Retrieves the data folder path for another plugin by its identifier.
        """
        plugin_instance = self._plugin_manager.get_plugin(plugin_identifier)
        if plugin_instance:
            return plugin_instance.get_plugin_data_folder()
        else:
            self._logger.error(f"Plugin '{plugin_identifier}' not found.")
            return None

    def _handle_metadata_statistics_updated(self, payload):
        file_info = payload.get("file", {})
        statistics = payload.get("statistics", {})

        filament_length = statistics.get("filament_length", "Unknown")
        print_time = statistics.get("print_time", "Unknown")

        self._logger.info(f"File: {file_info.get('name', 'Unknown')}")
        self._logger.info(f"Filament Length: {filament_length} mm")
        self._logger.info(f"Print Time: {print_time} minutes")
        
    def _handle_metadata_analysis_finished(self, payload):
        name = payload.get("path")
        estimatedPrintTime = payload.get("estimatedPrintTime")
        filament = payload.get("filament")
        
