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
    
        self.logger.info(f"Handling event: {event} {payload}")

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
        self.logger.info("Print started: %s", payload)
        self.logger.info(f"thumbnail: {self._extract_print_parameters(payload)}")


    def _handle_print_done(self, payload):
        self.logger.info("Print done: %s", payload)
       
    def _handle_print_failed(self, payload):
        self.logger.info("Print failed: %s", payload)
      
    def _handle_metadata_statistics_updated(self, payload):
        self.logger.info("Metadata statistics updated: %s", payload)
        #self._update_metadata(payload)

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
            "thumbnail": self._get_thumbnail(payload.get("path"))  # Extract thumbnail
        }

    def _get_thumbnail(self, file_path):
        """
        Gets the thumbnail path for the given gcode file from the slicer thumbnails plugin
        and encodes it to base64 for storage in the database.
        """
        # Remove the .gcode extension
        base_name = os.path.splitext(file_path)[0]

        """

        # Get the data folder of the slicerthumbnails plugin
        slicer_thumbnails_data_folder = self._get_other_plugin_data_folder("slicerthumbnails")
        
        if not slicer_thumbnails_data_folder:
            self.logger.error("Could not retrieve Slicer Thumbnails data folder.")
            return None


        # Construct the expected thumbnail path
        thumbnail_path = os.path.join(slicer_thumbnails_data_folder, base_name + ".png")
        
        # Check if the thumbnail exists and encode it
        if os.path.exists(thumbnail_path):
            self.logger.info(f"Thumbnail found: {thumbnail_path}")
            try:
                with open(thumbnail_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
            except IOError as e:
                self.logger.error(f"Error reading thumbnail file {thumbnail_path}: {e}")
                return None
        else:
            self.logger.error(f"Thumbnail not found for {file_path} at {thumbnail_path}")
            return None
        """

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
