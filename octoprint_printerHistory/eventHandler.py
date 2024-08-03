import base64
import os
from octoprint.events import Events
from .printerHistory import Print

class EventHandler :
    def __init__(self, plugin, logger):
        self.logger = logger
        self.plugin = plugin
        self.print = Print(plugin=self, logger=logger)              

    def handle_event(self, event, payload):
    
        #self.logger.info(f"Handling event: {event} {payload}")

        if event == Events.PRINT_STARTED:
            self._handle_print_started(payload)

        elif event == Events.PRINT_DONE:
            self._handle_print_done(payload)

        elif event == Events.PRINT_FAILED:
            self._handle_print_failed(payload)

        elif event == Events.METADATA_STATISTICS_UPDATED:
            self._handle_metadata_statistics_updated(payload)

        # unsupported event
        #else:
            #self.logger.info(f"Unsupported event: {event}")

    def _handle_print_started(self, payload):
        self.logger.info("Print started")
        metadata = self.get_metadata(payload)
        self.logger.info(f"metadata: {metadata}")
        self.logger.info(f"metadata: {payload}")

        thumbnail_path = self._takeThumbnailImage(metadata)

        #thumbnail_path
        #print_id 
        #order_id
        #printer_id


    def _handle_print_done(self, payload):
        self.logger.info("Print done: %s", payload)
       
    def _handle_print_failed(self, payload):
        self.logger.info("Print failed: %s", payload)
      
    def _handle_metadata_statistics_updated(self, payload):
        self.logger.info("Metadata statistics updated: %s", payload)
        #self._update_metadata(payload)


    def get_metadata(self, payload):
        return self.plugin._file_manager.get_metadata(payload["origin"], payload["path"])

    def _extract_print_parameters(self, payload):
        """
        Extracts parameters of the print from the event payload.
        """
        return {
            "file_name": payload.get("name", "N/A"),
            "file_path": payload.get("path", "N/A"),
            "start_time": payload.get("time", "N/A"),  # Unix timestamp
            "material_used": payload.get("material", "N/A"),  # Requires further processing
            "print_time": payload.get("printTime", "N/A"),  # Total print time
            "printer_state": payload.get("state", "N/A"),
            #"thumbnail": self._takeThumbnailImage(payload.get("path"))  # Extract thumbnail
        }
    
    def _takeThumbnailImage(self, metadata):        
        if ("thumbnail" in metadata):
            thumbnail_path = metadata.get("thumbnail")
            if '?' in thumbnail_path:
                    thumbnail_path = thumbnail_path.split('?')[0]
                    return thumbnail_path
        else:
            self.logger.error("Thumbnail not found in print metadata")
        

    def _get_other_plugin_data_folder(self, plugin_identifier):
        """
        Retrieves the data folder path for another plugin by its identifier.
        """
        plugin_instance = self.plugin._plugin_manager.get_plugin(plugin_identifier)
        if plugin_instance:
            return plugin_instance.get_plugin_data_folder()
        else:
            self.logger.error(f"Plugin '{plugin_identifier}' not found.")
            return None
