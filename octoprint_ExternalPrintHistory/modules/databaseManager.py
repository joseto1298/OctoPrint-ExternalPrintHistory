# coding=utf-8
from __future__ import absolute_import

import pymysql
from pymysql import MySQLError

class DatabaseManager():
    def __init__(self, plugin, _logger):
        self._logger = _logger
        self.plugin = plugin
        self.connection_settings = None
        self.connection = None

    def _test_connection(self, config):
        try:
            settings = {
                'host': config.get('db_host'),
                'user': config.get('db_user'),
                'password': config.get('db_password'),
                'database': config.get('db_database'),
                'port': int(config.get('db_port'))
            }
            with pymysql.connect(**settings) as connection:
                #self._logger.info("Database connection test successful.")
                return {"error": False, "message": "Connection successful"}
        except KeyError as e:
            self._logger.error("Missing configuration key: " + str(e))
            raise MySQLError("Error setting connection settings: Missing configuration key") from e
        except MySQLError as e:
            self._logger.error("Error testing DB connection: " + str(e))
            return {"error": True, "message": str(e)}
        except Exception as e:
            self._logger.error("Unexpected error during DB connection test: " + str(e))
            return {"error": True, "message": "An unexpected error occurred: " + str(e)}
        
    def _set_and_test_connection(self, config):
        try:
            self.connection_settings = {
                'host': config.get('db_host'),
                'user': config.get('db_user'),
                'password': config.get('db_password'),
                'database': config.get('db_database'),
                'port': int(config.get('db_port'))
            }
            with pymysql.connect(**self.connection_settings) as connection:
                #self._logger.info("Database connection test successful.")
                return {"error": False, "message": "Connection successful"}
        except KeyError as e:
            self._logger.error("Missing configuration key: " + str(e))
            raise MySQLError("Error setting connection settings: Missing configuration key") from e
        except MySQLError as e:
            self._logger.error("Error testing DB connection: " + str(e))
            return {"error": True, "message": str(e)}
        except Exception as e:
            self._logger.error("Unexpected error during DB connection test: " + str(e))
            return {"error": True, "message": "An unexpected error occurred: " + str(e)}
    
    def get_connection(self):
            if not self.connection_settings:
                self._logger.error("Database configuration is not set.")
                raise MySQLError("Database configuration is not set.")
            
            if self.connection is None or not self.connection.open:
                try:
                    self.connection = pymysql.connect(**self.connection_settings)
                    #self._logger.info("Database connection established.")
                except MySQLError as e:
                    self._logger.error("Error connecting to MySQL database: " + str(e))
                    raise
                except Exception as e:
                    self._logger.error("Unexpected error connecting to MySQL database: " + str(e))
                    raise
            
            return self.connection

    def close_connection(self, result):
        """
        Close the database connection and update the result with any errors.
        """
        if self.connection:
            try:
                self.connection.close()
                #self._logger.info("Database connection closed.")
            except MySQLError as e:
                self._logger.error("Error closing database connection: " + str(e))
                result.update({"error": True, "message": "Error closing database connection: " + str(e)})
            except Exception as e:
                self._logger.error("Unexpected error closing database connection: " + str(e))
                result.update({"error": True, "message": "Unexpected error closing database connection: " + str(e)})
            finally:
                self.connection = None
        else:
            self._logger.warning("Attempted to close a connection that was not open.")
        
        return result

    def _update_insert_printer_config(self, printer_data, printer_id):
        result = {"error": False, "printer_id": printer_id, "insert": False, "update": False}

        try:
            connection = self.get_connection()
            if connection:
                with connection.cursor() as cursor:
                    if printer_id:
                        query = """
                            SELECT printer_id FROM Printer WHERE printer_id = %s
                        """
                        cursor.execute(query, (printer_id,))
                        if cursor.fetchone():
                            update_fields = []
                            params = []

                            for field in ["printer_brand", "printer_model", "printer_name", "printer_power_consumption", 
                                        "printer_purchase_price", "printer_estimated_lifespan", "printer_maintenance_costs"]:
                                if field in printer_data:
                                    db_field = field.replace("printer_", "")
                                    update_fields.append(f"{db_field} = %s")
                                    params.append(printer_data[field])

                            if update_fields:
                                update_query = f"""
                                    UPDATE Printer
                                    SET {', '.join(update_fields)}
                                    WHERE printer_id = %s
                                """
                                params.append(printer_id)
                                cursor.execute(update_query, params)
                                result.update({"update": True})
                        else:
                            result = self._insert_printer(cursor, printer_data)
                    else:
                        result = self._insert_printer(cursor, printer_data)
                    
                    connection.commit()
            else:
                result.update({"message": "The connection to the database is not configured"})
                self._logger.error("The connection to the database is not configured")
                        
        except MySQLError as e:
            connection.rollback()
            result.update({"error": True, "message": str(e)})
            self._logger.error("Error updating/inserting printer configuration: " + str(e))
        except Exception as e:
            connection.rollback()
            result.update({"error": True, "message": "An unexpected error occurred: " + str(e)})
            self._logger.error("Unexpected error updating/inserting printer configuration: " + str(e))
        finally:
            result = self.close_connection(result)
        
        return result

    def _insert_printer(self, cursor, printer_data):
        try:
            fields = []
            values = []
            params = []

            for field in ["printer_brand", "printer_model", "printer_name", "printer_power_consumption", 
                        "printer_purchase_price", "printer_estimated_lifespan", "printer_maintenance_costs"]:
                if field in printer_data:
                    fields.append(field.replace("printer_", ""))
                    values.append("%s")
                    params.append(printer_data[field])

            if fields:
                query = f"""
                    INSERT INTO Printer ({', '.join(fields)})
                    VALUES ({', '.join(values)})
                """
                cursor.execute(query, params)
                cursor.execute("SELECT LAST_INSERT_ID()")
                result = cursor.fetchone()
                printer_id = result[0]
                #self._logger.info(f"Inserted new Printer record with ID {printer_id}")
                return {"error": False, "printer_id": printer_id, "insert": True, "update": False}
            else:
                raise ValueError("No data provided to insert printer record.")
        except MySQLError as e:
            self._logger.error("Error inserting printer record: " + str(e))
            raise
        except Exception as e:
            self._logger.error("Unexpected error inserting printer record: " + str(e))
            raise


    def _select_Printer(self, printer_id):
        result = {"error": True, "message": "Error selecting printer settings"}
        
        try:
            connection = self.get_connection()
            if connection:
                with connection.cursor() as cursor:
                    query = """
                        SELECT printer_id, brand, model, name, power_consumption, purchase_price, estimated_lifespan, maintenance_costs
                        FROM Printer
                        WHERE printer_id = %s
                    """
                    cursor.execute(query, (printer_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        printer_data = {
                            "printer_id": row[0],
                            "brand": row[1],
                            "model": row[2],
                            "name": row[3],
                            "power_consumption": row[4],
                            "purchase_price": row[5],
                            "estimated_lifespan": row[6],
                            "maintenance_costs": row[7],
                        }
                        result = {"error": False, "printer_data": printer_data}
                        #self._logger.info(f"Fetched Printer record with ID {printer_id}: {printer_data}")
                    else:
                        result = {"error": False, "message": "Printer data not found"}
                        #self._logger.info(result["message"])
                    
                connection.commit()
            else:
                result.update({"message": "The connection to the database is not configured"})
                self._logger.error("The connection to the database is not configured")
        except MySQLError as e:
            connection.rollback()
            result.update({"message": str(e)})
            self._logger.error("Error selecting printer configuration: " + str(e))
        except Exception as e:
            connection.rollback()
            result.update({"message": "An unexpected error occurred: " + str(e)})
            self._logger.error("Unexpected error selecting printer configuration: " + str(e))
        finally:
            result = self.close_connection(result)
        
        return result
