# coding=utf-8
# eventHandler.py

from octoprint.events import Events

class Event:
    def __init__(self, db, logger):
        self.logger = logger
        self.db = db

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
        else:
            self.logger.info(f"Unsupported event: {event}")

    def _handle_print_started(self, payload):
        self.logger.info("Print started: %s", payload)
        #self.db.execute_query("""
        #    INSERT INTO print_history 
        #    (order_id, printer_id, filament_id, start_datetime, state) 
        #    VALUES (%s, %s, %s, %s, %s)""",
        #    (payload.get("order_id"), payload.get("printer_id"), payload.get("filament_id"), payload["time"], "started"))

    def _handle_print_done(self, payload):
        self.logger.info("Print done: %s", payload)
        #self.db.execute_query("""
        #    UPDATE print_history 
        #    SET end_datetime = %s, duration = %s, state = %s 
        #    WHERE print_id = %s""",
        #    (payload["time"], self._calculate_duration(payload["time"], payload["file"]), "done", self._get_print_id(payload["file"])))

    def _handle_print_failed(self, payload):
        self.logger.info("Print failed: %s", payload)
        #self.db.execute_query("""
        #    UPDATE print_history 
        #    SET end_datetime = %s, state = %s 
        #    WHERE print_id = %s""",
        #    (payload["time"], "failed", self._get_print_id(payload["file"])))

    def _handle_metadata_statistics_updated(self, payload):
        self.logger.info("Metadata statistics updated: %s", payload)
        #self._update_metadata(payload)

    def _update_metadata(self, payload):
        print_id = self._get_print_id(payload["file"])
        #if print_id is not None:
        #    self.db.execute_query("""
        #        UPDATE print_history 
        #        SET estimated_time = %s, calculated_length = %s, total_length = %s, 
        #            calculated_height = %s, total_height = %s, calculated_layers = %s, 
        #            total_layers = %s, calculated_weight = %s, total_weight = %s, 
        #            nozzle_temperature = %s, bed_temperature = %s, bed_type = %s, 
        #            nozzle_diameter = %s
        #        WHERE print_id = %s""",
        #        (payload.get("estimated_time"), payload.get("calculated_length"), payload.get("total_length"),
        #        payload.get("calculated_height"), payload.get("total_height"), payload.get("calculated_layers"),
        #        payload.get("total_layers"), payload.get("calculated_weight"), payload.get("total_weight"),
        #        payload.get("nozzle_temperature"), payload.get("bed_temperature"), payload.get("bed_type"),
        #        payload.get("nozzle_diameter"), print_id))

    def _calculate_duration(self, end_time, file):
        start_time = self._get_start_time(file)
        if start_time:
            return int(end_time) - int(start_time)
        return 0

    def _get_start_time(self, file):
        #cursor = self.db.execute_query("SELECT start_datetime FROM print_history WHERE file = %s ORDER BY start_datetime DESC LIMIT 1", (file,))
        #result = cursor.fetchone()
        #return result[0] if result else None
        return None
    
    def _get_print_id(self, file):
        #cursor = self.db.execute_query("SELECT print_id FROM print_history WHERE file = %s ORDER BY start_datetime DESC LIMIT 1", (file,))
        #result = cursor.fetchone()
        #return result[0] if result else None
        return None
